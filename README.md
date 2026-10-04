#  Asset Management System

A production-style asset management application built with Django and Django REST Framework. It includes:

- Web dashboard and asset management using class-based views
- REST API for mobile apps and integrations
- Asset lifecycle tracking: purchase, assignment, maintenance, condition, and status
- Search, filtering, and reporting support
- JWT-based authentication for API clients

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- djangorestframework-simplejwt

## Project Features

- Asset catalog with categories and locations
- status tracking (available, assigned, under maintenance, retired, disposed)
- maintenance scheduling and history
- assignment tracking for users and departments
- dashboard with KPI summaries
- API endpoints for mobile clients

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open:

- Web app: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API docs: http://127.0.0.1:8000/api/

## Default API Auth

Use JWT tokens:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

## Core App Layout

- `assets/` — web UI and core asset logic
- `api/` — REST API serializers, viewsets, and endpoints
- `asset_management/` — project settings and routing

## Notes

This application is intentionally designed to be extensible for industrial, facilities, and fleet use cases.
