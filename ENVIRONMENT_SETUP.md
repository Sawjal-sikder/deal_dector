# Environment Setup

This project uses environment variables for configuration. Follow these steps to set up your environment:

## 1. Copy the Example Environment File

```bash
cp .env.example .env
```

## 2. Configure Your Environment Variables

Edit the `.env` file and update the following variables with your actual values:

### Required Variables

- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Database Configuration

**For SQLite (Default):**

- `DATABASE_ENGINE`: `django.db.backends.sqlite3`
- `DATABASE_NAME`: `db.sqlite3`

**For PostgreSQL:**

- Uncomment the PostgreSQL variables and set:
  - `DATABASE_ENGINE`: `django.db.backends.postgresql`
  - `DATABASE_NAME`: Your database name
  - `DATABASE_USER`: Your database username
  - `DATABASE_PASSWORD`: Your database password
  - `DATABASE_HOST`: Database host (default: `127.0.0.1`)
  - `DATABASE_PORT`: Database port (default: `5432`)

### Email Configuration

- `EMAIL_HOST_USER`: Your email address
- `EMAIL_HOST_PASSWORD`: Your email app password (for Gmail, use App Password)

### Social Authentication

**Google OAuth:**

- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

**Apple OAuth (Optional):**

- `APPLE_CLIENT_ID`: Your Apple Service ID
- `APPLE_SECRET`: Your Apple private key
- `APPLE_KEY_ID`: Key ID from Apple Developer portal
- `APPLE_TEAM_ID`: Team ID from Apple Developer account

### Redis/Celery Configuration

- `CELERY_BROKER_URL`: Redis URL for Celery broker
- `CELERY_RESULT_BACKEND`: Redis URL for Celery results

## 3. Install Dependencies

Make sure you have all required packages installed:

```bash
pip install -r requirements.txt
```

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Security Notes

- Never commit your `.env` file to version control
- Use strong, unique secret keys for production
- Use App Passwords for email authentication (not your regular password)
- Keep your API keys and secrets secure

## Environment Variables Reference

| Variable               | Description            | Default                      | Required                   |
| ---------------------- | ---------------------- | ---------------------------- | -------------------------- |
| `SECRET_KEY`           | Django secret key      | -                            | Yes                        |
| `DEBUG`                | Debug mode             | `True`                       | No                         |
| `ALLOWED_HOSTS`        | Allowed hosts          | `localhost,127.0.0.1`        | No                         |
| `DATABASE_ENGINE`      | Database engine        | `django.db.backends.sqlite3` | No                         |
| `DATABASE_NAME`        | Database name          | `db.sqlite3`                 | No                         |
| `EMAIL_HOST_USER`      | Email username         | -                            | Yes (if using email)       |
| `EMAIL_HOST_PASSWORD`  | Email password         | -                            | Yes (if using email)       |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID | -                            | Yes (if using Google auth) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret    | -                            | Yes (if using Google auth) |
