# ShipLock Complete Usage Example

This document demonstrates a complete end-to-end workflow of using ShipLock to secure and distribute a Docker-based Python application.

---

## Example Project: Flask API

We'll use a simple Flask REST API as our example product.

### Step 1: Create Sample Application

#### Directory Structure

```
my-api/
├── src/
│   ├── app.py
│   ├── models.py
│   └── utils.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

#### src/app.py

```python
from flask import Flask, jsonify
from models import get_users
from utils import validate_api_key

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def users():
    api_key = request.headers.get('X-API-Key')
    if not validate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(get_users())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### src/models.py

```python
def get_users():
    # Business logic - we want to protect this
    return [
        {'id': 1, 'name': 'John Doe'},
        {'id': 2, 'name': 'Jane Smith'}
    ]
```

#### src/utils.py

```python
import os

def validate_api_key(key):
    # Proprietary validation logic
    expected_key = os.getenv('API_KEY', 'default-key')
    return key == expected_key
```

#### Dockerfile (Multi-Stage)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and compile source
COPY src/ /app/src/
RUN python -m compileall /app/src/

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy only dependencies and compiled bytecode
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /app/src/__pycache__/*.pyc /app/

# NO source code (.py files) in final image!

ENV PYTHONPATH=/app
EXPOSE 5000

CMD ["python", "-c", "import app; app.app.run(host='0.0.0.0', port=5000)"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - API_KEY=${API_KEY}
    restart: unless-stopped
```

#### requirements.txt

```
flask==3.0.0
gunicorn==21.2.0
```

#### .env.example

```
API_KEY=your-secret-key-here
```

---

## Step 2: Initialize ShipLock

```bash
cd my-api
shiplock init
```

**Output:**
```
╔═══════════════════════════════════════════════════════╗
║                     SHIPLOCK                          ║
║          Secure Docker Distribution Platform          ║
╚═══════════════════════════════════════════════════════╝

[1/3] Initializing ShipLock configuration
[2/3] Creating .bundleignore file
[3/3] Project initialized successfully

┌─ Initialization Summary ─────────────────────────┐
│ File                    │ Status                 │
├─────────────────────────┼────────────────────────┤
│ .shiplock/config.yaml   │ ✓ Created              │
│ .bundleignore           │ ✓ Created              │
└─────────────────────────┴────────────────────────┘

✓ ShipLock project initialized!
ℹ Edit .shiplock/config.yaml to customize your build
```

### Generated .bundleignore

```
# Source code (critical!)
*.py
src/

# Development files
.git/
.gitignore
.env
__pycache__/
*.pyc
*.log

# Documentation
README.md
docs/
```

### Generated .shiplock/config.yaml

```yaml
project:
  name: my-api
  version: 1.0.0

build:
  strip_source: true
  multi_stage: true
  compress: true

exclude:
  - "*.py"
  - "src/"
  - ".git/"
  - "__pycache__/"

include:
  - "docker-compose.yml"
  - "Dockerfile"
  - ".env.example"

licensing:
  enabled: true
  type: machine_bound
  offline_validation: true
```

---

## Step 3: Analyze Project

```bash
shiplock analyze
```

**Output:**
```
╔═══════════════════════════════════════════════════════╗
║                     SHIPLOCK                          ║
║          Secure Docker Distribution Platform          ║
╚═══════════════════════════════════════════════════════╝

[1/4] Scanning project directory
Analyzing project... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[2/4] Project scan complete

📦 Project: my-api
├── 🐳 Docker Configuration
│   ├── ✓ Dockerfile found
│   └── ✓ docker-compose.yml (1 services)
└── 📁 Files (8 total)
    ├── Include: 3 files
    └── Exclude: 5 files

[3/4] Security analysis

┌─ Security Assessment ──────────────────────────────┐
│ Check                     │ Status                 │
├───────────────────────────┼────────────────────────┤
│ Source code protection    │ ✓ Enabled              │
│ Multi-stage build         │ ✓ Detected             │
│ Secrets in .env           │ ✓ Clean                │
└───────────────────────────┴────────────────────────┘

[4/4] Analysis complete
✓ Project is ready to bundle!
```

---

## Step 4: Build Secure Bundle

```bash
shiplock build --path . --output ./dist --zip
```

**Output:**
```
╔═══════════════════════════════════════════════════════╗
║                     SHIPLOCK                          ║
║          Secure Docker Distribution Platform          ║
╚═══════════════════════════════════════════════════════╝

[1/6] Initializing build process
Validating project... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[2/6] Building Docker images
Building Docker images... ━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[3/6] Stripping source code
Removing source code... ━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[4/6] Generating runtime scripts
Creating runtime environment... ━━━━━━━━━━━━━━━━━━━ 100%

[5/6] Applying security measures
Applying obfuscation... ━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[6/6] Creating distribution package
Packaging bundle... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

✓ ZIP bundle created: /home/user/my-api/dist/my-api-bundle.zip

┌─ Build Complete ─────────────────────────────────────┐
│                                                       │
│ ✓ Build completed successfully!                      │
│                                                       │
│ Bundle Location: ./dist                              │
│ Distribution Type: ZIP Archive                       │
│                                                       │
│ Next Steps:                                          │
│ 1. Test the bundle: cd dist && ./run.sh             │
│ 2. Generate license: shiplock license generate      │
│ 3. Deliver to client                                 │
│                                                       │
│ Security Reminder:                                   │
│ • Source code has been stripped                      │
│ • Images are production-ready                        │
│ • License verification is active                     │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Bundle Contents

```
my-api-bundle.zip
├── images/
│   └── my-api_api_latest.tar.gz     (Docker image, no source!)
├── runtime/
│   ├── run.sh                        (Main launcher)
│   ├── load_images.sh                (Image loader)
│   ├── docker-compose.yml            (Sanitized)
│   ├── verify_license.sh             (License checker)
│   ├── verify_license.py             (Obfuscated verifier)
│   ├── verify_integrity.py           (Integrity checker)
│   └── README.md                     (Client instructions)
├── MANIFEST.json                     (Bundle metadata)
└── CHECKSUMS.txt                     (File checksums)
```

---

## Step 5: Generate License

```bash
shiplock license generate \
  --product-id "MY-API-001" \
  --client "Acme Corporation" \
  --expires "2025-12-31" \
  --machine-bound \
  --output acme-license.key
```

**Output:**
```
╔═══════════════════════════════════════════════════════╗
║                     SHIPLOCK                          ║
║          Secure Docker Distribution Platform          ║
╚═══════════════════════════════════════════════════════╝

[1/4] Generating cryptographic keys
Creating license... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[2/4] License generated successfully

┌─ License Details ────────────────────────────────────┐
│ Property      │ Value                                │
├───────────────┼──────────────────────────────────────┤
│ Product ID    │ MY-API-001                           │
│ Client        │ Acme Corporation                     │
│ Expires       │ 2025-12-31                           │
│ Machine Bound │ Yes                                  │
│ License File  │ acme-license.key                     │
└───────────────┴──────────────────────────────────────┘

[3/4] Saving private key
⚠ Keep the private key secure - required for future licenses!

[4/4] License ready for distribution

┌─ License Generated ──────────────────────────────────┐
│                                                       │
│ ✓ License created successfully!                      │
│                                                       │
│ License File: acme-license.key                       │
│ Public Key: shiplock_public.key                      │
│ Private Key: shiplock_private.key                    │
│                                                       │
│ Distribution Instructions:                           │
│ 1. Include license file in bundle                    │
│ 2. Client activates with: ./activate_license.sh     │
│ 3. Product verifies on startup                       │
│                                                       │
│ Security Notes:                                      │
│ • Private key must be kept secret                    │
│ • License is cryptographically signed                │
│ • Machine binding prevents sharing                   │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### License File Content (acme-license.key)

```json
{
  "license": "eyJsaWNlbnNlX2lkIjogIjEyMzQ1Njc4LWFiY2QtZWZnaC1pamsxLW1ub3BxcnN0dXZ3eCIsICJwcm9kdWN0X2lkIjogIk1ZLUFQSS0wMDEiLCAiY2xpZW50IjogIkFjbWUgQ29ycG9yYXRpb24iLCAiaXNzdWVkX2F0IjogIjIwMjQtMTItMDFUMDA6MDA6MDAiLCAiZXhwaXJlc19hdCI6ICIyMDI1LTEyLTMxVDIzOjU5OjU5IiwgIm1hY2hpbmVfYm91bmQiOiB0cnVlLCAibWFjaGluZV9pZCI6ICJhYmMxMjNkZWY0NTZnaGk3ODkuLi4ifQ==",
  "signature": "kJHGFDSAasdfghjklzxcvbnmqwertyuiopASDFGHJKLZXCVBNMQWERTYUIOP...",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQE...\n-----END PUBLIC KEY-----",
  "integrity": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

## Step 6: Distribute to Client

### Package for Distribution

```bash
# Create distribution package
mkdir my-api-delivery
cp dist/my-api-bundle.zip my-api-delivery/
cp acme-license.key my-api-delivery/
cp DELIVERY-README.md my-api-delivery/

# Create delivery archive
tar czf my-api-delivery.tar.gz my-api-delivery/
```

### DELIVERY-README.md

```markdown
# My API - Secure Distribution

Thank you for your purchase!

## Quick Start

1. Extract the bundle:
   ```bash
   unzip my-api-bundle.zip
   cd my-api-bundle
   ```

2. Place your license file:
   ```bash
   cp ../acme-license.key ./license.key
   ```

3. Run the application:
   ```bash
   ./runtime/run.sh
   ```

4. Test the API:
   ```bash
   curl -H "X-API-Key: your-key" http://localhost:5000/api/users
   ```

## System Requirements

- Docker 20.10+
- Docker Compose 1.29+
- 2GB RAM minimum
- 5GB disk space

## Support

Contact: support@mycompany.com
License expires: 2025-12-31
```

---

## Step 7: Client Installation

### Client Workflow

```bash
# Extract delivery
tar xzf my-api-delivery.tar.gz
cd my-api-delivery

# Extract bundle
unzip my-api-bundle.zip
cd my-api-bundle

# Place license
cp ../acme-license.key ./license.key

# Run application
./runtime/run.sh
```

**Output on Client Machine:**
```
==================================================
  ShipLock Secure Runtime
==================================================

[0/4] Verifying bundle integrity...
Integrity verification passed

[1/4] Verifying license...
License verified successfully

[2/4] Loading Docker images...
  Loading my-api_api_latest.tar.gz...
All images loaded successfully!

[3/4] Starting services...
Creating network "my-api_default" with the default driver
Creating my-api_api_1 ... done

[4/4] Checking service status...
   Name                  Command               State    Ports
────────────────────────────────────────────────────────────
my-api_api_1   /app/entrypoint.sh python  ...   Up      0.0.0.0:5000->5000/tcp

==================================================
  Application started successfully!
==================================================

To view logs: docker-compose logs -f
To stop: docker-compose down
```

---

## Step 8: Verify Protection

### Check 1: No Source Code in Container

```bash
# Enter running container
docker exec -it my-api_api_1 bash

# Try to find Python source files
find / -name "*.py" -type f 2>/dev/null | grep -v "site-packages"

# Output: (empty or only system files)
# Source code is NOT accessible!
```

### Check 2: Verify License Binding

```bash
# Try to copy license to another machine
scp license.key other-machine:~/

# On other machine
./runtime/run.sh

# Output:
# ERROR: License not valid for this machine
# Expected: abc123def456...
# Actual:   xyz789uvw012...
```

### Check 3: Verify Expiration

```bash
# After December 31, 2025
./runtime/run.sh

# Output:
# ERROR: License expired
# Expired at: 2025-12-31T23:59:59
```

### Check 4: Verify Integrity Protection

```bash
# Tamper with a file
echo "hacked" >> runtime/run.sh

# Try to run
./runtime/run.sh

# Output:
# ERROR: File integrity check failed for runtime/run.sh
# Expected: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
# Actual:   1234567890abcdef...
# CRITICAL: Bundle integrity verification failed!
```

---

## Step 9: Client Operations

### View Logs

```bash
docker-compose logs -f api
```

### Stop Application

```bash
docker-compose down
```

### Update Environment Variables

```bash
# Edit .env file
nano .env

# Add:
API_KEY=production-secret-key

# Restart
docker-compose restart
```

### Health Check

```bash
# Application includes health check
docker-compose ps

# Shows health status:
# my-api_api_1   healthy   0.0.0.0:5000->5000/tcp
```

---

## Summary

### What We Protected

✅ **Source Code**
- app.py, models.py, utils.py - Completely removed
- Only bytecode in container
- Multi-stage build removes all source

✅ **Business Logic**
- Proprietary algorithms protected
- Cannot reverse engineer easily
- Obfuscated verification code

✅ **Distribution**
- License prevents unauthorized use
- Machine binding prevents sharing
- Integrity checks prevent tampering

### Security Guarantees

✅ **No Source Code**: Verified by container inspection
✅ **License Required**: Cannot run without valid license
✅ **Machine Bound**: License tied to specific machine
✅ **Expiration Enforced**: Automatic expiry on date
✅ **Tamper-Proof**: Integrity verification on startup
✅ **Obfuscated**: Verification code is protected

### Client Experience

✅ **Simple**: One command to run
✅ **Fast**: Loads in seconds
✅ **Reliable**: Offline validation
✅ **Clear Errors**: Helpful messages
✅ **Professional**: Production-quality bundle

---

## Advanced Scenarios

### Scenario 1: License Renewal

```bash
# Vendor generates new license with extended expiry
shiplock license generate \
  --product-id "MY-API-001" \
  --client "Acme Corporation" \
  --expires "2026-12-31" \
  --machine-bound \
  --output acme-license-2026.key

# Send to client
# Client replaces old license
cp acme-license-2026.key license.key

# Restart application
docker-compose restart
```

### Scenario 2: Feature Gates

```bash
# Generate license with features
shiplock license generate \
  --product-id "MY-API-001" \
  --client "Acme Corporation" \
  --expires "2025-12-31" \
  --machine-bound \
  --features '{"premium": true, "max_users": 100}' \
  --output acme-premium-license.key
```

### Scenario 3: Trial License

```bash
# 30-day trial
shiplock license generate \
  --product-id "MY-API-001" \
  --client "Trial User" \
  --expires "2024-12-31" \
  --machine-bound \
  --output trial-license.key
```

---

## Troubleshooting

### Problem: License Not Found

```
ERROR: License file not found
```

**Solution:**
```bash
# Ensure license.key is in bundle root
ls -la license.key

# If missing, copy it
cp /path/to/license.key ./
```

### Problem: License Invalid for Machine

```
ERROR: License not valid for this machine
```

**Solution:**
- License is machine-bound
- Request new license for this machine
- Contact vendor with machine fingerprint

### Problem: License Expired

```
ERROR: License validation failed
```

**Solution:**
- Check expiration date
- Request license renewal
- Contact vendor

### Problem: Integrity Check Failed

```
ERROR: Bundle integrity verification failed
```

**Solution:**
- Bundle has been modified
- Re-download from vendor
- Verify download integrity

---

## Conclusion

This example demonstrates:

1. ✅ **Complete source protection** - No source code accessible
2. ✅ **Strong licensing** - Cryptographic, machine-bound, time-limited
3. ✅ **Easy distribution** - Single ZIP file
4. ✅ **Simple client experience** - One command to run
5. ✅ **Production-ready** - Professional, secure, maintainable

ShipLock enables secure distribution of Docker products while protecting intellectual property and enforcing licensing terms.
