"""
ShipLock Project Analyzer
Scans and validates Docker-based projects for secure bundling
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import fnmatch


class ProjectAnalyzer:
    """Analyzes Docker projects for bundling"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config()
        self.ignore_patterns = self._load_ignore_patterns()
        
    def _load_config(self) -> Dict:
        """Load ShipLock configuration"""
        config_path = self.project_path / '.shiplock' / 'config.yaml'
        
        if not config_path.exists():
            return self._default_config()
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'project': {
                'name': self.project_path.name,
                'version': '1.0.0'
            },
            'build': {
                'strip_source': True,
                'multi_stage': True,
                'compress': True
            },
            'exclude': [
                '*.py', '*.js', '*.ts', '*.go', '*.java',
                'src/', 'tests/', '.git/', '__pycache__/', 'node_modules/'
            ],
            'include': [
                'docker-compose.yml', 'Dockerfile', '.env.example'
            ]
        }
    
    def _load_ignore_patterns(self) -> Set[str]:
        """Load .bundleignore patterns"""
        ignore_file = self.project_path / '.bundleignore'
        patterns = set()
        
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        
        # Add patterns from config
        patterns.update(self.config.get('exclude', []))
        
        return patterns
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        relative_path = file_path.relative_to(self.project_path)
        path_str = str(relative_path)
        
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        return False
    
    def scan_project(self) -> Dict:
        """Scan project and categorize files"""
        included_files = []
        excluded_files = []
        source_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                if self._should_exclude(file_path):
                    excluded_files.append(file_path)
                    
                    # Track source code files
                    if file_path.suffix in ['.py', '.js', '.ts', '.go', '.java', '.cpp', '.c']:
                        source_files.append(file_path)
                else:
                    included_files.append(file_path)
        
        return {
            'name': self.config['project']['name'],
            'version': self.config['project']['version'],
            'total_files': len(included_files) + len(excluded_files),
            'included_files': len(included_files),
            'excluded_files': len(excluded_files),
            'source_files_excluded': len(source_files),
            'included_list': included_files,
            'excluded_list': excluded_files
        }
    
    def detect_docker(self) -> Dict:
        """Detect Docker configuration"""
        dockerfile_path = self.project_path / 'Dockerfile'
        compose_path = self.project_path / 'docker-compose.yml'
        
        docker_info = {
            'has_dockerfile': dockerfile_path.exists(),
            'has_compose': compose_path.exists(),
            'multi_stage': False,
            'services': 0,
            'exposed_ports': [],
            'volumes': []
        }
        
        # Analyze Dockerfile
        if dockerfile_path.exists():
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
                
                # Detect multi-stage build
                from_count = len(re.findall(r'^FROM\s+', dockerfile_content, re.MULTILINE))
                docker_info['multi_stage'] = from_count > 1
                
                # Extract exposed ports
                ports = re.findall(r'EXPOSE\s+(\d+)', dockerfile_content)
                docker_info['exposed_ports'] = ports
        
        # Analyze docker-compose.yml
        if compose_path.exists():
            with open(compose_path, 'r') as f:
                compose_data = yaml.safe_load(f)
                
                if 'services' in compose_data:
                    docker_info['services'] = len(compose_data['services'])
                    
                    # Extract volumes
                    for service_name, service in compose_data['services'].items():
                        if 'volumes' in service:
                            docker_info['volumes'].extend(service['volumes'])
        
        return docker_info
    
    def analyze_dependencies(self) -> Dict:
        """Analyze project dependencies"""
        deps = {
            'python': [],
            'node': [],
            'system': []
        }
        
        # Python dependencies
        requirements_files = [
            'requirements.txt',
            'requirements-prod.txt',
            'Pipfile',
            'pyproject.toml'
        ]
        
        for req_file in requirements_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                deps['python'].append(req_file)
        
        # Node dependencies
        if (self.project_path / 'package.json').exists():
            deps['node'].append('package.json')
        
        # System dependencies (from Dockerfile)
        dockerfile_path = self.project_path / 'Dockerfile'
        if dockerfile_path.exists():
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                # Extract apt-get/yum/apk packages
                apt_packages = re.findall(r'apt-get install.*?([a-z0-9\-]+)', content)
                deps['system'].extend(apt_packages)
        
        return deps
    
    def validate(self) -> Dict:
        """Validate project for secure bundling"""
        validation = {
            'ready_to_build': True,
            'warnings': [],
            'errors': [],
            'source_protected': True,
            'has_secrets': False
        }
        
        # Check for Dockerfile
        if not (self.project_path / 'Dockerfile').exists():
            validation['errors'].append("Dockerfile not found")
            validation['ready_to_build'] = False
        
        # Check for docker-compose.yml
        if not (self.project_path / 'docker-compose.yml').exists():
            validation['warnings'].append("docker-compose.yml not found - will use Dockerfile only")
        
        # Check for .env with secrets
        env_path = self.project_path / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_content = f.read()
                # Look for potential secrets
                secret_patterns = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY']
                for pattern in secret_patterns:
                    if pattern in env_content.upper():
                        validation['has_secrets'] = True
                        validation['warnings'].append(
                            f"Potential secrets found in .env file. Use .env.example instead."
                        )
                        break
        
        # Check if source code would be included
        scan_result = self.scan_project()
        if scan_result['source_files_excluded'] == 0:
            validation['warnings'].append("No source files detected for exclusion")
        
        # Check for multi-stage Dockerfile
        docker_info = self.detect_docker()
        if not docker_info['multi_stage']:
            validation['warnings'].append(
                "Multi-stage Dockerfile not detected. Consider using multi-stage builds for smaller images."
            )
        
        # Ensure .shiplock config exists
        if not (self.project_path / '.shiplock' / 'config.yaml').exists():
            validation['warnings'].append(
                "ShipLock config not found. Run 'shiplock init' first."
            )
        
        return validation
    
    def get_file_tree(self) -> str:
        """Generate a visual tree of included files"""
        scan_result = self.scan_project()
        tree_lines = []
        
        tree_lines.append(f"📦 {self.config['project']['name']}")
        tree_lines.append(f"├── Included Files: {scan_result['included_files']}")
        tree_lines.append(f"└── Excluded Files: {scan_result['excluded_files']}")
        
        return "\n".join(tree_lines)
    
    def extract_metadata(self) -> Dict:
        """Extract project metadata"""
        metadata = {
            'name': self.config['project']['name'],
            'version': self.config['project']['version'],
            'docker': self.detect_docker(),
            'dependencies': self.analyze_dependencies(),
            'file_stats': self.scan_project()
        }
        
        return metadata
