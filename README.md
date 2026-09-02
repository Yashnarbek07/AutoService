# AutoService

AutoService is a vehicle maintenance and service-booking platform built with Django and Django REST Framework.

Users can register vehicles, browse service centres, book automotive services, receive real-time status notifications, and get scheduled booking reminders.

## Features

- JWT registration and authentication
- User profile management
- Vehicle management
- Service centres and service categories
- Automotive service management
- Mechanic profiles
- Service booking system
- Booking status workflow
- Role-based permissions
- Real-time WebSocket notifications
- Celery booking reminders
- Swagger/OpenAPI documentation
- Django HTML pages
- PostgreSQL database
- Docker Compose configuration
- API and permission tests

## Technology Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Celery Beat
- Django Channels
- Daphne
- JWT authentication
- drf-spectacular
- Docker
- Docker Compose

## Main Applications

- `accounts` — authentication and user profiles
- `vehicles` — customer vehicles
- `services` — service centres, mechanics and automotive services
- `bookings` — service booking and status management
- `notifications` — reminders and real-time notifications
- `webapp` — Django HTML interface

## API Documentation

After starting the project, Swagger documentation is available at:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/register/` | Register a new user |
| POST | `/api/accounts/login/` | Obtain JWT tokens |
| POST | `/api/accounts/token/refresh/` | Refresh access token |
| GET/PATCH | `/api/accounts/profile/` | View or update profile |
| GET/POST | `/api/vehicles/` | List or create vehicles |
| GET/POST | `/api/centres/` | List or create service centres |
| GET/POST | `/api/categories/` | List or create categories |
| GET/POST | `/api/services/` | List or create automotive services |
| GET/POST | `/api/mechanics/` | List or create mechanics |
| GET/POST | `/api/bookings/` | List or create bookings |
| PATCH | `/api/bookings/{id}/change-status/` | Change booking status |
| GET | `/api/notifications/` | List user notifications |

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

Do not commit the real `.env` file to GitHub.

## Running with Docker

Build and start all services:

```bash
docker compose up --build
```

Start containers in the background:

```bash
docker compose up -d
```

Stop all containers:

```bash
docker compose down
```

Create an administrator:

```bash
docker compose exec web python manage.py createsuperuser
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Running Locally

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

## Running Tests

Run all tests inside Docker:

```bash
docker compose exec web python manage.py test
```

Run authentication tests:

```bash
docker compose exec web python manage.py test accounts
```

Run booking and permission tests:

```bash
docker compose exec web python manage.py test bookings
```

## Booking Workflow

A booking can move through the following statuses:

```text
PENDING → ACCEPTED → IN_PROGRESS → COMPLETED
```

It may also be:

```text
REJECTED
CANCELLED
```

Only an authorised service-centre owner or staff member can manage the booking status. An accepted booking must have an assigned mechanic.

## Background Tasks

Celery processes background jobs, while Redis works as the message broker.

Celery Beat manages scheduled tasks. Booking reminders can be scheduled before the selected appointment time.

## Real-Time Notifications

Django Channels and Daphne provide WebSocket support. When a booking status changes, the client receives a real-time notification.

## Author

**Yashnarbek Akmalov**

- GitHub: [Yashnarbek07](https://github.com/Yashnarbek07)