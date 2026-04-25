# PWD Management System — Full Stack Blueprint

## Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Vue 3 (Composition API) + Bootstrap 5
- **DB**: PostgreSQL (prod) / SQLite (dev)
- **PWA**: Service Worker + Workbox
- **AI**: OpenAI API integration (summaries, risk flags)
- **Export**: WeasyPrint (PDF), python-pptx (PowerPoint)
- **Auth**: JWT (SimpleJWT)

## Project Structure
```
pwd_system/
├── backend/
│   ├── config/                  # Django settings
│   ├── apps/
│   │   ├── accounts/            # Users, roles, auth
│   │   ├── pwds/                # PWD personal & medical records
│   │   ├── benefits/            # Benefits from NGOs/Gov
│   │   ├── complaints/          # Complaints & grievances
│   │   ├── audit/               # Audit trail
│   │   ├── notifications/       # In-app & email notifications
│   │   ├── reports/             # Reports & analytics
│   │   └── settings_app/        # System settings (name, logo, colors)
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── public/
    │   ├── manifest.json        # PWA manifest
    │   └── sw.js                # Service worker
    ├── src/
    │   ├── views/
    │   ├── components/
    │   ├── stores/              # Pinia stores
    │   ├── composables/
    │   └── router/
    └── package.json
```
