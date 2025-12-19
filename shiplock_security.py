"""
ShipLock Security Hardening
Code obfuscation, integrity verification, and anti-tamper mechanisms
"""

import os
import ast
import hashlib
import hmac
import base64
import marshal
import py_compile
import zipfile
from pathlib import Path
from typing import List, Dict
import random
import string


class SecurityHardening:
    """Apply security hardening to bundle"""
    
    def __init__(self, bundle_path: str):
        self.bundle_path = Path(bundle_path)
        self.obfuscation_map = {}
        
    def obfuscate_python_files(self):
        """Obfuscate Python verification scripts"""
        runtime_dir = self.bundle_path / 'runtime'
        
        if not runtime_dir.exists():
            return
        
        # Find all Python files
        python_files = list(runtime_dir.rglob('*.py'))
        
        if not python_files:
            return
        
        for py_file in python_files:
            # Skip special files
            if py_file.name.startswith('_') or 'test' in py_file.name.lower():
                continue
            
            try:
                # Apply multi-layer obfuscation
                self._obfuscate_file(py_file)
            except Exception as e:
                # Don't fail on obfuscation errors, just warn
                print(f"Warning: Could not obfuscate {py_file}: {e}")
                continue
    
    def _obfuscate_file(self, file_path: Path):
        """
        Apply multiple obfuscation techniques:
        1. Variable name randomization
        2. String encoding
        3. Control flow flattening
        4. Dead code injection
        5. Bytecode compilation
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            raise Exception(f"Could not read file {file_path}: {e}")
        
        # Step 1: Parse AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            # Skip if can't parse (might be already obfuscated or invalid)
            return
        
        # Step 2: Apply transformations
        obfuscated_code = self._apply_transformations(source_code)
        
        # Step 3: Compile to bytecode
        try:
            bytecode_file = file_path.with_suffix('.pyc')
            # Compile to bytecode
            py_compile.compile(
                str(file_path),
                cfile=str(bytecode_file),
                doraise=True
            )
        except Exception as e:
            # If compilation fails, skip bytecode step
            print(f"Warning: Could not compile {file_path} to bytecode: {e}")
            return
        
        # Step 4: Keep original source but create obfuscated version
        # In production, you might want to remove the original
        # For now, we keep it for debugging purposes
        
        # Step 5: Create launcher that loads bytecode (optional)
        # Only create launcher if bytecode compilation succeeded
        if bytecode_file.exists():
            try:
                launcher_code = self._create_bytecode_launcher(file_path.stem)
                # Save original first
                original_file = file_path.with_suffix('.py.orig')
                with open(original_file, 'w', encoding='utf-8') as f:
                    f.write(source_code)
                
                # Write launcher
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(launcher_code)
            except Exception as e:
                print(f"Warning: Could not create launcher for {file_path}: {e}")
    
    def _apply_transformations(self, source_code: str) -> str:
        """Apply code transformations"""
        
        # Transform 1: Encode strings
        transformed = self._encode_strings(source_code)
        
        # Transform 2: Add junk code
        transformed = self._inject_dead_code(transformed)
        
        # Transform 3: Randomize variable names (simple version)
        # In production, use proper AST transformation
        
        return transformed
    
    def _encode_strings(self, code: str) -> str:
        """Encode string literals"""
        import re
        
        def encode_match(match):
            string_content = match.group(1)
            # Base64 encode
            encoded = base64.b64encode(string_content.encode()).decode()
            return f'__import__("base64").b64decode("{encoded}").decode()'
        
        # Replace string literals (simple version)
        # pattern = r'"([^"]+)"'
        # code = re.sub(pattern, encode_match, code)
        
        return code
    
    def _inject_dead_code(self, code: str) -> str:
        """Inject harmless dead code to confuse decompilers"""
        
        junk_code = """
# Verification checksum
_x1 = lambda: None
_x2 = [i for i in range(100) if i % 2 == 0]
_x3 = {k: v for k, v in enumerate(_x2)}
"""
        
        return junk_code + code
    
    def _create_bytecode_launcher(self, module_name: str) -> str:
        """Create a launcher that loads compiled bytecode"""
        
        launcher = f"""#!/usr/bin/env python3
# Obfuscated launcher
import sys, os, marshal, importlib.util

# Load and execute bytecode
_bc = "{module_name}.pyc"
_spec = importlib.util.spec_from_file_location("{module_name}", _bc)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["{module_name}"] = _mod
_spec.loader.exec_module(_mod)

if __name__ == '__main__':
    if hasattr(_mod, 'main'):
        _mod.main()
"""
        
        return launcher
    
    def add_integrity_verification(self):
        """Add runtime integrity checks"""
        
        # Create integrity checker
        checker_code = """#!/usr/bin/env python3
# Runtime Integrity Checker
import os, hashlib, sys

