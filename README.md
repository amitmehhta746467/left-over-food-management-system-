# LeftoverBite — Django Food Rescue API

A Django + Django REST Framework project inspired by the supplied food-delivery UI reference, adapted for leftover-food donation and rescue.

## Features

- Responsive community food-rescue homepage
- About page and live community overview
- Food donation listing with city and food-type filters
- Donor donation form
- NGO/receiver food request flow
- Donation, request and pickup REST APIs
- Statistics endpoint
- Django admin
- SQLite database
- CORS support for frontend/mobile clients

## Setup — Windows

```bat
cd leftover_food_django
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Website: http://127.0.0.1:8000/
- About: http://127.0.0.1:8000/about/
- Community overview: http://127.0.0.1:8000/overview/
- Available food: http://127.0.0.1:8000/donations/
- Donate food: http://127.0.0.1:8000/donate/
- Request food: http://127.0.0.1:8000/request-food/
- Register: http://127.0.0.1:8000/register/
- Log in: http://127.0.0.1:8000/login/
- API root: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/

## REST endpoints

- GET/POST `/api/donations/`
- GET/PATCH/DELETE `/api/donations/<id>/`
- GET/POST `/api/requests/`
- GET/PATCH/DELETE `/api/requests/<id>/`
- GET/POST `/api/pickups/`
- GET/PATCH/DELETE `/api/pickups/<id>/`
- GET `/api/stats/`
- GET `/api/nearby-donations/?city=Yamuna%20Nagar`

## Example JSON donation

```json
{
  "title": "50 Fresh Meal Boxes",
  "food_type": "meal",
  "quantity": 50,
  "description": "Fresh vegetarian meals",
  "pickup_address": "Model Town",
  "city": "Yamuna Nagar",
  "prepared_at": "2026-11-09T12:00:00+05:30",
  "safe_until": "2026-11-09T18:00:00+05:30",
  "status": "available"
}
```

For production, change `SECRET_KEY`, set `DEBUG=False`, configure allowed hosts, HTTPS, authentication and a production database.
