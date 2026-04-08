# Production Deployment Guide

## Quick Start

### 1. Set Environment Variables

Create a `.env` file or set these in your hosting platform:

```bash
# Required
SECRET_KEY=your-50-character-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Chatbot (optional but recommended)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Database (optional - defaults to SQLite)
# For PostgreSQL:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=calc_tutor
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Generate a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Server

```bash
gunicorn mathtutor.wsgi --bind 0.0.0.0:8000
```

---

## Platform-Specific Guides

### Heroku

```bash
# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set GROQ_API_KEY=gsk_your_key_here

# Deploy
git push heroku production-ready:main

# Run migrations
heroku run python manage.py migrate
```

### Railway / Render

1. Connect your GitHub repository
2. Set environment variables in the dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.railway.app` (or render.com domain)
   - `GROQ_API_KEY`
3. Deploy automatically from `production-ready` branch

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "mathtutor.wsgi", "--bind", "0.0.0.0:8000"]
```

```bash
docker build -t calc-tutor .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=localhost \
  -e GROQ_API_KEY=gsk_your_key \
  calc-tutor
```

### VPS (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv nginx

# Clone and setup
git clone https://github.com/beauvilerobed/calc-tutor-bot.git
cd calc-tutor-bot
python3.12 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
GROQ_API_KEY=gsk_your_key_here
EOF

# Setup
python manage.py collectstatic --noinput
python manage.py migrate

# Run with gunicorn (use systemd for production)
gunicorn mathtutor.wsgi --bind 127.0.0.1:8000 --daemon

# Configure nginx as reverse proxy
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | Dev key | Django secret key (50+ chars) |
| `DEBUG` | Yes | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | Yes | `localhost` | Comma-separated domains |
| `GROQ_API_KEY` | No | None | For AI chatbot feature |
| `DB_ENGINE` | No | SQLite | Database engine |
| `DB_NAME` | No | `db.sqlite3` | Database name |
| `DB_USER` | No | None | Database user |
| `DB_PASSWORD` | No | None | Database password |
| `DB_HOST` | No | None | Database host |
| `DB_PORT` | No | None | Database port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## Security Checklist

- [ ] `SECRET_KEY` is set and not committed to git
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` contains only your domains
- [ ] HTTPS enabled (handled by hosting platform or nginx)
- [ ] Database credentials are secure
- [ ] `.env` file is in `.gitignore`

---

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

### Database errors
```bash
python manage.py migrate
```

### Check configuration
```bash
python manage.py check --deploy
```