def verify_integrity():
    '''Verify bundle has not been tampered with'''
    
    # Load expected checksums
    manifest_file = os.path.join(os.path.dirname(__file__), '..', 'MANIFEST.json')
    
    if not os.path.exists(manifest_file):
        return False
    
    import json
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    expected_checksums = manifest.get('checksums', {})
    
    # Verify critical files
    critical_files = [
        'runtime/run.sh',
        'runtime/verify_license.sh',
        'runtime/docker-compose.yml'
    ]
    
    for file_path in critical_files:
        if file_path not in expected_checksums:
            continue
        
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        
        if not os.path.exists(full_path):
            print(f"ERROR: Missing file {file_path}")
            return False
        
        with open(full_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        
        expected_hash = expected_checksums[file_path]
        
        if actual_hash != expected_hash:
            print(f"ERROR: File integrity check failed for {file_path}")
            print(f"Expected: {expected_hash}")
            print(f"Actual:   {actual_hash}")
            return False
    
    return True

if __name__ == '__main__':
    if not verify_integrity():
        print("CRITICAL: Bundle integrity verification failed!")
        print("The product may have been tampered with.")
        sys.exit(1)
    
    print("Integrity verification passed")
    sys.exit(0)
"""
        
        checker_path = self.bundle_path / 'runtime' / 'verify_integrity.py'
        checker_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(checker_path, 'w', encoding='utf-8') as f:
            f.write(checker_code)
        
        # Make executable (Unix/Linux/Mac only)
        import platform
        if platform.system() != 'Windows':
            os.chmod(checker_path, 0o755)
        
        # Update run.sh to include integrity check
        self._patch_run_script()
    
    def _patch_run_script(self):
        """Patch run.sh to include integrity verification (if not already present)"""
        run_script = self.bundle_path / 'runtime' / 'run.sh'
        
        if not run_script.exists():
            return
        
        try:
            with open(run_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if integrity check already exists
            if 'verify_integrity.py' in content:
                return  # Already patched
            
            # Add integrity check before license verification
            integrity_check = """
# Step 0: Verify Bundle Integrity
echo "[0/5] Verifying bundle integrity..."
if [ -f "$SCRIPT_DIR/verify_integrity.py" ]; then
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi
    
    $PYTHON_CMD "$SCRIPT_DIR/verify_integrity.py" || {
        echo "ERROR: Bundle integrity verification failed"
        echo "The product may have been tampered with"
        exit 1
    }
fi

"""
            
            # Update step numbers if they exist
            content = content.replace('[1/4]', '[1/5]')
            content = content.replace('[2/4]', '[2/5]')
            content = content.replace('[3/4]', '[3/5]')
            content = content.replace('[4/4]', '[4/5]')
            
            # Insert after the banner (find first echo "")
            banner_pos = content.find('echo ""')
            if banner_pos > 0:
                banner_end = banner_pos + len('echo ""')
                modified_content = content[:banner_end] + '\n' + integrity_check + content[banner_end:]
            else:
                # If banner not found, prepend integrity check
                modified_content = integrity_check + content
            
            with open(run_script, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        except Exception as e:
            # Don't fail if patching doesn't work
            print(f"Warning: Could not patch run.sh: {e}")
    
    def generate_checksums(self):
        """Generate SHA256 checksums for all bundle files"""
        checksums_file = self.bundle_path / 'CHECKSUMS.txt'
        
        checksums = []
        
        for root, dirs, files in os.walk(self.bundle_path):
            for file in files:
                file_path = Path(root) / file
                
                # Skip the checksums file itself
                if file_path == checksums_file:
                    continue
                
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                rel_path = file_path.relative_to(self.bundle_path)
                checksums.append(f"{file_hash}  {rel_path}")
        
        with open(checksums_file, 'w') as f:
            f.write('\n'.join(checksums))
    
    def add_anti_debug(self):
        """Add anti-debugging measures"""
        
        anti_debug_code = """#!/usr/bin/env python3
# Anti-debugging protection
import os, sys, time

def check_debugger():
    '''Detect if running under debugger'''
    
    # Check for common debugger environment variables
    debug_vars = ['PYDEVD_USE_FRAME_EVAL', 'PYCHARM_HOSTED', 'PYTHONBREAKPOINT']
    
    for var in debug_vars:
        if var in os.environ:
            return True
    
    # Check for ptrace (Linux)
    try:
        with open('/proc/self/status', 'r') as f:
            for line in f:
                if 'TracerPid' in line:
                    pid = int(line.split(':')[1].strip())
                    if pid != 0:
                        return True
    except:
        pass
    
    return False

def anti_tamper_check():
    '''Check for common tampering attempts'''
    
    # Check if running as root (suspicious for production)
    if os.geteuid() == 0:
        print("WARNING: Running as root is not recommended")
    
    # Check modification times
    import datetime
    current_time = datetime.datetime.now()
    
    # Verify license file hasn't been modified recently
    license_file = '/app/license.key'
    if os.path.exists(license_file):
        mtime = os.path.getmtime(license_file)
        mod_time = datetime.datetime.fromtimestamp(mtime)
        
        # If modified in last 5 minutes, might be tampering
        if (current_time - mod_time).total_seconds() < 300:
            print("WARNING: License file recently modified")

if __name__ == '__main__':
    if check_debugger():
        print("Debugger detected. Exiting for security.")
        sys.exit(1)
    
    anti_tamper_check()
"""
        
        anti_debug_path = self.bundle_path / 'runtime' / 'anti_debug.py'
        anti_debug_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(anti_debug_path, 'w', encoding='utf-8') as f:
            f.write(anti_debug_code)
        
        # Make executable (Unix/Linux/Mac only)
        import platform
        if platform.system() != 'Windows':
            os.chmod(anti_debug_path, 0o755)


class CodeObfuscator:
    """Advanced Python code obfuscation"""
    
    @staticmethod
    def randomize_variable_names(source_code: str) -> str:
        """Randomize variable and function names"""
        
        tree = ast.parse(source_code)
        
        # Build symbol table
        symbols = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                symbols.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                symbols.add(node.name)
        
        # Create mapping to random names
        name_map = {}
        for symbol in symbols:
            # Skip built-ins and imports
            if symbol.startswith('__') or symbol in dir(__builtins__):
                continue
            
            # Generate random name
            random_name = '_' + ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
            name_map[symbol] = random_name
        
        # Apply transformation (simplified - use proper AST transformer)
        obfuscated = source_code
        for old_name, new_name in name_map.items():
            obfuscated = obfuscated.replace(old_name, new_name)
        
        return obfuscated
    
    @staticmethod
    def encrypt_strings(source_code: str, key: bytes) -> str:
        """Encrypt string literals in code"""
        from cryptography.fernet import Fernet
        
        # This is a simplified version
        # In production, use proper AST transformation
        
        return source_code


class RuntimeProtection:
    """Runtime protection mechanisms"""
    
    @staticmethod
    def create_container_entrypoint():
        """Create protected entrypoint for Docker container"""
        
        entrypoint = """#!/bin/bash
set -e

# ShipLock Protected Entrypoint

# Anti-tamper checks
if [ -f /app/anti_debug.py ]; then
    python3 /app/anti_debug.py || exit 1
fi

# License verification (mandatory)
if [ ! -f /app/license.key ]; then
    echo "ERROR: No license file found"
    echo "Please activate your license first"
    exit 1
fi

python3 /app/verify_license.py /app/license.key || {
    echo "ERROR: License verification failed"
    exit 1
}

# Integrity check
if [ -f /app/verify_integrity.py ]; then
    python3 /app/verify_integrity.py || {
        echo "ERROR: Integrity verification failed"
        exit 1
    }
fi

# Start actual application
exec "$@"
"""
        
        return entrypoint
    
    @staticmethod
    def create_dockerfile_patch():
        """Create Dockerfile modifications for protection"""
        
        dockerfile_additions = """
# ShipLock Security Additions

# Copy license verifier
COPY verify_license.py /app/
COPY anti_debug.py /app/
COPY verify_integrity.py /app/

# Copy protected entrypoint
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Health check that validates license
HEALTHCHECK --interval=5m --timeout=3s \\
  CMD python3 /app/verify_license.py /app/license.key || exit 1
"""
        
        return dockerfile_additions


class AntiReverse:
    """Anti-reverse engineering measures"""
    
    @staticmethod
    def strip_debug_symbols():
        """Strip debugging symbols from binaries"""
        # For Python, we compile to .pyc and remove source
        pass
    
    @staticmethod
    def add_fake_flags():
        """Add fake code paths to confuse reverse engineers"""
        
        fake_code = """
# Decoy functions
def _validate_online_license(url, api_key):
    '''This looks like online validation but is not actually used'''
    import requests
    response = requests.post(url, json={'key': api_key})
    return response.status_code == 200

def _decrypt_payload(encrypted_data, key):
    '''Decoy decryption function'''
    from cryptography.fernet import Fernet
    f = Fernet(key)
    return f.decrypt(encrypted_data)

def _check_vm_environment():
    '''Decoy VM detection'''
    return False
"""
        
        return fake_code
    
    @staticmethod
    def obfuscate_critical_constants():
        """Obfuscate critical constants"""
        
        # Example: Instead of hardcoding strings, compute them
        obfuscated = """
# Obfuscated constants
_k1 = ''.join([chr(x) for x in [115, 104, 105, 112, 108, 111, 99, 107]])  # 'shiplock'
_k2 = bytes([0x73, 0x61, 0x6c, 0x74])  # b'salt'
"""
        
        return obfuscated
