# LuxePOS — Django REST API Backend

A full-featured Point of Sale (POS) backend built with Django REST Framework. Supports multi-store retail operations including product management, order processing, saved carts, notifications, and a dashboard analytics API.

## Features

- **JWT Authentication** — register, login, token refresh via `djangorestframework-simplejwt`
- **Role-based access** — `customer`, `staff`, and `admin` roles
- **Store & Products** — categories and products with variants, stock status, badges, ratings across store types (Accessories, Clothing, Jewelry)
- **Orders** — full order lifecycle (processing → shipped → delivered), order timeline tracking, POS sale flag
- **Saved Cart** — per-user persistent cart stored as JSON
- **Notifications** — in-app notification model with user preferences
- **Dashboard API** — aggregated sales and analytics endpoints
- **API Docs** — auto-generated OpenAPI schema via `drf-spectacular`
- **Deployment-ready** — WhiteNoise static file serving, PythonAnywhere WSGI config included

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.x + Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | MySQL (production) / SQLite (dev) |
| Docs | drf-spectacular (OpenAPI 3) |
| Static files | WhiteNoise |
| Deployment | PythonAnywhere |

## Project Structure

```
apps/
├── accounts/       # Custom User model, auth views, notification preferences
├── store/          # Category & Product models, seed command
├── orders/         # Order, OrderItem, OrderTimeline, SavedCart
├── pos/            # POS-specific views and logic
├── notifications/  # Notification model and preferences
└── dashboard/      # Analytics and dashboard API

config/
└── settings/
    ├── base.py
    ├── dev.py
    ├── prod.py
    └── pythonanywhere.py
```

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL (for production) or SQLite (for development)

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/POS-Django.git
cd POS-Django

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your values (see Environment Variables below)

# 5. Run migrations
python manage.py migrate

# 6. (Optional) Seed sample data
python manage.py seed

# 7. Create a superuser
python manage.py createsuperuser

# 8. Start the dev server
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `luxepos` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | *(leave blank for SQLite dev)* |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |

For PythonAnywhere deployment, see `.env.pythonanywhere.example`.

## API Documentation

Once the server is running, interactive API docs are available at:

- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register a new user |
| POST | `/api/accounts/login/` | Login and get JWT tokens |
| POST | `/api/accounts/token/refresh/` | Refresh access token |
| GET | `/api/store/products/` | List all products |
| GET | `/api/store/categories/` | List all categories |
| GET/POST | `/api/orders/` | List or create orders |
| GET | `/api/orders/<id>/` | Order detail |
| GET | `/api/dashboard/` | Dashboard analytics |
| GET | `/api/notifications/` | User notifications |

## Deployment (PythonAnywhere)

1. Upload the project or clone from GitHub in a PythonAnywhere console
2. Create a virtual environment and install requirements
3. Copy `.env.pythonanywhere.example` to `.env` and fill in your MySQL credentials
4. Set the WSGI file to point to `pythonanywhere_wsgi.py`
5. Run `python manage.py migrate --settings=config.settings.pythonanywhere`
6. Collect static files: `python manage.py collectstatic --settings=config.settings.pythonanywhere`

## License

MIT
