# ShipLock Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Security Architecture](#security-architecture)
5. [License System Design](#license-system-design)
6. [Build Pipeline](#build-pipeline)
7. [Runtime Protection](#runtime-protection)

---

## Overview

ShipLock is designed as a layered security system where each layer provides independent protection against different attack vectors.

### Design Principles

1. **Defense in Depth**: Multiple independent security layers
2. **Least Privilege**: Minimal runtime permissions
3. **Zero Trust**: Verify everything, trust nothing
4. **Fail Secure**: Default to deny on errors
5. **Cryptographic Foundation**: All security based on proven cryptography

### Threat Assumptions

- **Attacker Goal**: Extract source code or bypass licensing
- **Attacker Capability**: Full access to bundle, container, and runtime environment
- **Attacker Resources**: Skilled reverse engineer with debugging tools
- **Defense Goal**: Raise cost of attack beyond economic value

---

## System Components

### 1. CLI Interface Layer

**Purpose**: User-facing interface for all operations

**Components**:
- `shiplock_cli.py`: Main CLI entry point with Rich UI
- Command routing and validation
- Progress tracking and user feedback

**Key Features**:
- Beautiful terminal UI with colors and progress bars
- Input validation and error handling
- Comprehensive help system

**Security Considerations**:
- Input sanitization
- Path traversal prevention
- Command injection protection

---

### 2. Project Analysis Engine

**Purpose**: Scan and validate Docker projects

**File**: `shiplock_analyzer.py`

**Functions**:

```python
class ProjectAnalyzer:
    - __init__(project_path)
    - scan_project() -> Dict[str, Any]
    - detect_docker() -> Dict[str, Any]
    - analyze_dependencies() -> Dict[str, List]
    - validate() -> Dict[str, Any]
```

**Analysis Process**:

```
1. Load Configuration
   ├── Read .shiplock/config.yaml
   ├── Load .bundleignore patterns
   └── Apply defaults

2. Scan Files
   ├── Walk directory tree
   ├── Apply ignore patterns
   ├── Categorize files (include/exclude)
   └── Identify source files

3. Detect Docker
   ├── Find Dockerfile
   ├── Parse docker-compose.yml
   ├── Detect multi-stage builds
   └── Extract metadata

4. Validate
   ├── Check for required files
   ├── Verify source protection
   ├── Detect secrets in .env
   └── Generate warnings
```

**Output**:
- File inclusion/exclusion lists
- Docker configuration metadata
- Validation report with warnings
- Build readiness status

---

### 3. Bundle Builder

**Purpose**: Build secure, distributable bundles

**File**: `shiplock_builder.py`

**Class Hierarchy**:

```
BundleBuilder
├── validate()
├── build_images()
│   ├── _get_compose_images()
│   └── _verify_no_source_in_image()
├── strip_source_code()
│   └── _export_images()
├── generate_runtime()
│   ├── _generate_run_script()
│   ├── _generate_load_images_script()
│   ├── _copy_compose_file()
│   ├── _generate_license_verifier()
│   └── _generate_readme()
├── apply_security()
├── create_directory_bundle()
├── create_zip_bundle()
└── push_to_github()
```

**Build Pipeline**:

```
Input: Docker Project
   ↓
[1] Validate Project
   ├── Check Dockerfile exists
   ├── Verify configuration
   └── Ensure no blocking issues
   ↓
[2] Build Docker Images
   ├── Execute docker build / docker-compose build
   ├── Tag images appropriately
   └── Verify build success
   ↓
[3] Strip Source Code
   ├── Verify no source in images
   ├── Export images to tar
   └── Compress archives
   ↓
[4] Generate Runtime
   ├── Create run.sh launcher
   ├── Generate image loader
   ├── Sanitize docker-compose.yml
   ├── Create license verifier
   └── Generate documentation
   ↓
[5] Apply Security
   ├── Obfuscate Python code
   ├── Add integrity checks
   ├── Generate checksums
   └── Add anti-debug
   ↓
[6] Package Bundle
   ├── Create directory structure
   ├── Generate manifest
   └── Package as ZIP or push to GitHub
   ↓
Output: Secure Bundle
```

**Security Guarantees**:
- ✅ Source code never in bundle
- ✅ Images contain only runtime artifacts
- ✅ All verification code obfuscated
- ✅ Integrity protected

---

### 4. License System

**Purpose**: Cryptographic licensing with machine binding

**File**: `shiplock_license.py`

**Components**:

```
HardwareFingerprint
├── get_machine_id() -> str
├── _get_mac_address() -> str
└── get_system_info() -> Dict

LicenseGenerator
├── generate_keys() -> (private, public)
├── load_keys()
├── create_license(...) -> Dict
├── sign_license(data) -> str
└── write_license(signed, path)

LicenseVerifier
├── verify(license_file) -> (bool, Dict)
├── _calculate_integrity(...)
└── create_verification_script(path)

LicenseActivation
├── activate_license(file) -> bool
└── is_activated() -> bool
```

**Cryptographic Architecture**:

```
Key Generation:
RSA-4096 Private Key
   ↓
Private Key (PKCS8, AES-256 encrypted)
   ↓
Public Key (SubjectPublicKeyInfo)

License Creation:
Payload (JSON)
   ↓
Sign with RSA-PSS-SHA256
   ↓
Base64 Encode
   ↓
Add Integrity Hash
   ↓
Final License Structure

Verification:
Load License
   ↓
Verify Integrity
   ↓
Verify RSA Signature
   ↓
Check Expiration
   ↓
Check Machine Binding
   ↓
VALID / INVALID
```

**Machine Fingerprint Algorithm**:

```python
Components = [
    CPU_Serial,
    Machine_ID (/etc/machine-id),
    Hostname,
    MAC_Address (primary interface)
]

Combined = '|'.join(Components)
Fingerprint = SHA256(Combined)
```

**License Payload Structure**:

```json
{
  "license_id": "uuid-v4",
  "product_id": "PRODUCT-001",
  "client": "Client Name",
  "issued_at": "ISO-8601",
  "expires_at": "ISO-8601 or 'never'",
  "machine_bound": true,
  "machine_id": "sha256_fingerprint",
  "system_info": {
    "platform": "Linux",
    "hostname": "server-01",
    ...
  },
  "features": {}
}
```

**Integrity Hash**:

```
integrity = SHA256(
  SHA512(
    SHA256(
      license_base64 + ":" + signature_base64 + salt
    ) + salt
  ) + salt
)
```

This multi-round hashing makes pre-computation attacks infeasible.

---

### 5. Security Hardening

**Purpose**: Obfuscation and anti-tamper protection

**File**: `shiplock_security.py`

**Components**:

```
SecurityHardening
├── obfuscate_python_files()
├── add_integrity_verification()
├── generate_checksums()
└── add_anti_debug()

CodeObfuscator
├── randomize_variable_names()
└── encrypt_strings()

RuntimeProtection
├── create_container_entrypoint()
└── create_dockerfile_patch()

AntiReverse
├── strip_debug_symbols()
├── add_fake_flags()
└── obfuscate_critical_constants()
```

**Obfuscation Techniques**:

1. **Variable Randomization**
   ```python
   # Before
   def verify_license(license_file):
       with open(license_file) as f:
           data = f.read()
   
   # After
   def _a1b2c3(f4d5e6):
       with open(f4d5e6) as g7h8i9:
           j0k1l2 = g7h8i9.read()
   ```

2. **String Encoding**
   ```python
   # Before
   if status == "valid":
   
   # After
   if status == __import__("base64").b64decode("dmFsaWQ=").decode():
   ```

3. **Bytecode Compilation**
   ```
   verify_license.py
      ↓
   verify_license.pyc (bytecode)
      ↓
   verify_license.py (launcher that loads .pyc)
   ```

4. **Dead Code Injection**
   ```python
   # Decoy functions
   def _validate_online_license(url, key):
       # Looks real but unused
       import requests
       return requests.post(url, json={'key': key})
   
   # Actual verification is hidden elsewhere
   ```

**Anti-Debug Measures**:

```python
def check_debugger():
    # Check environment variables
    if 'PYDEVD_USE_FRAME_EVAL' in os.environ:
        return True
    
    # Check ptrace (Linux)
    with open('/proc/self/status') as f:
        if 'TracerPid:' in f.read() and pid != 0:
            return True
    
    return False
```

**Integrity Verification**:

```
Startup
   ↓
Load MANIFEST.json
   ↓
For each critical file:
   ├── Calculate SHA256
   ├── Compare with manifest
   └── Fail if mismatch
   ↓
Continue only if all pass
```

---

## Data Flow

### Build-Time Flow

```
Developer Machine:
┌─────────────────────────────────────────┐
│ 1. Project Source Code                  │
│    ├── app.py (Python)                  │
│    ├── Dockerfile                       │
│    └── docker-compose.yml               │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 2. ShipLock Analyze                     │
│    ├── Scan files                       │
│    ├── Detect Docker config             │
│    └── Validate project                 │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 3. Docker Build                         │
│    ├── Build images                     │
│    ├── Multi-stage optimization         │
│    └── Verify no source in images       │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 4. Bundle Creation                      │
│    ├── Export images to tar.gz          │
│    ├── Generate runtime scripts         │
│    ├── Apply obfuscation                │
│    └── Add integrity checks              │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 5. License Generation                   │
│    ├── Generate RSA keys                │
│    ├── Create license payload           │
│    ├── Sign with private key            │
│    └── Write license file                │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 6. Distribution                         │
│    ├── Bundle (ZIP or GitHub)           │
│    └── License file (separate)          │
└─────────────────────────────────────────┘
```

### Runtime Flow

```
Client Machine:
┌─────────────────────────────────────────┐
│ 1. Extract Bundle                       │
│    └── Unzip my-product-bundle.zip      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 2. Place License                        │
│    └── cp license.key ./                │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 3. Execute run.sh                       │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 4. Integrity Verification               │
│    ├── Load MANIFEST.json               │
│    ├── Check file checksums             │
│    └── Fail if tampered                 │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 5. License Verification                 │
│    ├── Load license.key                 │
│    ├── Verify signature                 │
│    ├── Check expiration                 │
│    ├── Verify machine binding           │
│    └── Fail if invalid                  │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 6. Load Docker Images                   │
│    ├── Decompress tar.gz files          │
│    └── docker load < image.tar          │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 7. Start Services                       │
│    └── docker-compose up -d             │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 8. Application Running                  │
│    └── Periodic license checks          │
└─────────────────────────────────────────┘
```

---

## Security Architecture

### Defense Layers

```
Layer 7: Legal Protection
   ├── Copyright notice
   ├── License agreement
   └── Terms of service

Layer 6: Obfuscation
   ├── Bytecode compilation
   ├── String encoding
   ├── Variable randomization
   └── Dead code injection

Layer 5: Integrity Protection
   ├── Cryptographic checksums
   ├── Manifest verification
   └── Tamper detection

Layer 4: License Enforcement
   ├── RSA-4096 signatures
   ├── Machine binding
   ├── Expiration checks
   └── Offline validation

Layer 3: Source Protection
   ├── Multi-stage builds
   ├── Source exclusion
   └── Build artifact cleanup

Layer 2: Runtime Protection
   ├── Anti-debugging
   ├── Environment checks
   └── Container isolation

Layer 1: Container Security
   ├── Read-only filesystems
   ├── Dropped capabilities
   └── Resource limits
```

### Attack Surface Reduction

**Eliminated Attack Vectors**:
- ✅ Source code not present
- ✅ Debug symbols stripped
- ✅ Build artifacts removed
- ✅ Secrets not included

**Hardened Attack Vectors**:
- ⚠️ Bytecode decompilation (obfuscated)
- ⚠️ License file copying (machine-bound)
- ⚠️ Verification bypass (multi-layer)
- ⚠️ Memory extraction (requires root)

**Remaining Risks**:
- ⚠️ Determined attacker with debugging tools
- ⚠️ VM cloning with activated license
- ⚠️ Time manipulation for expiry bypass
- ⚠️ Advanced reverse engineering

---

## Implementation Notes

### Why RSA-4096?

- **Security**: 4096-bit RSA provides ~150-bit security level
- **Future-Proof**: Resistant to quantum computers (for now)
- **Standard**: Widely supported, well-audited implementations
- **Performance**: Signing is rare, verification is fast enough

### Why Machine Binding?

- **Prevents Sharing**: Can't share license between machines
- **Track Usage**: Know where product is deployed
- **Revenue Protection**: One license = one deployment

### Why Offline Validation?

- **Privacy**: No phone-home requirement
- **Reliability**: Works without internet
- **Air-Gapped**: Supports high-security environments
- **Performance**: Fast local verification

### Why Multiple Hash Rounds?

```python
# Single hash
integrity = SHA256(data)
# Vulnerable to rainbow tables

# Multiple rounds with salt
integrity = SHA256(SHA512(SHA256(data + salt) + salt) + salt)
# Pre-computation infeasible
```

---

## Performance Considerations

### Build Time

- Multi-stage Docker builds: Adds 10-30% to build time
- Source verification: Negligible (<1 second)
- Image export: Proportional to image size
- Compression: ~30 seconds per GB
- Obfuscation: ~5 seconds per 1000 lines

### Runtime

- Integrity check: ~100ms for typical bundle
- License verification: ~50ms (RSA verification)
- Image loading: Proportional to image size
- Startup overhead: ~200-500ms total

### Storage

- Bundle size: ~same as original images
- Compression: 40-60% reduction with gzip
- Overhead: <1MB for verification scripts

---

## Extensibility

### Plugin Architecture (Future)

```python
class ShipLockPlugin:
    def pre_build(self, context):
        pass
    
    def post_build(self, context):
        pass
    
    def verify_license(self, license, context):
        pass
    
    def add_features(self, bundle):
        pass
```

### Custom Verification

Vendors can inject custom verification logic:

```python
def custom_verify():
    # Check custom requirements
    if not meets_requirements():
        sys.exit(1)
```

---

## Maintenance and Updates

### Key Rotation

```bash
# Generate new keys
shiplock license generate-keys --output ./new-keys/

# Re-sign existing licenses (requires private key)
shiplock license resign --old-key ./old-private.key \
                       --new-key ./new-private.key \
                       --licenses ./licenses/*.key
```

### License Updates

```bash
# Extend expiration
shiplock license extend \
  --license client-license.key \
  --new-expiry 2026-12-31

# Add features
shiplock license add-feature \
  --license client-license.key \
  --feature "premium_support"
```

---

## Conclusion

ShipLock provides enterprise-grade security for Docker distributions through:

1. **Multi-layered security** - Defense in depth
2. **Strong cryptography** - RSA-4096, SHA-256
3. **Machine binding** - Hardware fingerprinting
4. **Source protection** - Complete removal
5. **Obfuscation** - Code and runtime protection
6. **Integrity verification** - Tamper detection

While no system is 100% secure, ShipLock raises the cost of attack significantly beyond the value for most use cases.

