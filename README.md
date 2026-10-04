# Asset Management System

A complete Django asset management app with web dashboard and mobile-ready REST API.

Features:
- Asset catalog with categories and locations
- Assignment tracking and maintenance history
- Dashboard with KPI summary
- Django class-based views for the web UI
- Django REST Framework endpoints for a mobile app
- JWT authentication for API clients
- Seed data and test coverage for core models

## Tech Stack
- Python 3.11+
- Django 5.x
- Django REST Framework
- djangorestframework-simplejwt

## Local Setup

```bash
cd asset-management-system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_assets
python manage.py runserver
```

## Access Points
- Web app: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/
- JWT token endpoint: http://127.0.0.1:8000/api/auth/token/

## Notes
This project is intentionally structured for industrial asset tracking operations such as facilities management, fleet oversight, production support, and plant maintenance.
