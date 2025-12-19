# ShipLock Quick Reference

## Installation

```bash
pip install -r requirements.txt
pip install -e .
shiplock --version
```

## Quick Start

```bash
# 1. Initialize
cd /path/to/project
shiplock init

# 2. Analyze
shiplock analyze

# 3. Build
shiplock build --path . --output ./dist --zip

# 4. Generate License
shiplock license generate \
  --product-id "PROD-001" \
  --client "Client Name" \
  --expires "2025-12-31" \
  --machine-bound \
  --output license.key

# 5. Distribute
# Send: dist/bundle.zip + license.key
```

## CLI Commands

### Project Commands

```bash
# Initialize project
shiplock init [--path PATH]

# Analyze project
shiplock analyze [--path PATH]
```

### Build Commands

```bash
# Build to directory
shiplock build --path . --output ./dist

# Build as ZIP
shiplock build --path . --output ./dist --zip

# Push to GitHub
shiplock build --path . --github git@github.com:user/repo.git
```

### License Commands

```bash
# Generate license
shiplock license generate \
  --product-id ID \
  --client NAME \
  [--expires YYYY-MM-DD] \
  [--machine-bound] \
  --output FILE

# Verify license
shiplock license verify LICENSE_FILE
```

## Configuration Files

### .shiplock/config.yaml

```yaml
project:
  name: my-product
  version: 1.0.0

build:
  strip_source: true
  multi_stage: true
  compress: true

exclude:
  - "*.py"
  - "src/"
  - ".git/"

include:
  - "docker-compose.yml"
  - "Dockerfile"

licensing:
  enabled: true
  type: machine_bound
```

### .bundleignore

```
# Source code
*.py
*.js
*.ts
src/

# Development
.git/
tests/
*.log
```

## Bundle Structure

```
bundle/
├── images/
│   └── *.tar.gz          # Docker images
├── runtime/
│   ├── run.sh            # Main launcher
│   ├── docker-compose.yml
│   ├── verify_license.py
│   └── README.md
├── MANIFEST.json
└── CHECKSUMS.txt
```

## Client Usage

```bash
# Extract bundle
unzip bundle.zip
cd bundle

# Place license
cp license.key ./

# Run
./runtime/run.sh

# Stop
docker-compose down
```

## Dockerfile Best Practice

```dockerfile
# Multi-stage build (REQUIRED)
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
RUN python -m compileall /app/src/

# Runtime (no source!)
FROM python:3.11-slim
COPY --from=builder /app/src/*.pyc /app/
CMD ["python", "app.pyc"]
```

## Security Checklist

### Before Build
- ✅ Multi-stage Dockerfile
- ✅ No secrets in .env
- ✅ .bundleignore configured
- ✅ Source files excluded

### After Build
- ✅ Test bundle on clean machine
- ✅ Verify no source in images
- ✅ Test license verification
- ✅ Check integrity protection

### Before Distribution
- ✅ Generate license
- ✅ Test license on target machine
- ✅ Prepare documentation
- ✅ Backup private key

## Troubleshooting

### Build Issues

```bash
# Error: Dockerfile not found
# Solution: Ensure Dockerfile exists in project root

# Error: Source files detected in image
# Solution: Use multi-stage Dockerfile

# Error: docker-compose.yml not found
# Solution: Create docker-compose.yml or build with Dockerfile only
```

### License Issues

```bash
# Error: License file not found
# Solution: Place license.key in bundle root

# Error: License not valid for this machine
# Solution: Machine-bound license - request new license

# Error: License expired
# Solution: Request license renewal

# Error: Signature verification failed
# Solution: License corrupted - request new license
```

### Runtime Issues

```bash
# Error: Integrity verification failed
# Solution: Bundle tampered - re-download

# Error: Image not found
# Solution: Run load_images.sh first

# Error: Port already in use
# Solution: Change port in docker-compose.yml
```

## Environment Variables

```bash
# License file location (default: ./license.key)
export SHIPLOCK_LICENSE=/path/to/license.key

# Debug mode
export SHIPLOCK_DEBUG=1

# Skip integrity check (NOT RECOMMENDED)
export SHIPLOCK_SKIP_INTEGRITY=1
```

