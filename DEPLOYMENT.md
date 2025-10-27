# Cloud Deployment Guide

Deploy your ML Competition Platform so students can access it from anywhere via the internet.

## 🚀 Recommended: Railway (Easiest)

**Railway.app** is the simplest option with generous free tier.

### Step 1: Prepare Repository

```bash
cd ml-competition-platform

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect and deploy

### Step 3: Set Environment Variables

In Railway dashboard:
- Click on your service
- Go to "Variables" tab
- Add these:
  ```
  SECRET_KEY=your-random-secret-key-here
  ENVIRONMENT=production
  ```

### Step 4: Get Your URL

Railway provides a URL like: `https://ml-competition-production.up.railway.app`

Share this with students!

**Cost:** Free tier includes 500 hours/month (enough for several tests)

---

## 🔷 Option 2: Render.com (Also Easy)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
# Create repo on GitHub and push
git remote add origin https://github.com/yourusername/ml-competition.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** ml-competition
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

### Step 3: Environment Variables

Add in Render dashboard:
```
SECRET_KEY=your-random-secret-key-here
ENVIRONMENT=production
```

### Step 4: Deploy

Click "Create Web Service" - deployment takes 2-3 minutes.

Your URL: `https://ml-competition.onrender.com`

**Cost:** Free tier available (spins down after 15 min inactivity)

---

## 🟣 Option 3: Heroku (Classic Option)

### Step 1: Install Heroku CLI

```bash
# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Or snap
sudo snap install --classic heroku
```

### Step 2: Deploy

```bash
cd ml-competition-platform

# Login to Heroku
heroku login

# Create app
heroku create ml-competition-yourname

# Set environment variables
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set ENVIRONMENT=production

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

Your URL: `https://ml-competition-yourname.herokuapp.com`

**Cost:** Free tier discontinued - starts at $5/month (Eco plan)

---

## 🐍 Option 4: PythonAnywhere (Python-Focused)

### Step 1: Sign Up

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Create free account

### Step 2: Upload Code

```bash
# On your local machine, create a zip
cd /home/kofi-eli
zip -r ml-competition.zip ml-competition-platform
```

Upload zip to PythonAnywhere or use their console:

```bash
# In PythonAnywhere console
git clone https://github.com/yourusername/ml-competition.git
cd ml-competition
pip install -r requirements.txt --user
```

### Step 3: Configure Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration" → Python 3.10
4. Set:
   - **Source code:** `/home/yourusername/ml-competition`
   - **WSGI file:** Edit to point to your app

### Step 4: WSGI Configuration

Edit the WSGI file:
```python
import sys
path = '/home/yourusername/ml-competition'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

Your URL: `https://yourusername.pythonanywhere.com`

**Cost:** Free tier available (limited to 1 web app)

---

## ⚙️ Environment Variables Required

For ALL platforms, set these:

| Variable | Value | Purpose |
|----------|-------|---------|
| `SECRET_KEY` | Random string | Session security |
| `ENVIRONMENT` | `production` | Disable debug mode |
| `PORT` | (auto-set) | Cloud platform sets this |

Generate a secure key:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

---

## 📝 Post-Deployment Checklist

### 1. Change Admin Password

Before test day, create a secure admin password:
- Option A: Edit `app.py` line 55 before deploying
- Option B: Use the database directly after first run

### 2. Test the Application

1. Visit your deployment URL
2. Register a test student account
3. Login as admin (username: `admin`, password: `admin123`)
4. Upload ground truth CSV
5. Test student submission with sample CSV

### 3. Share URL with Students

Your students will access:
```
https://your-app-name.platform.com
```

No need to be on same network!

---

## 🔒 Security Considerations

### Before Deployment:

1. **Change Secret Key**
   ```bash
   # Generate new key
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

2. **Change Admin Password**
   - Edit `app.py` line 55
   - Or create new admin in database

3. **Set Environment to Production**
   - Disables debug mode
   - Better error handling

### Optional Security Enhancements:

Add rate limiting to `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

Then add to `requirements.txt`:
```
Flask-Limiter==3.5.0
```

---

## 💾 Database Persistence

⚠️ **Important:** Free tiers often have ephemeral storage!

### Solutions:

1. **Use PostgreSQL** (recommended for production)
   - Most platforms offer free PostgreSQL databases
   - Modify `app.py` to use PostgreSQL instead of SQLite

2. **Accept Data Loss** (OK for one-time tests)
   - Data resets when app restarts
   - Fine for short competitions

3. **Export Data Before Shutdown**
   - Download database file after competition
   - Keep local backup

### Upgrade to PostgreSQL (Optional)

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

Update `app.py` connection string to use `DATABASE_URL` env variable.

---

## 🐛 Troubleshooting

### App Won't Start
- Check logs in platform dashboard
- Verify all requirements installed
- Check `Procfile` exists

### Students Can't Upload
- Check file size limits (16MB default)
- Verify uploads folder exists
- Check platform storage limits

### Database Resets
- Use PostgreSQL for persistence
- Or accept SQLite limitations on free tiers

### Slow First Load
- Free tiers often "sleep" after inactivity
- First visit takes 30-60 seconds to wake up
- Consider paid tier for consistent performance

---

## 🎯 Recommended Setup for Your Use Case

**For a one-time test:**
→ Use **Railway** (easiest, fast, reliable)

**For recurring tests throughout semester:**
→ Use **Render** with PostgreSQL addon

**For permanent solution:**
→ Upgrade to paid tier on any platform ($5-7/month)

---

## 📊 Platform Comparison

| Platform | Free Tier | Speed | Ease | Persistence |
|----------|-----------|-------|------|-------------|
| Railway | 500 hrs/mo | ⚡⚡⚡ | ⭐⭐⭐ | ✅ |
| Render | Always-on option | ⚡⚡ | ⭐⭐⭐ | ✅ |
| Heroku | None ($5/mo) | ⚡⚡⚡ | ⭐⭐ | ✅ |
| PythonAnywhere | 1 web app | ⚡ | ⭐⭐ | ✅ |

---

## 🚀 Quick Deploy (Railway - Fastest)

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# or
curl -fsSL https://railway.app/install.sh | sh

# 2. Login
railway login

# 3. Deploy from current directory
cd ml-competition-platform
railway init
railway up

# 4. Set env vars
railway variables set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
railway variables set ENVIRONMENT=production

# 5. Open your app
railway open
```

Done! Share the URL with students.

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Heroku Docs:** https://devcenter.heroku.com

Good luck with your deployment! 🎉
