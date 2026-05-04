# CaLaun Deployment Guide

## Recommended free stack (May 2026)

| Layer | Provider | Free tier |
|-------|----------|-----------|
| Web app | **Render** (Web Service) | 750 instance hrs/mo, sleeps after 15 min idle, auto-wakes |
| Database | **Neon** (Postgres) | 0.5 GB storage, 100 CU-hrs/mo, no expiry |
| Domain | `*.onrender.com` (free, included) — or attach a custom domain on the Hobby workspace (2 free) |
| TLS | Free, auto-managed by Render |

Render's own free Postgres expires after 30 days — that's why we use **Neon** instead, which is genuinely free with no time limit.

---

## Step 1 — Create a free Neon Postgres database

1. Sign up at https://neon.com (GitHub login works, no card required).
2. Create a new project — pick the region closest to where Render runs (`us-east` is a safe default).
3. Open the project's **Connection details** and copy the **pooled** connection string. It looks like:
   ```
   postgres://USER:PASSWORD@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
   Save this — you'll paste it into Render as `DATABASE_URL`.

## Step 2 — Generate a SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output for the next step.

## Step 3 — Deploy on Render

1. Push your branch to GitHub (or fork the repo).
2. Go to https://dashboard.render.com → **New** → **Web Service** → connect your repo.
3. Choose:
   - **Environment**: Python
   - **Build command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start command**: `gunicorn mathtutor.wsgi --bind 0.0.0.0:$PORT`
   - **Instance type**: Free
4. Add **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | (paste from Step 2) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
   | `CSRF_TRUSTED_ORIGINS` | `https://your-app-name.onrender.com` |
   | `DATABASE_URL` | (paste from Step 1) |
   | `GROQ_API_KEY` | (free key from https://console.groq.com/keys) |
   | `LOG_LEVEL` | `INFO` |

5. Click **Create Web Service**. First deploy takes ~3–5 min.
6. Visit `https://your-app-name.onrender.com` — you're live.

> **Cold start note:** the free instance sleeps after 15 minutes of inactivity and takes ~30 s to wake up on the next request. For a non-profit teaching tool that's typically fine; if you want it always-on, Render's Starter ($7/mo) or self-hosting on a small VPS removes the sleep.

## Step 4 — (Optional) Add a custom domain

If you have a domain (e.g. from a non-profit donation, Namecheap for ~$10/yr, or a free one via https://eu.org), add it under **Settings → Custom Domains** in Render. TLS is auto-issued.

If you don't, the free `*.onrender.com` subdomain is a perfectly valid public URL.

---

## Local development

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then edit .env
python manage.py migrate
python manage.py runserver
```

Local dev defaults to SQLite (no `DATABASE_URL` set), so you don't need Postgres locally unless you want to mirror production.

To run against a local Postgres:

```bash
# Install postgres (macOS)
brew install postgresql@16 && brew services start postgresql@16
createdb calaun
# Then in .env:
# DATABASE_URL=postgres://$USER@localhost:5432/calaun
```

---

## Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | prod | dev key | Django secret. 50+ random chars. |
| `DEBUG` | yes | `True` | `False` in production. |
| `ALLOWED_HOSTS` | prod | `127.0.0.1,localhost` | Comma-separated hosts. |
| `CSRF_TRUSTED_ORIGINS` | prod | empty | Comma-separated, **with scheme**: `https://example.com`. Required for HTTPS POSTs. |
| `DATABASE_URL` | prod | unset (SQLite) | Full Postgres URL. |
| `GROQ_API_KEY` | optional | unset | Enables the chatbot. |
| `SECURE_SSL_REDIRECT` | optional | `True` | Honored only when `DEBUG=False`. |
| `SECURE_HSTS_SECONDS` | optional | `31536000` | HSTS duration. |
| `LOG_LEVEL` | optional | `INFO` | Standard logging levels. |

---

## Other deployment targets

### Docker

```bash
docker build -t calaun .
docker run -p 8000:8000 \
  -e SECRET_KEY=... \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=localhost \
  -e DATABASE_URL=postgres://... \
  -e GROQ_API_KEY=gsk_... \
  calaun
```

### Railway

The repo includes `railway.toml`. Connect the repo in Railway, add the same env vars as above, and provision a Postgres add-on (Railway's free credit covers low traffic for a while, but it's not a permanent free tier).

### VPS (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv nginx postgresql
git clone https://github.com/beauvilerobed/calc-tutor-bot.git
cd calc-tutor-bot
python3.12 -m venv env && source env/bin/activate
pip install -r requirements.txt

cat > .env <<EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(64))')
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgres://user:pass@localhost:5432/calaun
GROQ_API_KEY=gsk_...
EOF

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn mathtutor.wsgi --bind 127.0.0.1:8000 --daemon
# then put nginx in front for TLS / reverse proxy
```

---

## Security checklist

- [ ] `SECRET_KEY` is 50+ random chars, set via env (never committed)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` contains only your real hosts
- [ ] `CSRF_TRUSTED_ORIGINS` includes your `https://...` host(s)
- [ ] `.env` is in `.gitignore` (it is — verified)
- [ ] HTTPS enforced (Render does this automatically; on a VPS use nginx + certbot)
- [ ] `python manage.py check --deploy` reports no issues with prod env vars set

## Troubleshooting

- **Static files 404 in prod** → re-run `python manage.py collectstatic --noinput` (already in build command).
- **CSRF "Origin checking failed"** → add the full `https://...` URL to `CSRF_TRUSTED_ORIGINS`.
- **Postgres SSL error on Neon** → settings already set `sslmode=require` automatically when `DEBUG=False`.
- **App is slow on first request** → cold start from sleep. Upgrade Render plan or ping it via uptime monitor.
