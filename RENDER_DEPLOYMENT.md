# Deploying PWD Management System to Render.com

## Overview

The system deploys as **4 services** on Render:

| Service | Type | Plan | Cost |
|---------|------|------|------|
| `pwd-backend` | Web Service (Django) | Free | $0 |
| `pwd-frontend` | Static Site (Vue 3) | Free | $0 |
| `pwd-db` | PostgreSQL | Free (90 days) | $0 |
| `pwd-redis` | Redis | Free | $0 |

> ⚠️ **Free tier note:** Web services sleep after 15 minutes of inactivity and take ~30s to wake up. Free PostgreSQL databases expire after 90 days. Upgrade to the Starter plan ($7/month) for production use with clients.

---

## Method A: Blueprint (Easiest — 1 click)

The `render.yaml` file in the repo root defines all 4 services automatically.

### Step 1 — Push to GitHub

```bash
# From the pwd_system/ folder
git init
git add .
git commit -m "Initial PWD system"
git branch -M main

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/pwd-system.git
git push -u origin main
```

### Step 2 — Connect to Render

1. Go to [render.com](https://render.com) → **Sign up / Log in**
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account → select `pwd-system` repo
4. Render reads `render.yaml` and shows a preview of all 4 services
5. Click **"Apply"**

Render will automatically:
- Create the PostgreSQL database
- Create the Redis instance
- Deploy the Django backend (runs `build.sh`)
- Build and deploy the Vue frontend (runs `npm run build`)

### Step 3 — Set the frontend API URL

After the backend finishes deploying, copy its URL (e.g. `pwd-backend.onrender.com`):

1. Go to `pwd-frontend` service → **Environment**
2. Add environment variable:
   - Key: `VITE_API_BASE_URL`
   - Value: `pwd-backend.onrender.com` (no `https://`)
3. Click **"Save Changes"** → frontend auto-redeploys

### Step 4 — Access the demo

- **Frontend:** `https://pwd-frontend.onrender.com`
- **Backend API:** `https://pwd-backend.onrender.com/api/`
- **Admin panel:** `https://pwd-backend.onrender.com/admin/`
- **API docs:** `https://pwd-backend.onrender.com/api/docs/`

**Default demo login:**
```
Email:    admin@pwdms.demo
Password: PWDdemo2024!
```

---

## Method B: Manual (step by step)

If you prefer to set each service up individually:

### 1. Create PostgreSQL Database

1. Render Dashboard → **New +** → **PostgreSQL**
2. Name: `pwd-db`
3. Plan: **Free**
4. Click **Create Database**
5. Copy the **"External Database URL"** — you'll need it shortly

### 2. Create Redis

1. Render Dashboard → **New +** → **Redis**
2. Name: `pwd-redis`
3. Plan: **Free**
4. Copy the **"Internal Redis URL"**

### 3. Deploy Django Backend

1. Render Dashboard → **New +** → **Web Service**
2. Connect your GitHub repo
3. Configure:

| Field | Value |
|-------|-------|
| **Name** | `pwd-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT --timeout 120` |
| **Plan** | Free |

4. Add these **Environment Variables**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Click **"Generate"** |
| `DEBUG` | `False` |
| `PYTHON_VERSION` | `3.11.0` |
| `ALLOWED_HOSTS` | `.onrender.com,localhost` |
| `DATABASE_URL` | *(paste External Database URL from step 1)* |
| `REDIS_URL` | *(paste Internal Redis URL from step 2)* |
| `CORS_ALLOWED_ORIGINS` | `https://pwd-frontend.onrender.com` |

5. Click **Create Web Service**

### 4. Deploy Vue Frontend

1. Render Dashboard → **New +** → **Static Site**
2. Connect your GitHub repo
3. Configure:

| Field | Value |
|-------|-------|
| **Name** | `pwd-frontend` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm ci && npm run build` |
| **Publish Directory** | `dist` |

4. Add **Rewrite Rule** (required for Vue Router SPA):
   - Source: `/*`
   - Destination: `/index.html`

5. Add **Environment Variable**:
   - `VITE_API_BASE_URL` = `pwd-backend.onrender.com`

6. Click **Create Static Site**

---

## Optional: Add Demo Data

After the backend is running, you can add sample PWD records via the Django shell:

1. Go to `pwd-backend` service → **Shell** tab
2. Run:

```bash
python manage.py shell
```

```python
from apps.pwds.models import PWD, DisabilityType, MedicalRecord
from apps.accounts.models import User
import datetime

admin = User.objects.get(email='admin@pwdms.demo')
dt = DisabilityType.objects.first()

# Create 3 sample records
for i in range(1, 4):
    p = PWD.objects.create(
        first_name=f'Sample{i}',
        last_name='Person',
        date_of_birth=datetime.date(1985, i, 15),
        gender='M' if i % 2 else 'F',
        marital_status='single',
        community='Demo Community',
        district='Demo District',
        region='Greater Accra',
        education_level='primary',
        employment_status='unemployed',
        registered_by=admin,
    )
    if dt:
        med = MedicalRecord.objects.create(
            pwd=p,
            disability_severity='moderate',
            disability_onset='acquired',
            recorded_by=admin,
        )
        med.disability_types.add(dt)

print("3 sample PWDs created!")
```

---

## Keeping the Free Tier Alive

Free web services sleep after 15 minutes of inactivity. To prevent this for demos:

**Option 1 — UptimeRobot (free)**
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add a new monitor:
   - Monitor type: **HTTP(s)**
   - URL: `https://pwd-backend.onrender.com/api/settings/`
   - Interval: **5 minutes**

**Option 2 — Cron-job.org (free)**
1. Sign up at [cron-job.org](https://cron-job.org)
2. Create a cron job that pings `https://pwd-backend.onrender.com/api/settings/` every 10 minutes

---

## Custom Domain (Optional)

1. Go to `pwd-frontend` service → **Settings** → **Custom Domains**
2. Add your domain (e.g. `pwd.yourassembly.gov.gh`)
3. Update your DNS: add a CNAME record pointing to `pwd-frontend.onrender.com`
4. Render automatically provisions an SSL certificate

---

## Upgrading for Production

When you're ready for real clients (not just demo), upgrade:

| Service | Upgrade to | Monthly cost |
|---------|-----------|-------------|
| Backend | Starter | $7/month |
| Database | Starter | $7/month |
| Redis | Starter | $10/month |

This gives you: no sleep, persistent storage, 1GB RAM, and database backups.

---

## Troubleshooting

**Build fails:**
- Check that `build.sh` has Unix line endings (not Windows `\r\n`)
- View logs in the Render dashboard under the **Logs** tab

**Frontend shows blank page / 404:**
- Confirm the Rewrite Rule `/* → /index.html` is set
- Make sure `VITE_API_BASE_URL` does NOT include `https://`

**API returns CORS error:**
- Check `CORS_ALLOWED_ORIGINS` in backend env vars matches your frontend URL exactly

**Database connection error:**
- Confirm `DATABASE_URL` is set to the **External** (not Internal) DB URL in manual setup
- With Blueprint, this is handled automatically

**Login not working:**
- Run the shell command above to check the superuser exists
- Password is case-sensitive: `PWDdemo2024!`
