# Render deployment

## Render commands

- Build command: `bash build.sh`
- Start command: `gunicorn campus_store.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- Health check: `/health/`

## Required environment variables

```text
DJANGO_SECRET_KEY
DEBUG
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS

MYSQL_HOST
MYSQL_PORT
MYSQL_USER
MYSQL_PASSWORD
MYSQL_NAME
MYSQL_AUTH_NAME

POSTGRES_HOST
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_NAME

MONGO_URI
MONGO_DB_NAME
MONGO_COLLECTION
```

Use Railway's **public TCP host and port** for `MYSQL_HOST` and `MYSQL_PORT`.
Do not use `localhost`, `127.0.0.1`, or a `*.railway.internal` hostname from Render.

Add Render's published outbound CIDR ranges to MongoDB Atlas Network Access, and ensure the
Atlas user has `readWrite` access to the configured activity database.

Book covers uploaded through Django Admin are stored on Render's ephemeral filesystem. Use
external object storage before relying on uploaded media in production.

## URLs to test

- `/`
- `/login/`
- `/signup/`
- `/admin/`
- `/health/`

## Post-deployment checklist

- Log in and log out successfully.
- Confirm Django Admin can add/edit a catalog book.
- Confirm catalog cards, static CSS, and book-detail pages load.
- Submit a review and place an order.
- Open a book detail page, return home, and confirm Recently Viewed is populated from MongoDB.
