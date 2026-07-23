# Deploy FoodExpress on Render (Web + PostgreSQL)

Follow these steps on [Render Dashboard](https://dashboard.render.com/) to deploy the app **and database** together.

## Option A — Blueprint (recommended)

Creates **PostgreSQL database** + **web service** in one step.

1. Sign in at https://dashboard.render.com/ (use **Continue with GitHub**).
2. Click **New +** → **Blueprint**.
3. Connect GitHub if asked, then select repository: **Poonghuzhali/FoodExpress**
4. Render reads `render.yaml` and shows:
   - **foodexpress-db** — PostgreSQL (free)
   - **foodexpress** — Django web service
5. Click **Apply** and wait 5–10 minutes for build to finish.

The web service gets `DATABASE_URL` automatically from the database. Build runs migrations and seeds demo data.

## Option B — Manual (database first)

Use this if Blueprint is not available.

### Step 1 — Create PostgreSQL database

1. **New +** → **PostgreSQL**
2. Name: `foodexpress-db`
3. Database: `foodexpress`
4. User: `foodexpress`
5. Region: **Singapore** (same as web service)
6. Plan: **Free**
7. Click **Create Database**
8. Wait until status is **Available**
9. Copy **Internal Database URL** from the database page

### Step 2 — Create web service

1. **New +** → **Web Service**
2. Connect repo: **Poonghuzhali/FoodExpress**
3. Settings:
   - **Name:** foodexpress
   - **Region:** Singapore
   - **Branch:** master
   - **Runtime:** Python
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn fooddelivery.wsgi:application --bind 0.0.0.0:$PORT`
4. Environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.3` |
| `SECRET_KEY` | Generate (random string) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Paste **Internal Database URL** from Step 1 |

5. Click **Create Web Service**

## After deploy

- Open your app URL, e.g. `https://foodexpress.onrender.com`
- Login with demo accounts from README (admin / admin123)

## Verify database

In Render → **foodexpress-db** → **Connect** tab, you can open **PSQL** or view connection info.

In web service **Logs**, you should see:
- `Running migrations...`
- `Seeding database...`
- `Created admin (admin/admin123)`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails on migrate | Check `DATABASE_URL` is set on web service |
| 502 / app not loading | Check **Logs** tab; ensure gunicorn started |
| CSRF error on login | Redeploy after first deploy (Render sets `RENDER_EXTERNAL_HOSTNAME`) |
| Free tier slow start | First request after idle may take ~1 minute |
