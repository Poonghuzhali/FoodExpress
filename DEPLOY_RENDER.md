# Deploy FoodExpress on Render

## Your error fix

If Blueprint shows:

> **Create database foodexpress-db** — cannot have more than one active free tier database

Render free plan allows **only 1 PostgreSQL database** per account. You already have one, so the Blueprint must **not** create a new database.

The repo `render.yaml` is now updated to deploy **web service only**. Use your **existing** database.

---

## Deploy now (use existing database)

### Step 1 — Copy your database URL

1. Open [Render Dashboard](https://dashboard.render.com/)
2. Click your existing **PostgreSQL** database (e.g. `foodexpress-db`)
3. Go to **Connect** or **Info** tab
4. Copy the **Internal Database URL** (starts with `postgresql://...`)

### Step 2 — Deploy with Blueprint

1. Click **New +** → **Blueprint**
2. Select repo: **Poonghuzhali/FoodExpress**
3. Render shows only: **foodexpress** (web service)
4. When asked for **DATABASE_URL**, paste the **Internal Database URL** from Step 1
5. Click **Apply** and wait 5–10 minutes

### Alternative — Manual web service

1. **New +** → **Web Service**
2. Connect **Poonghuzhali/FoodExpress** repo, branch **master**
3. Settings:
   - **Name:** foodexpress
   - **Region:** Singapore (same region as your database)
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn fooddelivery.wsgi:application --bind 0.0.0.0:$PORT`
4. Environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.3` |
| `SECRET_KEY` | Generate random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Your existing **Internal Database URL** |

5. Click **Create Web Service**

---

## After deploy

- App URL: `https://foodexpress.onrender.com` (or the URL Render gives you)
- Login: **admin** / **admin123**

Check **Logs** for:
- `Running database migrations...`
- `Seeding demo data...`
- `Build finished successfully.`

---

## Other options

| Situation | What to do |
|-----------|------------|
| Old unused free DB exists | Delete it in Render, then you can create a new one |
| Want fresh database | Delete old free DB first, then restore `databases:` section in render.yaml |
| Web service region ≠ DB region | Create web service in **same region** as your PostgreSQL |
