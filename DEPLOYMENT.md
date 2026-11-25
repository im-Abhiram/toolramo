# RAMONET 2.0 — PythonAnywhere WSGI Production Deployment Guide

This guide provides complete, production-tested instructions for deploying and updating **RAMONET** on PythonAnywhere under the account **`ramonet`**.

- **Production Domain:** `https://ramonet.pythonanywhere.com`
- **Application Directory:** `/home/ramonet/ramonet`
- **Virtualenv Directory:** `/home/ramonet/.virtualenvs/ramonet-env`
- **WSGI Configuration File:** `/var/www/ramonet_pythonanywhere_com_wsgi.py`
- **GitHub Repository:** `https://github.com/im-Abhiram/toolramo.git`

---

## ⚡ FAST UPDATE: How to Update Your Already Deployed App on PythonAnywhere

If you have already deployed RAMONET on PythonAnywhere, updating with the latest features (**Gemini AI Copilot**, **empty-canvas Network Designer with Device Web GUI default**, **Space Grotesk + JetBrains Mono UI**, and security fixes) takes about 30 seconds:

1. Open your **Bash console** on PythonAnywhere ([pythonanywhere.com/user/ramonet/consoles/](https://www.pythonanywhere.com/user/ramonet/consoles/)).
2. Run this single copy-paste update command (or follow the step-by-step commands below):

```bash
cd /home/ramonet/ramonet && workon ramonet-env && git checkout -- db.sqlite3 && git pull origin main && pip install -r requirements.txt && python manage.py migrate && python manage.py seed_data && python manage.py seed_academy && python manage.py collectstatic --noinput && touch /var/www/ramonet_pythonanywhere_com_wsgi.py
```

Step-by-step equivalent:

```bash
# 1. Go to project directory
cd /home/ramonet/ramonet

# 2. Activate virtualenv
workon ramonet-env

# 3. Discard local SQLite runtime changes to avoid merge conflict, then pull latest code
git checkout -- db.sqlite3
git pull origin main

# (If git pull still reports conflicts on any local file, simply run:)
# git stash && git pull origin main

# 4. Install any package requirements
pip install -r requirements.txt

# 5. Apply database migrations
python manage.py migrate

# 6. Re-seed device library, command reference & Academy courses (safe, skips existing)
python manage.py seed_data
python manage.py seed_academy

# 7. Collect updated static assets (CSS, JS, device SVGs, AI chatbot scripts)
python manage.py collectstatic --noinput

# 8. Reload your web app instantly:
touch /var/www/ramonet_pythonanywhere_com_wsgi.py
```

*Or go to the **Web** tab in PythonAnywhere and click the green **Reload ramonet.pythonanywhere.com** button.*

### One-Time Gemini AI Chatbot Secret Setup on PythonAnywhere
Because `.env` is excluded from git for security, configure `GEMINI_API_KEY` once on PythonAnywhere (either in `.env` inside `/home/ramonet/ramonet/` or inside your WSGI file):

```bash
cat << 'EOF' > /home/ramonet/ramonet/.env
GEMINI_API_KEY=your-gemini-api-key-here
EOF
chmod 600 /home/ramonet/ramonet/.env
touch /var/www/ramonet_pythonanywhere_com_wsgi.py
```

> **Note for PythonAnywhere Free Accounts:** Free PythonAnywhere accounts restrict outbound internet access to an official allowlist (`generativelanguage.googleapis.com` requires either requesting allowlist approval on the PythonAnywhere Forums or using a paid/Hacker account). If outbound access is restricted or the upstream API is unavailable, RAMONET AI automatically degrades gracefully to its built-in local knowledgebase without throwing errors.

### Creating Your Administrator Account (No Default Passwords):
To create your personal admin account, simply run in the Bash console:
```bash
python manage.py createsuperuser
```
Follow the prompt to type your chosen username, email, and password.

---

## 1. Architecture & Platform Prerequisites

- PythonAnywhere account username: **`ramonet`**
- Python version: **Python 3.10 – 3.13** (use **Python 3.10+**; note Django 6.x requires Python 3.12+, while Django 5.x supports Python 3.10+)
- Storage footprint: Ultra-lightweight (~620 KB SQLite database, self-hosted assets + Python stdlib Gemini client) — well within PythonAnywhere's 512 MB free tier quota.
- Client storage: Heavy topologies and simulation states reside in browser IndexedDB.

---

## 2. Step 1: Open a Bash Console on PythonAnywhere

1. Log into your dashboard at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Consoles** tab.
3. Click on **Bash** to open a new terminal session in `/home/ramonet`.

---

## 3. Step 2: Set Up Virtual Environment

In the Bash terminal, run:

```bash
# Create a dedicated virtualenv with Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 ramonet-env

# Verify the virtual environment is active (prompt shows (ramonet-env))
which python
python --version
```

*(If returning to an existing session in the future, activate it with `workon ramonet-env`)*

---

## 4. Step 3: Clone the GitHub Repository

Clone the repository into `/home/ramonet/ramonet`:

```bash
cd /home/ramonet

# Clone repo into a folder named 'ramonet'
git clone https://github.com/im-Abhiram/toolramo.git ramonet

# Change to project root
cd /home/ramonet/ramonet
```

---

## 5. Step 4: Install Dependencies

With `(ramonet-env)` active:

```bash
cd /home/ramonet/ramonet
pip install --upgrade pip
pip install -r requirements.txt
```

*RAMONET uses only `Django>=5.0,<6.1` and `djangorestframework>=3.14,<4.0`, keeping the footprint minimal and fast (even the Gemini AI client uses Python's standard library).*

---

## 6. Step 5: Run Database Migrations & Seed Initial Data

Initialize the SQLite database schema and populate the device library, command syntax, learning center, and Academy courses:

```bash
cd /home/ramonet/ramonet

# 1. Apply database migrations
python manage.py migrate

# 2. Seed device models, command reference, templates & learning topics
python manage.py seed_data

# 3. Seed 14 RAMONET Academy courses and 27 device practical guides
python manage.py seed_academy
```

This seeds:
- 10 Hardware Categories & 13+ Device Models
- 18 Prebuilt Production Network Templates
- 14 RAMONET Academy Courses & Practical Lab Scenarios
- 27 Device Configuration Guides
- Central CLI Command Library (Cisco IOS, Linux, Windows, MikroTik, iptables)

*Note: For security, no default admin credentials are created. Run `python manage.py createsuperuser` or register via the web UI.*

---

## 7. Step 6: Collect Production Static Assets

Compile all offline local CSS, JS, Bootstrap 5, FontAwesome, and Chart.js files into the production `staticfiles/` directory:

```bash
cd /home/ramonet/ramonet
python manage.py collectstatic --noinput
```

---

## 8. Step 7: Configure the Web App in PythonAnywhere Dashboard

1. Navigate to the **Web** tab in the PythonAnywhere top navigation.
2. If you haven't created a web app yet:
   - Click **Add a new web app**.
   - Domain will be: **`ramonet.pythonanywhere.com`**.
   - Choose **Manual configuration** (select **Python 3.10**).
3. If the web app already exists, configure the sections below:

### A. Paths Configuration
- **Source code:** `/home/ramonet/ramonet`
- **Working directory:** `/home/ramonet/ramonet`

### B. Virtualenv Configuration
In the **Virtualenv** section:
- Path: `/home/ramonet/.virtualenvs/ramonet-env`

### C. Static Files Mapping
In the **Static files** table, add the following URL-to-Directory mapping:

| URL | Directory |
| :--- | :--- |
| `/static/` | `/home/ramonet/ramonet/staticfiles` |

*(Leave the Media files section blank or set `/media/` to `/home/ramonet/ramonet/media`)*

### D. WSGI Configuration File
Click on the link for the **WSGI configuration file** (`/var/www/ramonet_pythonanywhere_com_wsgi.py`).

Replace the entire content of that file with the following production-hardened script:

```python
import os
import sys

# 1. Set application directory path
path = '/home/ramonet/ramonet'
if path not in sys.path:
    sys.path.insert(0, path)

# 2. Production Environment Settings & Security Hardening
os.environ['DJANGO_SETTINGS_MODULE'] = 'ramonet.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'ramonet.pythonanywhere.com,localhost,127.0.0.1'

# Generate a unique production secret key (or set a 64+ char random string)
os.environ['DJANGO_SECRET_KEY'] = 'replace-with-generated-random-64-char-secret-key'

# Enforce HTTPS redirect and HSTS
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['ENABLE_HSTS'] = 'True'

# Gemini AI Chatbot API Key (keep secret; never commit to git)
# os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key-here'

# 3. WSGI Application Handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Click the green **Save** button (top right).

---

## 9. Step 8: Reload and Verify the Web Application

1. Return to the **Web** tab.
2. Click the big green **Reload ramonet.pythonanywhere.com** button.
3. Open your browser and navigate to:
   **[https://ramonet.pythonanywhere.com](https://ramonet.pythonanywhere.com)**

### Verification Checklist:
- [ ] **Home Dashboard:** Page loads with dark theme, Space Grotesk typography, real-time clock, and interactive infrastructure map.
- [ ] **Network Designer:** Accessible at `/topology/designer/`, starts with a clean empty canvas, `+` anchor cabling connects devices, and **Device Web GUI** opens by default alongside CLI Terminal.
- [ ] **RAMONET AI Copilot:** Click **AI Help** in the top navigation bar or the bottom-right **Ask AI** button (`POST /api/knowledgebase/chat/`) and confirm Gemini AI or local KB responses work cleanly.
- [ ] **RAMONET Academy:** Accessible at `/academy/`, 14 courses listed.
- [ ] **Digital Twin Studio:** Accessible at `/projects/digital-twin/` (sandbox cloning and diff comparison).
- [ ] **Packet Capture & Analyzer:** Accessible at `/simulation/analyzer/` (OSI 7-layer Wireshark dissection).
- [ ] **What-If Simulation:** Accessible at `/simulation/what-if/` (failure injection and reachability metrics).
- [ ] **Network Automation Studio:** Accessible at `/configuration/automation/` (multi-device playbooks and dry-run).
- [ ] **Compliance Centre:** Accessible at `/configuration/compliance/` (CIS/DISA STIG benchmarks and scoring).
- [ ] **High Availability Lab:** Accessible at `/monitoring/ha-lab/` (STP, VRRP, LACP failover).
- [ ] **QoS Traffic Engineering:** Accessible at `/monitoring/qos/` (LLQ/CBWFQ vs tail drop).
- [ ] **Cable & Port Tracing:** Accessible at `/topology/cable-trace/` (TIA/EIA-568B pinout & run hops).
- [ ] **Capacity & Cost BOM:** Accessible at `/networktools/capacity-cost/` (BOM sizing and Capex estimation).
- [ ] **Incident Response Simulator:** Accessible at `/troubleshooting/incident-response/` (4-phase containment & post-mortem).
- [ ] **Security Operations Center:** Accessible at `/storage/security/` (log in as `admin`).
- [ ] **Static Assets:** CSS, fonts, and FontAwesome icons load without 404s.

---

## 10. Production Security Best Practices

1. **Change Default Passwords:**
   Once logged in, navigate to `/admin/` or `/accounts/settings/` and change the default `admin` and `student` passwords.
2. **Secret Key Rotation:**
   You can generate a cryptographically strong secret key anytime in the Bash console:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Paste the output into `os.environ['DJANGO_SECRET_KEY']` inside `/var/www/ramonet_pythonanywhere_com_wsgi.py`.
3. **Database Backups:**
   Download `/home/ramonet/ramonet/db.sqlite3` from the **Files** tab periodically or use the built-in JSON backup tool at `/projects/backups/`.

---

## 11. Troubleshooting Guide

| Issue | Root Cause | Exact Solution |
| :--- | :--- | :--- |
| **500 Internal Server Error** | Missing virtualenv or unmigrated tables | Check the Error Log linked at the bottom of the Web tab (`/var/log/ramonet.pythonanywhere.com.error.log`). Run `python manage.py migrate`. |
| **ImproperlyConfigured (Secret Key)** | Default key used with `DEBUG=False` | Ensure `os.environ['DJANGO_SECRET_KEY']` is set in the WSGI file. |
| **CSS/Icons Missing (Unstyled HTML)** | Static files mapping incorrect | Ensure `/static/` maps to `/home/ramonet/ramonet/staticfiles` and run `python manage.py collectstatic --noinput`. |
| **DisallowedHost Error** | Domain not in `ALLOWED_HOSTS` | Ensure `DJANGO_ALLOWED_HOSTS` in WSGI file includes `ramonet.pythonanywhere.com`. |
| **429 Too Many Requests on Login** | Rate limiter triggered (5 failed attempts) | Wait 5 minutes for the lockout window to expire, or restart the web app from the Web tab. |
| **Database Locked Error** | File permission conflict | Ensure `db.sqlite3` is writable (`chmod 664 /home/ramonet/ramonet/db.sqlite3`). |
| **AI Chatbot Uses `Local KB` Fallback** | Missing `GEMINI_API_KEY` or PythonAnywhere free-tier outbound block | Add `GEMINI_API_KEY=...` to `/home/ramonet/ramonet/.env` or WSGI file and reload. On PythonAnywhere free accounts, request `generativelanguage.googleapis.com` allowlist approval or upgrade to a paid tier. |
