<div align="center">

# 🚢 ShipLock

### **Secure Docker Product Distribution Platform**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Commercial-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/sarat1kyan/ShipLock)

**Enterprise-grade tool for distributing Docker-based products without exposing source code**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Contributing](#-contributing)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Why ShipLock?](#-why-shiplock)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Examples](#-usage-examples)
- [How It Works](#-how-it-works)
- [How Licensing Works](#-how-licensing-works) ⭐ **Important: Read this section**
- [Security](#-security)
- [Documentation](#-documentation)
- [Requirements](#-requirements)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#-license)

---

## 🎯 Overview

ShipLock is a **production-grade CLI tool** designed for software vendors who need to distribute Docker-based products to clients **without exposing source code**, while providing enterprise-grade licensing and copy protection.

### Perfect for:
- 🔐 **SaaS Vendors** - Distribute on-premise versions securely
- 💼 **Enterprise Software** - Protect IP while enabling client deployments
- 🎁 **Commercial Products** - License-controlled Docker applications
- 🏢 **B2B Solutions** - Secure distribution to business clients

---

## ✨ Features

### 🔒 Security Features

| Feature | Description |
|---------|-------------|
| 🛡️ **Source Code Protection** | Automatically strips source code from Docker images using multi-stage builds |
| 🔐 **Cryptographic Licensing** | RSA-4096 signed licenses with machine binding and offline validation |
| ✅ **Integrity Verification** | Tamper detection with cryptographic checksums and manifest validation |
| 🎭 **Code Obfuscation** | Advanced security hardening with bytecode compilation and obfuscation |
| 🔍 **Anti-Debug Protection** | Runtime protection against debugging and reverse engineering |

### 🚀 Development Features

| Feature | Description |
|---------|-------------|
| 🎨 **Beautiful CLI** | Rich terminal UI with colors, progress bars, and helpful error messages |
| 🐳 **Docker Integration** | Full support for Docker and docker-compose (v1 & v2) |
| 🌐 **Cross-Platform** | Works seamlessly on Linux, macOS, and Windows |
| ⚡ **Fast Build Pipeline** | Optimized build process with progress tracking |
| 📦 **Flexible Packaging** | Create directory bundles or ZIP archives for easy distribution |

### 📋 Management Features

| Feature | Description |
|---------|-------------|
| 🔑 **License Generation** | Generate cryptographically signed licenses with expiration and features |
| 🔍 **Project Analysis** | Scan and validate Docker projects before building |
| 📊 **Bundle Verification** | Comprehensive validation and testing tools |
| 📝 **Configuration System** | YAML-based configuration with sensible defaults |

---

## 💡 Why ShipLock?

### The Problem

When distributing Docker-based products, you face challenges:
- ❌ **Source Code Exposure** - Clients can extract your proprietary code
- ❌ **License Violations** - No way to control usage or enforce licensing
- ❌ **IP Theft** - Easy to copy and redistribute your product
- ❌ **Unauthorized Access** - No protection against unauthorized usage

### The Solution

ShipLock provides:
- ✅ **Complete Source Protection** - Source code never leaves your build environment
- ✅ **Cryptographic Licensing** - RSA-4096 signed licenses that can't be forged
- ✅ **Machine Binding** - Licenses tied to specific hardware (optional)
- ✅ **Tamper Detection** - Integrity checks prevent modification
- ✅ **Offline Validation** - Works without internet connection

### Example Use Case

```
Developer                    ShipLock                      Client
    │                           │                            │
    ├─── Build Product ──────────>                           │
    │                           │                            │
    │                      ┌────┴─────┐                      │
    │                      │ Build    │                      │
    │                      │ Bundle   │                      │
    │                      └────┬─────┘                      │
    │                           │                            │
    ├─── Generate License ──────>                            │
    │                           │                            │
    ├───<── Bundle + License ────                            │
    │                           │                            │
    └─── Distribute ─────────────────────────────────────────>
                                            │
                                            ├─── Extract Bundle
                                            ├─── Place License
                                            ├─── Run ./run.sh
                                            └─── Product Runs ✅
```

---

## 🚀 Quick Start

### 1️⃣ Initialize Your Project

```bash
# Navigate to your Docker project
cd /path/to/your/docker-project

# Initialize ShipLock configuration
shiplock init

# This creates:
# - .shiplock/config.yaml
# - .bundleignore
```

### 2️⃣ Analyze Your Project

```bash
# Analyze project structure and security
shiplock analyze

# Output shows:
# ✓ Docker configuration detected
# ✓ Source files will be excluded
# ✓ Security assessment
```

### 3️⃣ Build Secure Bundle

```bash
# Build distributable bundle
shiplock build --path . --output ./dist --zip

# Creates:
# - dist/
#   ├── images/        # Docker images (source code removed)
#   ├── runtime/       # Runtime scripts and configs
#   ├── MANIFEST.json  # Bundle metadata
#   └── bundle.zip     # Ready to distribute
```

### 4️⃣ Generate License

```bash
# Generate a license for your client
shiplock license generate \
  --product-id "MY-PRODUCT-001" \
  --client "Acme Corporation" \
  --expires "2025-12-31" \
  --machine-bound \
  --output ./license.key

# Creates:
# - license.key              # License file for client
# - shiplock_private.key     # Keep this SECRET!
# - shiplock_public.key      # Embedded in bundle
```

### 5️⃣ Distribute

```bash
# Send to client:
# - bundle.zip
# - license.key
# - installation instructions
```

---

## 📦 Installation

### Prerequisites

- **Python** 3.8 or higher
- **Docker** 20.10+ and docker-compose 1.29+ (or Docker Compose v2)
- **Operating System**: Linux, macOS, or Windows

### Install from Source

```bash
# Clone the repository
git clone https://github.com/sarat1kyan/ShipLock.git
cd ShipLock

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install ShipLock
pip install -e .

# Verify installation
python test_ins.py
```

### Verify Installation

```bash
# Check version
shiplock --version

# View help
shiplock --help

# Test Docker connectivity
docker --version
docker-compose --version  # or: docker compose version
```

---

## 💻 Usage Examples

### Example 1: Simple Docker Application

```bash
# Project structure:
my-app/
├── Dockerfile
├── docker-compose.yml
├── src/
│   └── app.py          # Your source code
└── requirements.txt

# Build bundle
shiplock init
shiplock analyze
shiplock build --zip

# Result: Source code removed, only compiled artifacts in bundle
```

### Example 2: Multi-Service Application

```bash
# Project with multiple services
my-platform/
├── docker-compose.yml
├── services/
│   ├── api/
│   │   └── Dockerfile
│   ├── frontend/
│   │   └── Dockerfile
│   └── database/
│       └── Dockerfile

# ShipLock handles all services automatically
shiplock build --zip
```

### Example 3: Time-Limited Trial License

```bash
# Generate 30-day trial license
shiplock license generate \
  --product-id "PRODUCT-TRIAL" \
  --client "Trial User" \
  --expires "$(date -d '+30 days' +%Y-%m-%d)" \
  --machine-bound \
  --output trial-license.key
```

### Example 4: Perpetual Enterprise License

```bash
# Generate perpetual license (no expiration)
shiplock license generate \
  --product-id "PRODUCT-ENTERPRISE" \
  --client "Acme Corporation" \
  --machine-bound \
  --output enterprise-license.key

# Note: No --expires flag = license never expires
```

### Example 5: Floating License (No Machine Binding)

```bash
# Generate license that works on any machine
shiplock license generate \
  --product-id "PRODUCT-FLOATING" \
  --client "Company Name" \
  --output floating-license.key

# Note: No --machine-bound flag = can be used on any machine
```

---

## 🔧 How It Works

### Build Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ShipLock Build Process                   │
└─────────────────────────────────────────────────────────────┘

1. PROJECT ANALYSIS
   ├── Scan project files
   ├── Detect Docker configuration
   ├── Validate security settings
   └── Check for common issues

2. DOCKER BUILD
   ├── Build Docker images (multi-stage)
   ├── Verify no source code in images
   └── Tag and prepare images

3. SOURCE STRIPPING
   ├── Export images to tar archives
   ├── Compress with gzip
   └── Verify source removal

4. RUNTIME GENERATION
   ├── Create run.sh launcher
   ├── Generate license verifier
   ├── Create image loader script
   ├── Sanitize docker-compose.yml
   └── Generate client documentation

5. SECURITY HARDENING
   ├── Obfuscate Python scripts
   ├── Add integrity checks
   ├── Generate checksums
   └── Apply anti-tamper measures

6. BUNDLE CREATION
   ├── Create directory structure
   ├── Generate MANIFEST.json
   ├── Package as ZIP (optional)
   └── Ready for distribution
```

### License System

```
┌─────────────────────────────────────────────────────────────┐
│                   Cryptographic License Flow                │
└─────────────────────────────────────────────────────────────┘

GENERATION (Vendor Side):
┌──────────────┐
│ License Data │  Product ID, Client, Expiration, Features
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ RSA-4096     │  Sign with private key
│ Signing      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ License File │  Base64 encoded + signature + integrity hash
└──────┬───────┘
       │
       ▼
   Distribute to Client

VERIFICATION (Client Side):
┌──────────────┐
│ License File │  Load from disk
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Integrity    │  Verify hash matches
│ Check        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Signature    │  Verify RSA signature with public key
│ Verification │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Validation   │  Check expiration, machine binding, features
└──────┬───────┘
       │
       ▼
   ✅ VALID or ❌ INVALID
```

---

## 🔑 How Licensing Works

### Overview

ShipLock uses **cryptographic licensing** to ensure that your Docker-based products **cannot run without a valid license**. The license system is built into the bundle and **must pass verification** before any Docker containers start.

### Key Principle: **License is Mandatory**

❌ **Without a valid license, the software WILL NOT START** - The runtime launcher (`run.sh`) performs license verification **before** any Docker containers are loaded or started. If license verification fails, the entire process exits immediately.

### License Verification Flow

```
Client runs ./runtime/run.sh
         │
         ▼
┌────────────────────────┐
│ Step 1: Integrity Check│  ← Verify bundle hasn't been tampered
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Step 2: License Check  │  ← **MANDATORY - EXITS IF FAILS**
│                        │
│ 1. Check license.key   │
│    file exists         │
│                        │
│ 2. Verify cryptographic│
│    signature (RSA-4096)│
│                        │
│ 3. Check expiration    │
│    date                │
│                        │
│ 4. Verify machine      │
│    binding (if enabled)│
│                        │
│ 5. Validate integrity  │
│    hash                │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   ✅ Valid    ❌ Invalid
      │           │
      │           └───> EXIT with error message
      │
      ▼
┌────────────────────────┐
│ Step 3: Load Images    │  ← Only if license is valid
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Step 4: Start Services │  ← Only if license is valid
└────────────────────────┘
```

### What Happens Without a License?

**Scenario 1: License File Missing**
```bash
$ ./runtime/run.sh
==================================================
  ShipLock Secure Runtime
==================================================

[1/5] Verifying bundle integrity...
✓ Integrity check passed

[2/5] Verifying license...
ERROR: License file not found
Please contact your vendor for a valid license
Expected license file at: /path/to/bundle/license.key

❌ PROCESS EXITS - No containers start
```

**Scenario 2: Invalid License**
```bash
$ ./runtime/run.sh
...
[2/5] Verifying license...
ERROR: License validation failed
License validation failed: Signature verification failed

==================================================
  LICENSE VERIFICATION FAILED
==================================================

This software requires a valid license to run.

Possible reasons:
  - License file (license.key) is missing
  - License file is invalid or corrupted
  - License has expired
  - License is not valid for this machine

❌ PROCESS EXITS - No containers start
```

**Scenario 3: Expired License**
```bash
$ ./runtime/run.sh
...
[2/5] Verifying license...
ERROR: License validation failed
License validation failed: License expired on 2024-12-31

❌ PROCESS EXITS - No containers start
```

**Scenario 4: Machine Binding Mismatch**
```bash
$ ./runtime/run.sh
...
[2/5] Verifying license...
ERROR: License validation failed
License validation failed: License not valid for this machine

❌ PROCESS EXITS - No containers start
```

### License Components

Each license file (`license.key`) contains:

1. **License Payload** (Base64 encoded JSON):
   ```json
   {
     "license_id": "uuid-v4",
     "product_id": "MY-PRODUCT-001",
     "client": "Acme Corporation",
     "issued_at": "2024-01-01T00:00:00",
     "expires_at": "2025-12-31T23:59:59",  // or "never"
     "machine_bound": true,
     "machine_id": "sha256_fingerprint",
     "features": {}
   }
   ```

2. **Cryptographic Signature** (RSA-4096):
   - Signed with vendor's private key
   - Cannot be forged or modified
   - Verified using embedded public key

3. **Integrity Hash**:
   - Prevents tampering
   - Multi-round SHA hashing with salt

### License Generation (Vendor Side)

```bash
# Step 1: Generate cryptographic key pair (one-time)
shiplock license generate \
  --product-id "MY-PRODUCT-001" \
  --client "Acme Corporation" \
  --expires "2025-12-31" \
  --machine-bound \
  --output license.key

# This creates:
# - license.key (for client)
# - shiplock_private.key (KEEP SECRET - vendor only)
# - shiplock_public.key (embedded in bundle)
```

**What happens during generation:**

1. **Create License Payload**: Product ID, client name, expiration, features
2. **Calculate Machine Fingerprint** (if machine-bound):
   - Combines: CPU serial, machine-id, hostname, MAC address
   - Hashes with SHA-256 to create unique fingerprint
3. **Sign with Private Key**: RSA-4096 signature using PSS padding
4. **Calculate Integrity Hash**: Multi-round hashing prevents tampering
5. **Encode**: Base64 encode for storage

### License Verification (Client Side)

The verification happens **automatically** when the client runs `./runtime/run.sh`:

1. **Load License File**: Reads `license.key` from bundle root
2. **Verify Integrity Hash**: Ensures file hasn't been tampered
3. **Verify Signature**: Uses embedded public key to verify RSA signature
4. **Parse License Data**: Extracts license information
5. **Check Expiration**: Compares current date with expiration
6. **Check Machine Binding**: Verifies hardware fingerprint matches (if enabled)

**All checks must pass** - If any check fails, the process exits immediately.

### Multiple Layers of Protection

1. **File-Level Check**: License file must exist
2. **Cryptographic Check**: Signature must be valid (RSA-4096)
3. **Time-Based Check**: License must not be expired
4. **Hardware Check**: Machine fingerprint must match (if enabled)
5. **Integrity Check**: License file must not be tampered

**Any failure at any layer = Software cannot run**

### Machine Binding

**What is Machine Binding?**

Machine binding ties a license to a specific hardware configuration, preventing license sharing between machines.

**How it works:**

1. **During License Generation**:
   ```bash
   # Vendor runs on client's machine or client provides machine ID
   # Machine fingerprint calculated from:
   - Hostname
   - /etc/machine-id (Linux) or Hardware UUID (macOS/Windows)
   - MAC address of primary network interface
   - CPU serial number (if available)
   
   # Combined and hashed: SHA256(components)
   # Result stored in license as machine_id
   ```

2. **During Verification**:
   ```bash
   # Client runs software
   # System calculates current machine fingerprint
   # Compares with machine_id in license
   # If mismatch → License invalid → Software won't start
   ```

**When to use Machine Binding:**

✅ **Use machine binding for:**
- Enterprise software with per-machine licensing
- High-value products where license sharing is a concern
- Compliance requirements

❌ **Don't use machine binding for:**
- Floating licenses that can move between machines
- Development/testing scenarios
- Cloud deployments where hardware changes frequently

### License Expiration

**Time-Limited License:**
```bash
# License expires on specific date
shiplock license generate \
  --expires "2025-12-31" \
  --product-id "TRIAL-001" \
  --client "Trial User"

# After 2025-12-31, software will refuse to start
```

**Perpetual License:**
```bash
# License never expires (omit --expires flag)
shiplock license generate \
  --product-id "PRODUCT-001" \
  --client "Enterprise Client"

# License valid forever (but still machine-bound if enabled)
```

### Bypassing License Verification (Security Note)

**Can clients bypass the license check?**

The license verification is integrated into the startup sequence **before** any Docker containers run. While determined attackers could potentially:

- Modify the `run.sh` script (but integrity checks detect this)
- Skip the license check (but containers won't start without it)
- Modify the verification script (but integrity checks fail)

**However:** ShipLock's goal is not to be 100% unhackable (which is impossible), but to:
- ✅ Prevent casual piracy
- ✅ Make bypassing more expensive than purchasing
- ✅ Provide legal protection through licensing terms
- ✅ Track usage and enforce licensing agreements

**For maximum security:**
1. Use machine binding for high-value products
2. Implement periodic license checks within your application
3. Use online license validation (future feature)
4. Monitor for unusual usage patterns

### License Best Practices

**For Vendors:**

1. ✅ **Keep Private Keys Secure**: Never share `shiplock_private.key`
2. ✅ **Backup Private Keys**: Store in secure location (losing it means you can't generate licenses)
3. ✅ **Track License IDs**: Maintain database of issued licenses
4. ✅ **Use Machine Binding**: For products where license sharing is a concern
5. ✅ **Set Appropriate Expiration**: Balance trial periods with renewal needs
6. ✅ **Test Licenses**: Verify licenses work on client machines before distribution

**For Clients:**

1. ✅ **Protect License File**: Keep `license.key` secure and backed up
2. ✅ **Don't Modify License**: Any changes invalidate the license
3. ✅ **Request Renewals Early**: Contact vendor before expiration
4. ✅ **Provide Machine Info**: If machine-bound, ensure vendor has correct hardware info

---

## 🔐 Security

### Security Architecture

ShipLock implements **defense in depth** with multiple security layers:

1. **Layer 7: Legal Protection** - Copyright notices and license agreements
2. **Layer 6: Obfuscation** - Bytecode compilation, string encoding, variable randomization
3. **Layer 5: Integrity Protection** - Cryptographic checksums, manifest verification
4. **Layer 4: License Enforcement** - RSA-4096 signatures, machine binding, expiration checks
5. **Layer 3: Source Protection** - Multi-stage builds, source exclusion, artifact cleanup
6. **Layer 2: Runtime Protection** - Anti-debugging, environment checks, container isolation
7. **Layer 1: Container Security** - Read-only filesystems, dropped capabilities, resource limits

### Security Guarantees

✅ **Guaranteed Protected:**
- Source code completely removed from distribution
- License signatures cannot be forged (RSA-4096)
- Machine binding prevents license sharing (when enabled)
- Integrity checks detect tampering
- All cryptographic operations use industry-standard algorithms

⚠️ **Best Effort Protection:**
- Bytecode obfuscation (can be decompiled with effort)
- Anti-debugging (skilled attackers can bypass)
- Time validation (client can manipulate system time)

### Threat Model

ShipLock is designed to protect against:
- ✅ Casual piracy and unauthorized sharing
- ✅ Reverse engineering by non-experts
- ✅ License key sharing (with machine binding)
- ✅ Simple tampering attempts

ShipLock **cannot protect** against:
- ⚠️ Determined attackers with advanced reverse engineering tools
- ⚠️ VM cloning with activated license
- ⚠️ System time manipulation (for expiration bypass)
- ⚠️ Memory extraction by root users

**Goal**: Raise the cost of attack beyond economic value for most use cases.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | Detailed system architecture and design principles |
| [**IMPLEMENTATION.md**](IMPLEMENTATION.md) | Implementation details and technical specifications |
| [**QUICK_REFERENCE.md**](QUICK_REFERENCE.md) | Quick command reference and common patterns |
| [**EXAMPLE.md**](EXAMPLE.md) | Step-by-step examples and tutorials |

### Key Documentation Sections

- 🔧 **Configuration** - `.shiplock/config.yaml` and `.bundleignore`
- 🐳 **Docker Integration** - Multi-stage builds and best practices
- 🔑 **License System** - Generation, verification, and management
- 🔒 **Security** - Obfuscation, integrity, and anti-tamper measures
- 🚀 **Build Pipeline** - Complete build process walkthrough
- 🏃 **Runtime** - Client-side execution and verification

---

## 📋 Requirements

### System Requirements

- **Operating System**: Linux, macOS (10.14+), or Windows 10+
- **Python**: 3.8 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 1.29+ or Docker Compose v2

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```
rich>=13.0.0          # Beautiful terminal UI
click>=8.0.0          # CLI framework
pyyaml>=6.0           # Configuration parsing
cryptography>=41.0.0  # Cryptographic operations
docker>=6.0.0         # Docker SDK
netifaces>=0.11.0     # Network interface detection
psutil>=5.9.0         # System utilities
```

### Docker Requirements

- Docker daemon must be running
- User must have permissions to build and export images
- Sufficient disk space for image building and export

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with tests
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest

# Format code
black .

# Type checking
mypy shiplock_*.py

# Linting
flake8 shiplock_*.py
```

### Code Style

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all public functions
- Add tests for new features
- Update documentation as needed

---

## 💬 Support

### Getting Help

- 📖 **Documentation**: Check the [documentation](#-documentation) section above
- 🐛 **Bug Reports**: Open an issue on [GitHub](https://github.com/sarat1kyan/ShipLock/issues)
- 💡 **Feature Requests**: Open an issue with the `enhancement` label
- ❓ **Questions**: Open an issue with the `question` label

All support is handled through GitHub Issues. Please search existing issues before creating a new one.

### Common Issues

<details>
<summary><b>Docker not found</b></summary>

```bash
# Verify Docker is installed
docker --version

# Start Docker daemon (Linux)
sudo systemctl start docker

# On macOS/Windows, start Docker Desktop
```
</details>

<details>
<summary><b>Source code detected in image</b></summary>

Use a multi-stage Dockerfile:

```dockerfile
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
RUN python -m compileall /app/src/

FROM python:3.11-slim
COPY --from=builder /app/src/__pycache__ /app/
CMD ["python", "-m", "app"]
```
</details>

<details>
<summary><b>License verification failed</b></summary>

Check:
1. License file exists and is readable
2. Machine binding matches (if enabled)
3. License hasn't expired
4. License file hasn't been corrupted

```bash
# Verify license manually
shiplock license verify ./license.key
```
</details>

---

## 📄 License

This project is licensed under a **Commercial License**. See the [LICENSE](LICENSE) file for details.

### License Types

- **Commercial Use**: Requires a commercial license
- **Enterprise**: Open an issue on [GitHub](https://github.com/sarat1kyan/ShipLock/issues) with the `enterprise` label
- **Evaluation**: Free evaluation for testing purposes

For licensing inquiries, please open an issue on [GitHub](https://github.com/sarat1kyan/ShipLock/issues) with the `license` label.

---

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Uses [cryptography](https://github.com/pyca/cryptography) for cryptographic operations
- Inspired by best practices in software protection and licensing

---

<div align="center">

**Made with ❤️ by [sarat1kyan](https://github.com/sarat1kyan)**

[⭐ Star us on GitHub](https://github.com/sarat1kyan/ShipLock) • [📖 Documentation](ARCHITECTURE.md) • [🐛 Report Bug](https://github.com/sarat1kyan/ShipLock/issues)

**ShipLock v1.0.0** • Secure • Reliable • Production-Ready

</div>