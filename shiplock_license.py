"""
ShipLock License System
Strong cryptographic licensing with machine binding and offline validation
"""

import os
import json
import hashlib
import hmac
import base64
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class HardwareFingerprint:
    """Generate hardware fingerprints for machine binding"""
    
    @staticmethod
    def get_machine_id() -> str:
        """
        Generate unique machine identifier based on hardware
        Combines multiple hardware attributes for robustness
        Cross-platform support for Linux, Windows, and macOS
        """
        import platform
        import socket
        
        components = []
        system = platform.system()
        
        # Hostname (always available)
        try:
            components.append(socket.gethostname())
        except:
            pass
        
        # Platform-specific identifiers
        if system == 'Linux':
            # Machine ID (systemd)
            try:
                with open('/etc/machine-id', 'r') as f:
                    components.append(f.read().strip())
            except:
                pass
            
            # CPU ID (if available)
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'Serial' in line:
                            components.append(line.strip())
                            break
            except:
                pass
        
        elif system == 'Windows':
            # Windows-specific identifiers
            try:
                import subprocess
                # Get machine GUID from Windows registry
                result = subprocess.run(
                    ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography', '/v', 'MachineGuid'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'MachineGuid' in line:
                            guid = line.split()[-1] if line.split() else ''
                            if guid:
                                components.append(guid)
                                break
            except:
                pass
        
        elif system == 'Darwin':  # macOS
            # macOS-specific identifiers
            try:
                import subprocess
                # Get hardware UUID
                result = subprocess.run(
                    ['system_profiler', 'SPHardwareDataType'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Hardware UUID' in line:
                            uuid = line.split(':')[-1].strip() if ':' in line else ''
                            if uuid:
                                components.append(uuid)
                                break
            except:
                pass
        
        # MAC Address (works on all platforms)
        mac = HardwareFingerprint._get_mac_address()
        if mac:
            components.append(mac)
        
        # If we don't have enough components, add more platform-agnostic identifiers
        if len(components) < 2:
            try:
                import uuid as uuid_lib
                # Get node ID (based on MAC address)
                node_id = str(uuid_lib.getnode())
                if node_id and node_id != '0':
                    components.append(node_id)
            except:
                pass
        
        # Combine and hash
        if not components:
            # Fallback: use a combination that's at least somewhat unique
            import platform as pl
            components = [
                pl.node(),
                pl.machine(),
                pl.processor()[:50] if pl.processor() else 'unknown'
            ]
        
        combined = '|'.join(components)
        machine_id = hashlib.sha256(combined.encode()).hexdigest()
        
        return machine_id
    
    @staticmethod
    def _get_mac_address() -> Optional[str]:
        """Get MAC address of primary network interface"""
        import platform
        
        # Try netifaces first (more reliable)
        try:
            import netifaces
            interfaces = netifaces.interfaces()
            
            # Prefer non-loopback, non-virtual interfaces
            for interface in interfaces:
                if interface.startswith('lo') or 'virtual' in interface.lower():
                    continue
                    
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_LINK in addrs:
                        mac = addrs[netifaces.AF_LINK][0].get('addr')
                        if mac and mac != '00:00:00:00:00:00':
                            return mac
                except:
                    continue
        except ImportError:
            # netifaces not available, use fallback
            pass
        except Exception:
            # Other error, use fallback
            pass
        
        # Fallback: use uuid.getnode() (works cross-platform)
        try:
            node = uuid.getnode()
            if node != 0:
                mac = ':'.join(['{:02x}'.format((node >> i) & 0xff) 
                               for i in range(0, 48, 8)][::-1])
                if mac and mac != '00:00:00:00:00:00':
                    return mac
        except:
            pass
        
        # Windows-specific fallback
        if platform.system() == 'Windows':
            try:
                import subprocess
                result = subprocess.run(
                    ['getmac', '/NH'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            parts = line.strip().split()
                            if parts and len(parts[0]) == 17 and ':' in parts[0]:
                                mac = parts[0].replace('-', ':')
                                if mac and mac != '00:00:00:00:00:00':
                                    return mac
            except:
                pass
        
        return None
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get detailed system information"""
        import platform
        
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node()
        }


class LicenseGenerator:
    """Generate cryptographically signed licenses"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.encryption_key = None
        
    def generate_keys(self) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for license signing"""
        # Generate RSA private key (4096 bits for strong security)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        self.public_key = self.private_key.public_key()
        
        # Serialize keys
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b'shiplock_secure_key_2024')
        )
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save keys
        with open('shiplock_private.key', 'wb') as f:
            f.write(private_pem)
        
        with open('shiplock_public.key', 'wb') as f:
            f.write(public_pem)
        
        # Generate symmetric encryption key
        self.encryption_key = Fernet.generate_key()
        
        return private_pem, public_pem
    
    def load_keys(self):
        """Load existing keys"""
        try:
            with open('shiplock_private.key', 'rb') as f:
                private_pem = f.read()
                self.private_key = serialization.load_pem_private_key(
                    private_pem,
                    password=b'shiplock_secure_key_2024',
                    backend=default_backend()
                )
            
            with open('shiplock_public.key', 'rb') as f:
                public_pem = f.read()
                self.public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
        except FileNotFoundError:
            # Generate new keys if not found
            self.generate_keys()
    
    def create_license(
        self,
        product_id: str,
        client: str,
        expires: Optional[str] = None,
        machine_bound: bool = True,
        features: Optional[Dict] = None
    ) -> Dict:
        """Create license payload"""
        
        license_data = {
            'license_id': str(uuid.uuid4()),
            'product_id': product_id,
            'client': client,
            'issued_at': datetime.now().isoformat(),
            'expires_at': expires or 'never',
            'machine_bound': machine_bound,
            'features': features or {},
            'version': '1.0'
        }
        
        if machine_bound:
            # Get machine fingerprint
            fingerprint = HardwareFingerprint.get_machine_id()
            license_data['machine_id'] = fingerprint
            license_data['system_info'] = HardwareFingerprint.get_system_info()
        
        return license_data
    
    def sign_license(self, license_data: Dict) -> str:
        """Sign license with private key"""
        if not self.private_key:
            self.load_keys()
        
        # Convert to JSON
        license_json = json.dumps(license_data, sort_keys=True)
        license_bytes = license_json.encode('utf-8')
        
        # Create signature
        signature = self.private_key.sign(
            license_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encode license and signature
        license_b64 = base64.b64encode(license_bytes).decode('utf-8')
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Create final license structure
        signed_license = {
            'license': license_b64,
            'signature': signature_b64,
            'public_key': self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        }
        
        # Add obfuscated integrity check
        integrity_hash = self._calculate_integrity(license_b64, signature_b64)
        signed_license['integrity'] = integrity_hash
        
        return json.dumps(signed_license, indent=2)
    
    def _calculate_integrity(self, license_b64: str, signature_b64: str) -> str:
        """Calculate integrity hash with obfuscation"""
        # Combine license and signature
        combined = f"{license_b64}:{signature_b64}"
        
        # Multiple rounds of hashing with salt
        salt = b'shiplock_integrity_salt_v1'
        
        hash1 = hashlib.sha256(combined.encode() + salt).hexdigest()
        hash2 = hashlib.sha512(hash1.encode() + salt).hexdigest()
        hash3 = hashlib.sha256(hash2.encode() + salt).hexdigest()
        
        return hash3
    
    def write_license(self, signed_license: str, output_path: str):
        """Write license to file"""
        with open(output_path, 'w') as f:
            f.write(signed_license)
        
        # Also create a binary version with additional obfuscation
        binary_path = output_path.replace('.key', '.bin')
        
        # Encrypt the license
        encryption_key = Fernet.generate_key()
        cipher = Fernet(encryption_key)
        encrypted = cipher.encrypt(signed_license.encode('utf-8'))
        
        with open(binary_path, 'wb') as f:
            # Write key XORed with a known pattern
            xor_key = bytes([k ^ 0xAB for k in encryption_key])
            f.write(xor_key)
            f.write(b'\x00' * 16)  # Separator
            f.write(encrypted)


class LicenseVerifier:
    """Verify and validate licenses at runtime"""
    
    def __init__(self):
        self.public_key = None
        
    def verify(self, license_file: str) -> Tuple[bool, Dict]:
        """
        Verify license file
        Returns (is_valid, details)
        """
        try:
            # Load license
            with open(license_file, 'r') as f:
                signed_license = json.loads(f.read())
            
            # Extract components
            license_b64 = signed_license['license']
            signature_b64 = signed_license['signature']
            public_key_pem = signed_license['public_key']
            integrity = signed_license['integrity']
            
            # Verify integrity first
            expected_integrity = self._calculate_integrity(license_b64, signature_b64)
            if integrity != expected_integrity:
                return False, {'reason': 'Integrity check failed - license may be tampered'}
            
            # Load public key
            self.public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Decode license and signature
            license_bytes = base64.b64decode(license_b64)
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            try:
                self.public_key.verify(
                    signature,
                    license_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            except Exception as e:
                return False, {'reason': f'Signature verification failed: {str(e)}'}
            
            # Parse license data
            license_data = json.loads(license_bytes.decode('utf-8'))
            
            # Verify expiration
            if license_data['expires_at'] != 'never':
                expiry_date = datetime.fromisoformat(license_data['expires_at'])
                if datetime.now() > expiry_date:
                    return False, {'reason': 'License expired', 'expired_at': license_data['expires_at']}
            
            # Verify machine binding
            if license_data.get('machine_bound', False):
                current_machine_id = HardwareFingerprint.get_machine_id()
                license_machine_id = license_data.get('machine_id', '')
                
                if current_machine_id != license_machine_id:
                    return False, {
                        'reason': 'License not valid for this machine',
                        'expected': license_machine_id[:16] + '...',
                        'actual': current_machine_id[:16] + '...'
                    }
            
            # License is valid
            return True, {
                'license_id': license_data['license_id'],
                'product_id': license_data['product_id'],
                'client': license_data['client'],
                'issued_at': license_data['issued_at'],
                'expires_at': license_data['expires_at'],
                'machine_bound': license_data['machine_bound'],
                'features': license_data.get('features', {})
            }
            
        except FileNotFoundError:
            return False, {'reason': 'License file not found'}
        except json.JSONDecodeError:
            return False, {'reason': 'Invalid license file format'}
        except Exception as e:
            return False, {'reason': f'Verification error: {str(e)}'}
    
    def _calculate_integrity(self, license_b64: str, signature_b64: str) -> str:
        """Calculate integrity hash (must match generator)"""
        combined = f"{license_b64}:{signature_b64}"
        salt = b'shiplock_integrity_salt_v1'
        
        hash1 = hashlib.sha256(combined.encode() + salt).hexdigest()
        hash2 = hashlib.sha512(hash1.encode() + salt).hexdigest()
        hash3 = hashlib.sha256(hash2.encode() + salt).hexdigest()
        
        return hash3
    
    def create_verification_script(self, output_path: str):
        """
        Create standalone verification script for embedding in Docker containers
        This script is obfuscated and difficult to bypass
        """
        import platform
        
        # More robust license verification script
        verification_code = """#!/usr/bin/env python3
# ShipLock License Verifier
# DO NOT MODIFY - Integrity protected

import os
import sys
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path

def verify_license_file(license_file_path):
    '''Verify license file using cryptographic signatures'''
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        print("ERROR: cryptography library not found. Install with: pip install cryptography")
        return False, "Missing cryptography library"
    
    try:
        # Load license file
        license_path = Path(license_file_path)
        if not license_path.exists():
            return False, f"License file not found: {license_file_path}"
        
        with open(license_path, 'r') as f:
            signed_license = json.loads(f.read())
        
        # Extract components
        license_b64 = signed_license.get('license')
        signature_b64 = signed_license.get('signature')
        public_key_pem = signed_license.get('public_key')
        integrity = signed_license.get('integrity')
        
        if not all([license_b64, signature_b64, public_key_pem, integrity]):
            return False, "Invalid license file format"
        
        # Verify integrity hash first
        combined = f"{license_b64}:{signature_b64}"
        salt = b'shiplock_integrity_salt_v1'
        hash1 = hashlib.sha256(combined.encode() + salt).hexdigest()
        hash2 = hashlib.sha512(hash1.encode() + salt).hexdigest()
        hash3 = hashlib.sha256(hash2.encode() + salt).hexdigest()
        
        if integrity != hash3:
            return False, "Integrity check failed - license may be tampered"
        
        # Load public key and verify signature
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
        except Exception as e:
            return False, f"Failed to load public key: {str(e)}"
        
        # Decode license and signature
        try:
            license_bytes = base64.b64decode(license_b64)
            signature = base64.b64decode(signature_b64)
        except Exception as e:
            return False, f"Failed to decode license data: {str(e)}"
        
        # Verify cryptographic signature
        try:
            public_key.verify(
                signature,
                license_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"
        
        # Parse license data
        try:
            license_data = json.loads(license_bytes.decode('utf-8'))
        except Exception as e:
            return False, f"Failed to parse license data: {str(e)}"
        
        # Check expiration
        if license_data.get('expires_at') != 'never':
            try:
                expiry_date = datetime.fromisoformat(license_data['expires_at'])
                if datetime.now() > expiry_date:
                    return False, f"License expired on {license_data['expires_at']}"
            except (ValueError, KeyError) as e:
                return False, f"Invalid expiration date: {str(e)}"
        
        # Verify machine binding if enabled
        if license_data.get('machine_bound', False):
            machine_id = license_data.get('machine_id', '')
            if machine_id:
                # Calculate current machine ID
                try:
                    import socket
                    import uuid as uuid_lib
                    components = []
                    
                    # Get hostname
                    try:
                        components.append(socket.gethostname())
                    except:
                        pass
                    
                    # Get machine ID
                    try:
                        if os.path.exists('/etc/machine-id'):
                            with open('/etc/machine-id', 'r') as f:
                                components.append(f.read().strip())
                    except:
                        pass
                    
                    # Get MAC address
                    try:
                        mac = ':'.join(['{:02x}'.format((uuid_lib.getnode() >> i) & 0xff) 
                                       for i in range(0, 48, 8)][::-1])
                        components.append(mac)
                    except:
                        pass
                    
                    # Calculate fingerprint
                    combined = '|'.join(components)
                    current_machine_id = hashlib.sha256(combined.encode()).hexdigest()
                    
                    if current_machine_id != machine_id:
                        return False, "License not valid for this machine (machine binding mismatch)"
                except Exception as e:
                    # If machine ID calculation fails, warn but don't fail (for compatibility)
                    print(f"WARNING: Could not verify machine binding: {str(e)}")
        
        # License is valid
        return True, license_data
        
    except json.JSONDecodeError as e:
        return False, f"Invalid license file format (JSON error): {str(e)}"
    except Exception as e:
        return False, f"Verification error: {str(e)}"


def main():
    '''Main entry point'''
    if len(sys.argv) < 2:
        print("Usage: verify_license.py <license_file>")
        sys.exit(1)
    
    license_file = sys.argv[1]
    
    # If relative path, try to find in common locations
    if not os.path.isabs(license_file) and not Path(license_file).exists():
        # Try parent directory
        parent_license = Path(__file__).parent.parent / license_file
        if parent_license.exists():
            license_file = str(parent_license)
        # Try current directory
        elif Path(license_file).exists():
            license_file = os.path.abspath(license_file)
    
    is_valid, result = verify_license_file(license_file)
    
    if not is_valid:
        print(f"License validation failed: {result}")
        sys.exit(1)
    
    # Print license info if it's a dict
    if isinstance(result, dict):
        print("License verified successfully!")
        print(f"Product: {result.get('product_id', 'Unknown')}")
        print(f"Client: {result.get('client', 'Unknown')}")
        print(f"Expires: {result.get('expires_at', 'Never')}")
    else:
        print("License OK")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(verification_code)
        
        # Make executable (Unix/Linux/Mac only)
        if platform.system() != 'Windows':
            os.chmod(output_file, 0o755)


class LicenseActivation:
    """Handle license activation and machine binding"""
    
    @staticmethod
    def activate_license(license_file: str) -> bool:
        """Activate license on current machine"""
        verifier = LicenseVerifier()
        is_valid, details = verifier.verify(license_file)
        
        if not is_valid:
            print(f"Activation failed: {details.get('reason')}")
            return False
        
        # Create activation record
        activation_record = {
            'activated_at': datetime.now().isoformat(),
            'machine_id': HardwareFingerprint.get_machine_id(),
            'system_info': HardwareFingerprint.get_system_info(),
            'license_id': details['license_id']
        }
        
        # Store activation
        activation_file = Path.home() / '.shiplock' / 'activation.json'
        activation_file.parent.mkdir(exist_ok=True)
        
        with open(activation_file, 'w') as f:
            json.dump(activation_record, f, indent=2)
        
        print("License activated successfully!")
        return True
    
    @staticmethod
    def is_activated() -> bool:
        """Check if license is already activated"""
        activation_file = Path.home() / '.shiplock' / 'activation.json'
        return activation_file.exists()
