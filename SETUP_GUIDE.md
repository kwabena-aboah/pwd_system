# PWD Management System — Complete Setup Guide

## System Overview

A full-stack **Persons With Disability (PWD) Management System** built for District Assemblies in Ghana with:

- 🏛️ **Django 4.2 + DRF** — REST API backend
- ⚡ **Vue 3 + Bootstrap 5** — Progressive Web App frontend
- 📴 **Offline-first** — Service Worker + IndexedDB queue for poor connectivity
- 🤖 **AI Analysis** — GPT-4o-mini risk scoring and recommendations
- 📊 **Charts** — Chart.js dashboards for decision-making
- 📖 **Album** — PDF & PowerPoint export with branding
- 🔔 **Real-time Notifications** — Django Channels WebSockets
- 🔍 **Audit Trail** — Complete system audit log
- ⚙️ **Custom Branding** — Name, logo, colors per District Assembly

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (for WebSockets + Celery)
- Git

---

## 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations accounts pwds benefits complaints settings_app notifications
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data.json

# Start development server
python manage.py runserver
```

### Backend .env file:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Database (leave empty for SQLite)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# OpenAI (for AI features)
OPENAI_API_KEY=sk-your-key-here
```

---

## 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The frontend will be available at **http://localhost:5173**

---

## 3. Redis & Celery (for notifications & background tasks)

```bash
# Start Redis
redis-server

# In a new terminal, start Celery worker
cd backend
celery -A config worker --loglevel=info

# Start Celery beat (scheduled tasks)
celery -A config beat --loglevel=info
```

---

## 4. Production Deployment

### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve Vue build
    location / {
        root /var/www/pwd-system/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSockets
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Media files
    location /media/ {
        alias /var/www/pwd-system/media/;
    }
}
```

### Gunicorn + Daphne:
```bash
# WSGI (standard HTTP)
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

# ASGI (WebSockets support)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

---

## 5. Default Login

After running `createsuperuser`, login at:
- URL: `http://localhost:5173/login`
- Use the email and password you set

---

## 6. User Roles

| Role | Permissions |
|------|-------------|
| Super Admin | Full access, settings, user management |
| District Officer | Edit PWDs, approve benefits |
| Data Entry Officer | Create/edit PWD records |
| Social Worker | Edit PWDs, manage complaints |
| NGO Partner | View own district data |
| Government Officer | View own district data |
| Auditor | Read-only + audit log access |
| Viewer | Read-only access |

---

## 7. Key Features

### PWD Records
- Full personal, contact, socioeconomic & caregiver data
- Unique registration number (PWD-YYYY-NNNNN)
- Photo upload
- Medical records with disability types and severity
- Document attachments

### AI Analysis (requires OpenAI API key)
- Vulnerability risk score (0-100)
- Risk labels: Low / Medium / High / Critical
- Profile summary
- Intervention recommendations

### Album
- Visual grid of all registered PWDs
- Filter by district
- Export to **PDF** (jsPDF + autoTable)
- Export to **PowerPoint** (PptxGenJS)
- Print-ready layout with DA branding

### Benefits Tracking
- Development partner registry (NGOs, Gov, International)
- Benefit programme management
- Allocation workflow: Pending → Approved → Disbursed
- GHS value tracking and reporting

### Complaints
- Complaint logging with priority levels
- Assignment to social workers
- Resolution tracking with notes
- Statistics dashboard

### Offline Mode (PWA)
- Full offline browsing of cached data
- Offline form submissions queued in IndexedDB
- Auto-syncs when connectivity is restored
- Works as installable app on mobile/desktop

### Settings (Super Admin only)
- System name & short name
- Logo upload (primary + secondary)
- Color scheme (primary, secondary, accent)
- Pre-built color themes including "Ghana Gold"
- Album layout configuration
- Contact information

---

## 8. API Documentation

Django REST Framework Browsable API: `http://localhost:8000/api/`
Swagger UI: `http://localhost:8000/api/docs/`
Admin Panel: `http://localhost:8000/admin/`

---

## 9. Project Structure

```
pwd_system/
├── backend/
│   ├── apps/
│   │   ├── accounts/        # Custom User model + JWT auth
│   │   ├── pwds/            # PWD records + medical
│   │   ├── benefits/        # Partners, benefits, allocations
│   │   ├── complaints/      # Complaints + grievances
│   │   ├── notifications/   # WebSocket notifications
│   │   ├── reports/         # Analytics API
│   │   ├── settings_app/    # System settings + branding
│   │   └── audit/           # Audit log (django-auditlog)
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py          # WebSocket support
│   │   └── wsgi.py
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/
    │   │   ├── pwds/        # PWD list, detail, form
    │   │   ├── benefits/    # Partners, benefits, allocations
    │   │   ├── complaints/  # Complaints list & detail
    │   │   ├── Dashboard, Album, Reports, Audit,
    │   │   │   Users, Settings, Notifications
    │   ├── components/      # KpiCard, NavItem, InfoCard, InfoRow
    │   ├── stores/          # Pinia: auth, settings, offline
    │   ├── services/api.js  # Axios with JWT + auto-refresh
    │   ├── layouts/         # AppLayout with sidebar
    │   └── router/          # Protected routes
    ├── public/
    │   └── manifest.json    # PWA manifest
    ├── vite.config.js       # PWA + proxy config
    └── package.json
```

---

## 10. Support & Customization

The system is fully customizable:
- **Colors**: Via Settings page (Super Admin)
- **Branding**: Upload your District Assembly logo
- **Album**: Configure what fields appear in the PWD directory
- **Themes**: 7 built-in color themes including Ghana Gold

For technical support, refer to:
- Django docs: https://docs.djangoproject.com/
- Vue 3 docs: https://vuejs.org/
- DRF docs: https://www.django-rest-framework.org/