## License File Structure

```json
{
  "license": "base64_payload",
  "signature": "base64_signature",
  "public_key": "pem_key",
  "integrity": "hash"
}
```

## Cryptography Details

```
RSA-4096        # Signing algorithm
SHA-256         # Hashing algorithm
PSS padding     # RSA padding mode
AES-256         # Key encryption
```

## Hardware Fingerprint

```
Machine ID = SHA256(
    CPU_Serial +
    /etc/machine-id +
    Hostname +
    MAC_Address
)
```

## Performance Metrics

```
Build Time:     1-10 minutes (typical)
Startup Time:   5-10 seconds (typical)
License Check:  ~50ms
Integrity Check: ~100ms
Bundle Overhead: <1MB
```

## File Size Estimates

```
Small API:      ~50MB compressed
Web App:        ~200MB compressed
Database App:   ~500MB compressed
ML Application: ~2GB compressed
```

## Security Guarantees

✅ **Guaranteed Protected:**
- Source code removed
- License signature verified
- Machine binding enforced
- Integrity checked

⚠️ **Best Effort:**
- Bytecode obfuscation
- Anti-debugging
- Time validation
- VM detection

## Common Patterns

### Pattern 1: Time-Limited Trial

```bash
shiplock license generate \
  --product-id "PROD-001" \
  --client "Trial User" \
  --expires "2024-12-31" \
  --machine-bound
```

### Pattern 2: Perpetual License

```bash
shiplock license generate \
  --product-id "PROD-001" \
  --client "Enterprise Corp" \
  --machine-bound
  # No --expires = never expires
```

### Pattern 3: Floating License

```bash
shiplock license generate \
  --product-id "PROD-001" \
  --client "Company Dept"
  # No --machine-bound = can move machines
```

### Pattern 4: Feature-Gated

```bash
shiplock license generate \
  --product-id "PROD-001" \
  --client "Premium Client" \
  --features '{"tier": "premium", "users": 100}'
```

## API Examples (Future)

```python
# Programmatic license generation
from shiplock import LicenseGenerator

gen = LicenseGenerator()
license = gen.create_license(
    product_id="PROD-001",
    client="Acme Corp",
    expires="2025-12-31",
    machine_bound=True
)

signed = gen.sign_license(license)
gen.write_license(signed, "license.key")
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install ShipLock
        run: pip install shiplock
      - name: Build bundle
        run: |
          shiplock build --path . --output ./dist --zip
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: bundle
          path: dist/*.zip
```

### Docker Compose for Client

```yaml
# docker-compose.yml (generated by ShipLock)
version: '3.8'
services:
  app:
    image: prebuilt-image:latest
    ports:
      - "8080:8080"
    environment:
      - LICENSE_FILE=/app/license.key
    volumes:
      - ./license.key:/app/license.key:ro
    restart: unless-stopped
    healthcheck:
      test: python /app/verify_license.py
      interval: 5m
```

## Best Practices Summary

### DO:
✅ Use multi-stage Dockerfiles
✅ Test bundles before distribution
✅ Keep private keys secure
✅ Track issued licenses
✅ Provide clear documentation
✅ Test on clean machines

### DON'T:
❌ Include real secrets in bundles
❌ Commit private keys to Git
❌ Skip integrity verification
❌ Modify obfuscated code
❌ Share private keys
❌ Trust client-provided time

## Support Resources

- **Documentation**: README.md, ARCHITECTURE.md
- **Examples**: EXAMPLE.md
- **Reference**: This file
- **Issues**: GitHub issues
- **Email**: support@shiplock.io

## Version History

```
v1.0.0 (2024-12)
- Initial release
- RSA-4096 licensing
- Machine binding
- Source protection
- Integrity verification
```

## Quick Command Reference

```bash
# Most common workflow
shiplock init                    # Initialize
shiplock analyze                 # Check project
shiplock build --zip             # Build bundle
shiplock license generate ...    # Create license

# Client workflow
./runtime/run.sh                 # Run product
docker-compose logs -f           # View logs
docker-compose down              # Stop product
```

---

**ShipLock Quick Reference v1.0.0**

