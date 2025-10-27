# Deploy Predict-It to Railway

## Step 1: Prepare Your Repository

Your GitHub repo is ready! Make sure these files are pushed:
- `.gitignore` (hides sensitive files)
- `.env.example` (shows what env vars are needed)
- `Procfile` (tells Railway how to run)
- `requirements.txt` (Python dependencies)

## Step 2: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub" (or create account)
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Find and select your `ml-competition-platform` repo
6. Railway will auto-detect and start building!

## Step 3: Set Environment Variables (IMPORTANT!)

Once your service is deployed:

1. In Railway dashboard, click your service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add these:

| Key | Value | Notes |
|-----|-------|-------|
| `ADMIN_USERNAME` | `isaaceinst3in` | Your admin login username |
| `ADMIN_PASSWORD` | `12zaci` | Your admin login password |
| `SECRET_KEY` | `your-random-string-123abc` | Generate random string |
| `ENVIRONMENT` | `production` | Disables debug mode |

## Step 4: Get Your URL

1. Click "Settings" tab
2. Under "Domains", click "Generate Domain"
3. Your URL: `https://ml-competition-xxxx.up.railway.app`

## Step 5: Share with Students

Send them your deployment URL. They can:
1. Register with their student index
2. Upload predictions
3. See their RMSE scores

## Troubleshooting

**"Application Error" on first load?**
- Wait 30-60 seconds (cold start)
- Check Railway logs for errors

**Credentials not working?**
- Verify env variables are set correctly
- Clear browser cache
- Try incognito mode

**Upload fails?**
- Make sure ground truth CSV is uploaded first
- Check CSV format matches expectations

## Resetting the Database

If you need to reset everything:
1. In Railway, go to your service
2. Check if you have a PostgreSQL database attached
3. If using SQLite, database resets when service restarts

## Upgrading Storage

For persistent data across restarts, Railway recommends adding PostgreSQL:
1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Update `app.py` to use `DATABASE_URL` env variable

Good luck! 🚀
