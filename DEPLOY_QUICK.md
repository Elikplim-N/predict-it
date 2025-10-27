# Quick Cloud Deployment Guide

## 🎯 Goal
Deploy so students can access from **anywhere** (not just your local network).

## ⚡ Fastest Method: Railway

### 1. Push to GitHub (First Time)

```bash
cd ml-competition-platform

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ml-competition.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Railway

1. Go to **[railway.app](https://railway.app)**
2. Click **"Login with GitHub"**
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `ml-competition` repository
6. Railway will automatically build and deploy!

### 3. Set Environment Variables

In Railway dashboard:
- Click on your service
- Go to **"Variables"** tab
- Click **"+ New Variable"**
- Add:
  - **Name:** `SECRET_KEY`
  - **Value:** (generate with command below)
  - **Name:** `ENVIRONMENT`
  - **Value:** `production`

Generate secret key:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### 4. Get Your URL

- Click **"Settings"** tab
- Under **"Domains"**, click **"Generate Domain"**
- Your URL will be something like: `https://ml-competition-production.up.railway.app`

### 5. Share with Students! 🎉

Students access: `https://your-app.up.railway.app`

---

## 🔷 Alternative: Render.com

### Steps:

1. Push code to GitHub (same as above)
2. Go to **[render.com](https://render.com)**
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name:** `ml-competition`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Add environment variables (same as Railway)
7. Click **"Create Web Service"**

Your URL: `https://ml-competition.onrender.com`

⚠️ **Note:** Free tier "sleeps" after 15 min inactivity. First visit takes 30-60 seconds to wake up.

---

## 📋 Pre-Deployment Checklist

- [ ] Change admin password in `app.py` line 55 (optional)
- [ ] Generate SECRET_KEY
- [ ] Push code to GitHub
- [ ] Deploy on chosen platform
- [ ] Set environment variables
- [ ] Test the deployment URL
- [ ] Upload ground truth CSV as admin
- [ ] Test student submission with sample CSV

---

## 🧪 Testing Your Deployment

1. Visit your deployment URL
2. Click "Register" → Create test student account
3. Login as student → Try uploading `sample_prediction.csv`
4. Go to `/admin/login` → Login (admin/admin123)
5. Upload `sample_ground_truth.csv`
6. Go back to student account → Upload prediction again
7. Verify RMSE calculation works
8. Check leaderboard in admin dashboard

---

## 💡 Tips

### Free Tier Limitations:
- **Railway:** 500 hours/month (plenty for multiple tests)
- **Render:** Sleeps after 15 min inactivity
- **Both:** May lose data on restart (use PostgreSQL for persistence)

### For Short Tests (1-2 hours):
- Free tier is perfect
- No need for database persistence
- Just export results before shutting down

### For Semester-Long Use:
- Consider paid tier ($5-7/month)
- Or use PostgreSQL addon (see DEPLOYMENT.md)

---

## 🚨 Troubleshooting

**"Application Error" on first visit:**
- Wait 30-60 seconds for cold start
- Check platform logs for errors
- Verify all dependencies in requirements.txt

**Admin can't login:**
- Default: username `admin`, password `admin123`
- Access at: `https://your-url.com/admin/login` (not `/admin`)

**Students can't upload:**
- Did you upload ground truth first?
- Check file is CSV format
- Verify file size < 16MB

**Need to reset everything:**
- Redeploy or restart the service
- Database will reset automatically (with SQLite)

---

## 📞 Quick Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Render Dashboard:** https://dashboard.render.com
- **Full Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ⏱️ Time Estimate

**Total deployment time:** 10-15 minutes

- GitHub push: 2 min
- Railway setup: 5 min  
- Testing: 5 min

---

Good luck! 🚀
