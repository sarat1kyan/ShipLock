#!/usr/bin/env python3
"""
ShipLock Installation Test
Verifies that all components are working correctly
"""

import sys
import importlib

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")
    
    required_packages = {
        'rich': 'Rich terminal formatting',
        'click': 'CLI framework',
        'yaml': 'YAML parsing (PyYAML)',
        'cryptography': 'Cryptographic operations',
        'docker': 'Docker SDK',
        'psutil': 'System utilities',
    }
    
    optional_packages = {
        'netifaces': 'Network interfaces (for advanced fingerprinting)',
    }
    
    failed = []
    
    print("\nRequired Packages:")
    print("-" * 50)
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {package:20s} - {description}")
        except ImportError as e:
            print(f"✗ {package:20s} - {description}")
            print(f"  Error: {e}")
            failed.append(package)
    
    print("\nOptional Packages:")
    print("-" * 50)
    for package, description in optional_packages.items():
        try:
            importlib.import_module(package)
            print(f"✓ {package:20s} - {description}")
        except ImportError:
            print(f"⚠ {package:20s} - {description} (optional)")
    
    return len(failed) == 0

def test_shiplock_modules():
    """Test that ShipLock modules can be imported"""
    print("\n\nTesting ShipLock Modules:")
    print("-" * 50)
    
    modules = [
        'shiplock_cli',
        'shiplock_analyzer',
        'shiplock_builder',
        'shiplock_license',
        'shiplock_security',
    ]
    
    failed = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}")
            print(f"  Error: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_cryptography():
    """Test cryptographic operations"""
    print("\n\nTesting Cryptographic Operations:")
    print("-" * 50)
    
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        
        print("✓ Generating RSA key pair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # Use 2048 for faster test
            backend=default_backend()
        )
        
        print("✓ Extracting public key...")
        public_key = private_key.public_key()
        
        print("✓ Cryptography library working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Cryptography test failed: {e}")
        return False

def test_docker():
    """Test Docker connectivity"""
    print("\n\nTesting Docker:")
    print("-" * 50)
    
    try:
        import docker
        
        print("✓ Docker SDK imported")
        
        try:
            client = docker.from_env()
            version = client.version()
            print(f"✓ Docker daemon connected")
            print(f"  Version: {version.get('Version', 'unknown')}")
            return True
        except Exception as e:
            print(f"⚠ Docker daemon not accessible: {e}")
            print("  This is OK if Docker isn't running yet")
            return True  # Not a fatal error
            
    except Exception as e:
        print(f"✗ Docker SDK test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ShipLock Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("ShipLock Modules", test_shiplock_modules),
        ("Cryptography", test_cryptography),
        ("Docker", test_docker),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nUnexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10s} - {name}")
    
    print("-" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! ShipLock is ready to use.")
        print("\nNext steps:")
        print("  1. Run: shiplock --version")
        print("  2. Try: shiplock init")
        print("  3. Read: README.md for usage guide")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Ensure all requirements are installed: pip install -r requirements.txt")
        print("  2. Check Python version: python3 --version (need 3.8+)")
        print("  3. Install system dependencies (see INSTALL.md)")
        print("  4. For Docker errors, start Docker: sudo systemctl start docker")
        return 1

if __name__ == '__main__':
    sys.exit(main())
