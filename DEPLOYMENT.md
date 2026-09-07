# CampyTeq — Production Deployment & Operations Runbook

This document details the production deployment, scaling, security hardening, and maintenance procedures for the **CampyTeq** multi-tenant higher education digital ecosystem.

---

## Architecture Overview

```
                          [ Internet Traffic ]
                                   │
                                   ▼
                    [ Port 80 / 443 — Nginx Proxy ]
                      (Rate Limiting & SSL / TLS)
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   [ Next.js Frontend ]                     [ Gunicorn WSGI Backend ]
     (Node 20 Cluster)                        (Django 5 Multi-Worker)
       (Port 3000)                                  (Port 8000)
                                                        │
                         ┌──────────────────────────────┴──────────────┐
                         ▼                                             ▼
             [ PostgreSQL 16 Alpine ]                       [ Redis 7 Alpine ]
              (Multi-Tenant Schema)                         (Cache & Sessions)
```

---

## 1. System Requirements

| Resource | Minimum (Small College: < 2,000 users) | Recommended (Multi-Campus: > 10,000 users) |
|---|---|---|
| **CPU** | 4 vCPU | 8+ vCPU |
| **RAM** | 8 GB | 16–32 GB |
| **Storage** | 80 GB SSD (NVMe preferred) | 250+ GB NVMe SSD |
| **OS** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 24.04 LTS |
| **Container Engine** | Docker 24+ & Docker Compose v2 | Docker Engine with Swarm or Kubernetes |

---

## 2. Production Deployment Steps

### Step 1: Clone Codebase and Configure Environment
```bash
git clone https://github.com/your-org/campyteq.git /opt/campyteq
cd /opt/campyteq

# Copy and edit production environment variables
cp .env.production.example .env.production
nano .env.production
```

Ensure the following variables are customized:
- `SECRET_KEY`: Generate a 50-character random key (`openssl rand -base64 42`)
- `POSTGRES_PASSWORD`: Use a strong, unique database password
- `ALLOWED_HOSTS`: Domain names of the college (e.g. `campyteq.edu,api.campyteq.edu`)
- `CORS_ALLOWED_ORIGINS`: Allowed web client origins (`https://campyteq.edu`)

### Step 2: Build and Launch Containers
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Step 3: Verify Container Health
```bash
docker compose -f docker-compose.prod.yml ps
```
Expected status:
- `campyteq_prod_postgres` (healthy)
- `campyteq_prod_redis` (healthy)
- `campyteq_prod_backend` (running)
- `campyteq_prod_frontend` (running)
- `campyteq_prod_nginx` (running, ports 80/443 exposed)

### Step 4: SSL/TLS Provisioning with Let's Encrypt
To enable HTTPS with automatic certificate renewal:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d campyteq.edu -d api.campyteq.edu
```

---

## 3. Database Backup & Disaster Recovery

### Automated Nightly Backup Script
Save to `/opt/campyteq/scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/campyteq"
DATE=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

docker exec campyteq_prod_postgres pg_dump -U campyteq_user campyteq_db | gzip > "$BACKUP_DIR/campyteq_backup_$DATE.sql.gz"

# Retain backups for 14 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +14 -delete
```

Make executable and register in cron:
```bash
chmod +x /opt/campyteq/scripts/backup_db.sh
crontab -e
# Add: 0 2 * * * /opt/campyteq/scripts/backup_db.sh
```

### Restoring a Backup
```bash
gunzip -c /var/backups/campyteq/campyteq_backup_20260906.sql.gz | docker exec -i campyteq_prod_postgres psql -U campyteq_user -d campyteq_db
```

---

## 4. Mobile Application Build & Distribution (Expo / EAS)

The student mobile application located in `mobile/` is built using Expo:

### Local Simulator Testing
```bash
cd mobile
npm install
npx expo start
```

### Production Binary Compilation (EAS Build)
```bash
# Install EAS CLI
npm install -g eas-cli
eas login

# Configure project
eas build:configure

# Build Android APK / AAB
eas build --platform android --profile production

# Build iOS IPA
eas build --platform ios --profile production
```

---

## 5. Security & Compliance Checklist

- [x] Multi-tenant isolation verified with automated regression tests (all queries scoped to tenant model).
- [x] Zero continuous student GPS tracking in mobile app (biometric presence recorded solely through authorized campus CCTV zones).
- [x] Ethical AI guardrail: academic risk predictions are strictly advisory decision support without automated punitive penalties.
- [x] Gunicorn multi-worker WSGI configuration with request timeout safeguards.
- [x] Rate limiting configured on Nginx reverse proxy (30 req/s for general API; 5 req/s for token auth).
- [x] Strict JWT authentication with token expiry and rotation.
- [x] Sensitive personal data (biometric facial embeddings, payslips) protected under tenant-specific RBAC roles.
