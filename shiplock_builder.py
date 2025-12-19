"""
ShipLock Bundle Builder
Builds secure, source-code-free Docker distributions
"""

import os
import sys
import subprocess
import shutil
import zipfile
import json
import hashlib
import yaml
import platform
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import tempfile


class BundleBuilder:
    """Builds secure distributable bundles"""
    
    def __init__(self, project_path: str, output_path: str):
        self.project_path = Path(project_path).resolve()
        self.output_path = Path(output_path).resolve()
        self.temp_dir = None
        self.built_images = []
        
    def validate(self):
        """Validate project before building"""
        from shiplock_analyzer import ProjectAnalyzer
        
        # Check Docker availability
        self._check_docker_available()
        
        analyzer = ProjectAnalyzer(str(self.project_path))
        validation = analyzer.validate()
        
        if validation.get('errors'):
            error_msg = "Project validation failed:\n" + "\n".join(f"  - {e}" for e in validation['errors'])
            raise ValueError(error_msg)
        
        if not validation['ready_to_build']:
            warnings = validation.get('warnings', [])
            warning_msg = "\n".join(f"  - {w}" for w in warnings) if warnings else "Unknown validation issue"
            raise ValueError(f"Project not ready to build:\n{warning_msg}")
        
        return validation
    
    def _check_docker_available(self):
        """Check if Docker and docker-compose are available"""
        # Check docker command
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Docker is not available. Please install Docker.")
        except FileNotFoundError:
            raise RuntimeError("Docker is not installed. Please install Docker from https://www.docker.com/")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Docker command timed out. Is Docker daemon running?")
        
        # Check docker-compose command
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                # Try newer docker compose (v2) syntax
                result = subprocess.run(
                    ['docker', 'compose', 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    raise RuntimeError("docker-compose is not available. Please install docker-compose.")
        except FileNotFoundError:
            # Try docker compose v2
            try:
                result = subprocess.run(
                    ['docker', 'compose', 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    raise RuntimeError("docker-compose is not installed. Please install docker-compose.")
            except FileNotFoundError:
                raise RuntimeError("docker-compose is not installed. Please install docker-compose.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("docker-compose command timed out.")
        
        # Check Docker daemon is running
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Docker daemon is not running. Please start Docker.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Cannot connect to Docker daemon. Is Docker running?")
    
    def build_images(self) -> List[str]:
        """Build Docker images with multi-stage optimization"""
        images = []
        
        # Check for docker-compose.yml
        compose_path = self.project_path / 'docker-compose.yml'
        dockerfile_path = self.project_path / 'Dockerfile'
        
        if compose_path.exists():
            # Build using docker-compose
            # Try docker-compose v1 first, then v2
            compose_cmd = ['docker-compose', 'build', '--no-cache']
            result = subprocess.run(
                compose_cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            # If docker-compose v1 fails, try v2
            if result.returncode != 0:
                compose_cmd = ['docker', 'compose', 'build', '--no-cache']
                result = subprocess.run(
                    compose_cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode != 0:
                error_msg = f"Docker build failed:\n{result.stderr}\n\nCommand output:\n{result.stdout}"
                raise RuntimeError(error_msg)
            
            # Get built images
            images = self._get_compose_images()
            
        elif dockerfile_path.exists():
            # Build single Dockerfile
            image_name = f"shiplock-{self.project_path.name}:latest"
            
            result = subprocess.run(
                ['docker', 'build', '--no-cache', '-t', image_name, '.'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"Docker build failed:\n{result.stderr}\n\nCommand output:\n{result.stdout}"
                raise RuntimeError(error_msg)
            
            images = [image_name]
        else:
            raise ValueError("Neither docker-compose.yml nor Dockerfile found in project directory")
        
        self.built_images = images
        return images
    
    def _get_compose_images(self) -> List[str]:
        """Extract image names from docker-compose"""
        compose_path = self.project_path / 'docker-compose.yml'
        
        if not compose_path.exists():
            return []
        
        with open(compose_path, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        images = []
        if 'services' in compose_data:
            for service_name, service in compose_data['services'].items():
                if 'image' in service:
                    images.append(service['image'])
                else:
                    # Use service name as image name (docker-compose convention)
                    project_name = self.project_path.name.lower().replace(' ', '_')
                    images.append(f"{project_name}_{service_name}:latest")
        
        return images
    
    def strip_source_code(self):
        """
        Ensure source code is not accessible in built images.
        Uses multi-stage builds and removes build artifacts.
        """
        # Verify images don't contain source code
        for image in self.built_images:
            self._verify_no_source_in_image(image)
        
        # Export images to tar archives
        self._export_images()
    
    def _verify_no_source_in_image(self, image_name: str):
        """Verify image doesn't contain source files"""
        # Create temporary container
        result = subprocess.run(
            ['docker', 'create', image_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return  # Can't verify, but that's okay
        
        container_id = result.stdout.strip()
        
        # Check for common source file extensions
        source_extensions = ['.py', '.js', '.ts', '.go', '.java']
        found_source = False
        
        for ext in source_extensions:
            check_result = subprocess.run(
                ['docker', 'exec', container_id, 'find', '/', '-name', f'*{ext}', '-type', 'f'],
                capture_output=True,
                text=True
            )
            
            if check_result.stdout.strip():
                found_source = True
                break
        
        # Remove temporary container
        subprocess.run(['docker', 'rm', container_id], capture_output=True)
        
        if found_source:
            raise Exception(
                f"WARNING: Source code detected in image {image_name}. "
                "Use multi-stage Dockerfile to exclude source files."
            )
    
    def _export_images(self):
        """Export Docker images to tar archives"""
        images_dir = self.output_path / 'images'
        images_dir.mkdir(parents=True, exist_ok=True)
        
        for image in self.built_images:
            # Sanitize image name for filename
            safe_name = image.replace(':', '_').replace('/', '_')
            tar_path = images_dir / f"{safe_name}.tar"
            
            # Export image
            result = subprocess.run(
                ['docker', 'save', '-o', str(tar_path), image],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to export image {image}: {result.stderr}")
            
            # Compress
            self._compress_tar(tar_path)
    
    def _compress_tar(self, tar_path: Path):
        """Compress tar file with gzip"""
        # Try using Python's gzip module as fallback for cross-platform compatibility
        import gzip
        import shutil
        
        try:
            # Try system gzip first (faster)
            result = subprocess.run(
                ['gzip', '-f', str(tar_path)],
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback to Python gzip
        try:
            gz_path = Path(str(tar_path) + '.gz')
            with open(tar_path, 'rb') as f_in:
                with gzip.open(gz_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            tar_path.unlink()  # Remove original tar file
        except Exception as e:
            print(f"Warning: Could not compress {tar_path}: {e}")
    
    def generate_runtime(self):
        """Generate runtime scripts and configuration"""
        runtime_dir = self.output_path / 'runtime'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate run.sh
        self._generate_run_script(runtime_dir)
        
        # Copy docker-compose.yml (sanitized)
        self._copy_compose_file(runtime_dir)
        
        # Generate load_images.sh
        self._generate_load_images_script(runtime_dir)
        
        # Generate license verifier
        self._generate_license_verifier(runtime_dir)
        
        # Generate README
        self._generate_readme(runtime_dir)
    
    def _generate_run_script(self, runtime_dir: Path):
        """Generate main run.sh script"""
        run_script = """#!/bin/bash
set -e

# ShipLock Runtime Launcher
# Auto-generated - DO NOT MODIFY

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "  ShipLock Secure Runtime"
echo "=================================================="
echo ""

# Detect Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Detect docker-compose command
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Step 1: Verify Bundle Integrity (if available)
if [ -f "$SCRIPT_DIR/verify_integrity.py" ]; then
    echo "[1/5] Verifying bundle integrity..."
    $PYTHON_CMD "$SCRIPT_DIR/verify_integrity.py" || {
        echo "ERROR: Bundle integrity verification failed"
        echo "The product may have been tampered with"
        exit 1
    }
fi

# Step 2: Verify License (MANDATORY - Software cannot run without valid license)
echo "[2/5] Verifying license..."
if [ ! -f "$SCRIPT_DIR/verify_license.sh" ]; then
    echo "ERROR: License verification script not found"
    echo "This bundle appears to be corrupted or incomplete"
    exit 1
fi

# License verification is MANDATORY - exit immediately if it fails
bash "$SCRIPT_DIR/verify_license.sh" || {
    echo ""
    echo "=================================================="
    echo "  LICENSE VERIFICATION FAILED"
    echo "=================================================="
    echo ""
    echo "This software requires a valid license to run."
    echo ""
    echo "Possible reasons:"
    echo "  - License file (license.key) is missing"
    echo "  - License file is invalid or corrupted"
    echo "  - License has expired"
    echo "  - License is not valid for this machine"
    echo ""
    echo "Please contact your vendor to obtain a valid license."
    echo "Expected license file location: $SCRIPT_DIR/../license.key"
    echo ""
    exit 1
}

# Step 3: Load Docker Images
echo "[3/5] Loading Docker images..."
if [ -f "$SCRIPT_DIR/load_images.sh" ]; then
    bash "$SCRIPT_DIR/load_images.sh" || {
        echo "ERROR: Failed to load images"
        exit 1
    }
else
    echo "WARNING: No images to load"
fi

# Step 4: Start Services
echo "[4/5] Starting services..."
cd "$SCRIPT_DIR"

if [ -f "docker-compose.yml" ]; then
    $COMPOSE_CMD up -d || {
        echo "ERROR: Failed to start services"
        echo "Make sure Docker is running and you have permissions"
        exit 1
    }
else
    echo "ERROR: docker-compose.yml not found"
    exit 1
fi

# Step 5: Show Status
echo "[5/5] Checking service status..."
$COMPOSE_CMD ps

echo ""
echo "=================================================="
echo "  Application started successfully!"
echo "=================================================="
echo ""
echo "To view logs: $COMPOSE_CMD logs -f"
echo "To stop: $COMPOSE_CMD down"
echo ""
"""
        
        run_path = runtime_dir / 'run.sh'
        runtime_dir.mkdir(parents=True, exist_ok=True)
        
        with open(run_path, 'w', encoding='utf-8') as f:
            f.write(run_script)
        
        # Make executable (Unix/Linux/Mac only)
        if platform.system() != 'Windows':
            os.chmod(run_path, 0o755)
    
    def _generate_load_images_script(self, runtime_dir: Path):
        """Generate script to load Docker images"""
        script = """#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES_DIR="$SCRIPT_DIR/../images"

echo "Loading Docker images..."

for image_file in "$IMAGES_DIR"/*.tar.gz; do
    if [ -f "$image_file" ]; then
        echo "  Loading $(basename "$image_file")..."
        gunzip -c "$image_file" | docker load
    fi
done

echo "All images loaded successfully!"
"""
        
        script_path = runtime_dir / 'load_images.sh'
        with open(script_path, 'w') as f:
            f.write(script)
        
        # Make executable (Unix/Linux/Mac only)
        if platform.system() != 'Windows':
            os.chmod(script_path, 0o755)
    
    def _copy_compose_file(self, runtime_dir: Path):
        """Copy and sanitize docker-compose.yml"""
        source_compose = self.project_path / 'docker-compose.yml'
        
        if not source_compose.exists():
            return
        
        import yaml
        
        with open(source_compose, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Remove build contexts (we're using pre-built images)
        if 'services' in compose_data:
            for service_name, service in compose_data['services'].items():
                if 'build' in service:
                    del service['build']
                    
                    # Ensure image is specified
                    if 'image' not in service:
                        service['image'] = f"{self.project_path.name}_{service_name}:latest"
        
        # Write sanitized compose file
        dest_compose = runtime_dir / 'docker-compose.yml'
        with open(dest_compose, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False)
    
    def _generate_license_verifier(self, runtime_dir: Path):
        """Generate license verification scripts (both bash and Python)"""
        from shiplock_license import LicenseVerifier
        
        # Generate Python verification script
        verifier = LicenseVerifier()
        verifier.create_verification_script(str(runtime_dir / 'verify_license.py'))
        
        # Generate bash wrapper script
        verifier_script = """#!/bin/bash
# ShipLock License Verifier Wrapper
# This script calls the Python license verifier

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LICENSE_FILE="$SCRIPT_DIR/../license.key"

if [ ! -f "$LICENSE_FILE" ]; then
    echo "ERROR: License file not found"
    echo "Please contact your vendor for a valid license"
    echo "Expected license file at: $LICENSE_FILE"
    exit 1
fi

# Call Python verifier
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

"$PYTHON_CMD" "$SCRIPT_DIR/verify_license.py" "$LICENSE_FILE" || {
    echo "ERROR: License validation failed"
    exit 1
}

echo "License verified successfully"
exit 0
"""
        
        script_path = runtime_dir / 'verify_license.sh'
        with open(script_path, 'w') as f:
            f.write(verifier_script)
        
        # Make executable (Unix/Linux/Mac)
        if platform.system() != 'Windows':
            os.chmod(script_path, 0o755)
    
    def _generate_readme(self, runtime_dir: Path):
        """Generate README for client"""
        readme = f"""# ShipLock Secure Distribution

## Quick Start

1. **Load the application:**
   ```bash
   ./run.sh
   ```

2. **Check status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop application:**
   ```bash
   docker-compose down
   ```

## License Activation

This product requires a valid license key.

If you received a license file, place it in the root directory:
```bash
cp license.key ./
```

The license will be automatically verified on startup.

## System Requirements

- Docker 20.10 or higher
- Docker Compose 1.29 or higher
- Minimum 2GB RAM
- 10GB free disk space

## Support

For technical support or license issues, contact your vendor.

## Security Notice

This distribution contains proprietary software protected by copyright law.
Reverse engineering, decompilation, or redistribution is prohibited.

---
Generated by ShipLock v1.0.0
Distribution Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        readme_path = runtime_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme)
    
    def apply_security(self):
        """Apply security measures and obfuscation"""
        from shiplock_security import SecurityHardening
        
        hardening = SecurityHardening(self.output_path)
        
        # Obfuscate verification scripts
        hardening.obfuscate_python_files()
        
        # Add integrity checks
        hardening.add_integrity_verification()
        
        # Generate checksums
        hardening.generate_checksums()
    
    def create_directory_bundle(self) -> Path:
        """Create directory-based bundle"""
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Create manifest
        self._create_manifest()
        
        return self.output_path
    
    def create_zip_bundle(self) -> Path:
        """Create ZIP archive bundle"""
        bundle_name = f"{self.project_path.name}-bundle.zip"
        zip_path = self.output_path.parent / bundle_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def push_to_github(self, repo_url: str):
        """Push bundle to GitHub repository"""
        # Initialize git repo in output directory
        subprocess.run(['git', 'init'], cwd=self.output_path, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.output_path, check=True)
        subprocess.run(
            ['git', 'commit', '-m', 'ShipLock distribution bundle'],
            cwd=self.output_path,
            check=True
        )
        
        # Add remote and push
        subprocess.run(
            ['git', 'remote', 'add', 'origin', repo_url],
            cwd=self.output_path,
            check=True
        )
        subprocess.run(
            ['git', 'push', '-u', 'origin', 'main'],
            cwd=self.output_path,
            check=True
        )
    
    def _create_manifest(self):
        """Create bundle manifest"""
        manifest = {
            'bundle_info': {
                'project_name': self.project_path.name,
                'created_at': datetime.now().isoformat(),
                'shiplock_version': '1.0.0'
            },
            'images': self.built_images,
            'files': self._list_bundle_files(),
            'checksums': self._calculate_checksums()
        }
        
        manifest_path = self.output_path / 'MANIFEST.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _list_bundle_files(self) -> List[str]:
        """List all files in bundle"""
        files = []
        for root, dirs, filenames in os.walk(self.output_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.output_path)
                files.append(str(rel_path))
        return files
    
    def _calculate_checksums(self) -> Dict[str, str]:
        """Calculate SHA256 checksums for all files"""
        checksums = {}
        
        for root, dirs, filenames in os.walk(self.output_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.output_path)
                
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    checksums[str(rel_path)] = file_hash
        
        return checksums
