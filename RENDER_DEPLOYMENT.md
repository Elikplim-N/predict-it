# Deploy to Render with PostgreSQL

## Steps to Deploy

1. **Push your code to GitHub** (already done)

2. **Create PostgreSQL Database on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "PostgreSQL"
   - Name: `predictit-db` (or any name)
   - Select free tier
   - Click "Create Database"
   - **Copy the Internal Database URL** (starts with `postgres://`)

3. **Create Web Service on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository `Elikplim-N/predict-it`
   - Configure:
     - **Name**: `predictit` (or any name)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   
4. **Add Environment Variables**
   - Click "Environment" tab
   - Add these variables:
     - `SECRET_KEY` = `your-random-secret-key-here` (generate one)
     - `DATABASE_URL` = Paste the Internal Database URL you copied in step 2
     - `ADMIN_USERNAME` = your chosen admin login
     - `ADMIN_PASSWORD` = your chosen admin password
   - **`DATABASE_URL` is required for your data to survive restarts.** Without
     it the app falls back to SQLite, which is wiped every time the service
     restarts or redeploys on the free tier.
   
5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Visit your app URL!

## Generate Secret Key

Run this locally to generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Important Notes

- The PostgreSQL database will persist data even when the app restarts
- Free tier databases have storage limits
- Your app will automatically detect `DATABASE_URL` and use PostgreSQL
- If `DATABASE_URL` is not set, it falls back to SQLite (for local development)

## Admin Login

The admin username and password come from the `ADMIN_USERNAME` and
`ADMIN_PASSWORD` environment variables. If they are not set, the app falls
back to the local development defaults (`isaac3instein` / `12zaci`) — set the
environment variables in production so the credentials are not the public
defaults.
