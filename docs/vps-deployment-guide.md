# 🌐 Universal Linux VPS Deployment & Hardening Guide
## Enterprise Production Blueprint (Cloud & Provider-Agnostic)

> **Purpose:** This guide walks developers and teams through deploying any Aegis Forge project (FastAPI, Express.js, or Laravel) to **ANY Linux VPS** with banking-grade network isolation, automated TLS/HTTPS (Let's Encrypt), and zero-port-leakage architecture.
>
> **100% Provider-Agnostic:** Whether you use **Hetzner, DigitalOcean, AWS Lightsail/EC2, Linode (Akamai), Vultr, Contabo, Biznet GIO, IDCloudHost, KilatVM**, or your own on-premise hardware, this procedure works identically.

---

## 🏗️ 1. Production Architecture Overview

In local development, database and cache ports (`5432`, `6379`) are often published to `localhost` for developer convenience. **In production, exposing database ports to the public internet is a critical security vulnerability.**

```
[ Public Internet ]
        │
        ▼ (Port 80 / 443 / 443-udp)
┌────────────────────────────────────────────────────────────────────────┐
│ VPS Host (UFW Firewall: Only Port 22, 80, 443 Open)                   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Docker Private Bridge Network (`internal-net`)                 │   │
│   │                                                                │   │
│   │   ┌───────────────┐        ┌─────────────┐                     │   │
│   │   │ Caddy Proxy   │ ─────▶ │ Backend API │                     │   │
│   │   │ (Auto-HTTPS)  │        │ (Port 8000) │                     │   │
│   │   └───────────────┘        └──────┬──────┘                     │   │
│   │                                   │                            │   │
│   │                    ┌──────────────┴──────────────┐             │   │
│   │                    ▼                             ▼             │   │
│   │           ┌─────────────────┐           ┌─────────────────┐    │   │
│   │           │ PostgreSQL 16   │           │ Redis 7 Cache   │    │   │
│   │           │ (NO HOST PORTS) │           │ (NO HOST PORTS) │    │   │
│   │           └─────────────────┘           └─────────────────┘    │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Security Principles Enforced:**
1. **Zero Public Port Leakage:** PostgreSQL and Redis are bound exclusively to the private Docker network (`internal-net`). Internet scanners cannot touch them.
2. **Automated SSL/TLS:** Caddy acts as reverse proxy, auto-generating and auto-renewing Let's Encrypt SSL/TLS certificates.
3. **Hardened Headers:** HSTS, X-Frame-Options: DENY, and strict CSP are injected at the edge.

---

## 🧰 2. VPS Sizing & Recommended OS

- **Recommended OS:** **Ubuntu 24.04 LTS** or **Ubuntu 22.04 LTS** (Debian 12 also fully supported).
- **Minimum Specs (MVP / Small API):**
  - 1 vCPU, 2 GB RAM, 20 GB SSD.
- **Recommended Production Specs:**
  - 2 vCPU, 4 GB RAM, 40+ GB NVMe SSD.
  *(A swapfile of 2GB–4GB is recommended to prevent OOM kills).*

---

## 🛡️ 3. Step-by-Step Server Preparation & Hardening

Log into your fresh VPS as `root`:
```bash
ssh root@<YOUR_VPS_IP>
```

### Step 3.1: Update System Packages
```bash
apt update && apt upgrade -y
```

### Step 3.2: Create a Dedicated Deployer User (Non-Root)
```bash
# Create deployer user
adduser deployer

# Grant sudo privileges
usermod -aG sudo deployer

# Copy SSH keys from root to deployer
mkdir -p /home/deployer/.ssh
cp /root/.ssh/authorized_keys /home/deployer/.ssh/
chown -R deployer:deployer /home/deployer/.ssh
chmod 700 /home/deployer/.ssh
chmod 600 /home/deployer/.ssh/authorized_keys
```

### Step 3.3: Harden SSH Daemon
Edit `/etc/ssh/sshd_config`:
```bash
sudo nano /etc/ssh/sshd_config
```
Ensure the following directives are set:
```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
```
Restart SSH service:
```bash
sudo systemctl restart ssh
```
*(Keep your current terminal open while opening a second terminal to verify `ssh deployer@<YOUR_VPS_IP>` connects successfully)*.

### Step 3.4: Configure Uncomplicated Firewall (UFW)
Strictly allow only SSH, HTTP, and HTTPS traffic:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 443/udp comment 'HTTP/3 QUIC'
sudo ufw enable
```
Check firewall status:
```bash
sudo ufw status verbose
```
*(Notice: Ports 5432, 6379, and 8000 are not open to the world)*.

### Step 3.5: Install Fail2ban (Brute-Force Protection)
```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
```

---

## 🐳 4. Install Modern Docker Engine & Compose

Install official Docker using the automated script:
```bash
curl -fsSL https://get.docker.com | sh

# Allow deployer user to run Docker without sudo
sudo usermod -aG docker deployer
newgrp docker
```
Verify installation:
```bash
docker --version
docker compose version
```

---

## 🌐 5. Configure Your Domain DNS

Before starting Caddy, map your domain name to your VPS Public IP at your DNS provider (Cloudflare, Namecheap, Route53, Niagahoster, etc.):

| Type | Name | Content / Target | TTL |
|---|---|---|---|
| **A** | `api` (or `@` for root) | `<YOUR_VPS_PUBLIC_IP>` | Auto / 300 |

*Verify DNS propagation from your terminal:*
```bash
dig +short api.yourdomain.com
# Should return your VPS Public IP
```

---

## 🚀 6. Deploy Your Project with Aegis Forge

Switch to your `deployer` user and clone/copy your project:
```bash
# Recommended deployment folder
sudo mkdir -p /var/www/app
sudo chown deployer:deployer /var/www/app
cd /var/www/app

# Option A: Clone from Git
git clone <YOUR_GIT_REPO_URL> .

# Option B: Or copy using rsync from your local machine
# rsync -avz --exclude 'node_modules' --exclude '.venv' ./ deployer@<YOUR_VPS_IP>:/var/www/app/
```

### Step 6.1: Setup Production Environment (`.env`)
```bash
cp .env.example .env
nano .env
```
Ensure production variables are configured securely:
```env
# Domain & SSL (Required by Caddy)
DOMAIN_NAME=api.yourdomain.com
ACME_EMAIL=admin@yourdomain.com

# Environment Flags
ENVIRONMENT=production
NODE_ENV=production
APP_ENV=production

# Database Credentials (use strong random password)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_super_secret_db_password_here
POSTGRES_DB=your_production_db

# Cryptographic Keys (Must be unique & random)
JWT_ACCESS_SECRET="<generate with openssl rand -base64 48>"
JWT_REFRESH_SECRET="<generate with openssl rand -base64 48>"
ENCRYPTION_MASTER_KEY="<generate with openssl rand -hex 32>"
```

### Step 6.2: Launch Production Stack
Launch services using the production compose file:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Step 6.3: Run Database Migrations
Depending on your chosen backend framework:
```bash
# For FastAPI:
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# For Express.js:
# Migrations run automatically on startup or via your migration runner

# For Laravel:
docker compose -f docker-compose.prod.yml exec api php artisan migrate --force
```

---

## ✅ 7. Verification & Health Check

Test that your site is live with a valid SSL certificate:
```bash
# 1. Test HTTPS response
curl -I https://api.yourdomain.com/health/live

# Expected Response:
# HTTP/2 200
# strict-transport-security: max-age=63072000; includeSubDomains; preload
# x-frame-options: DENY
# x-content-type-options: nosniff

# 2. Verify that Database and Redis ports are NOT reachable from outside
nmap -p 5432,6379,8000 <YOUR_VPS_PUBLIC_IP>
# All three ports MUST show as 'filtered' or 'closed'
```

---

## 🔄 8. Zero-Downtime Updates (Deploying Code Changes)

When you push new code to your Git repository, update the server cleanly:

```bash
cd /var/www/app

# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart API without stopping database or cache
docker compose -f docker-compose.prod.yml up -d --build --no-deps api

# 3. Run any new database migrations
docker compose -f docker-compose.prod.yml exec api <migration-command>

# 4. Clean up dangling images to save disk space
docker image prune -f
```

---

## 💾 9. Automated Database Backup Routine

Never deploy to production without an automated backup. Set up a daily encrypted database dump:

Create `/home/deployer/backup-db.sh`:
```bash
#!/usr/bin/env bash
set -e

BACKUP_DIR="/var/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME=$(docker compose -f /var/www/app/docker-compose.prod.yml ps -q db)

mkdir -p "$BACKUP_DIR"

# Dump database to compressed archive
docker exec -t "$CONTAINER_NAME" pg_dumpall -U postgres | gzip > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Retain only last 14 days of backups
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +14 -delete

echo "✅ Backup successfully created at $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
```
Make it executable and add to crontab:
```bash
chmod +x /home/deployer/backup-db.sh
# Run every night at 02:00 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/deployer/backup-db.sh >> /var/log/db-backup.log 2>&1") | crontab -
```

---

## 🎯 Summary Checklist for Production

- [ ] Linux packages updated & deployer user created.
- [ ] SSH password authentication disabled.
- [ ] UFW firewall active: only ports 22, 80, 443 permitted.
- [ ] Database and Redis have **zero host ports exposed**.
- [ ] Caddy auto-provisions SSL for `DOMAIN_NAME`.
- [ ] Security headers confirmed (HSTS, DENY, nosniff).
- [ ] Nightly backup cronjob enabled.
