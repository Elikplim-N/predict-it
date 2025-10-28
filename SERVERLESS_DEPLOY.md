# Serverless Deployment Guide

## Overview
This is a serverless version of the ML Competition Platform where:
- **RMSE is calculated directly in code** (no external services)
- **Files are stored in the database** (no file system required)
- **Runs on Vercel** with Supabase PostgreSQL
- **Fully scalable** serverless architecture

## Architecture

```
┌─────────────────┐
│  Vercel Edge    │
│   Functions     │
└────────┬────────┘
         │
    ┌────┴─────┐
    │   API    │
    │  Routes  │
    └────┬─────┘
         │
    ┌────┴─────────┐
    │  Supabase    │
    │  PostgreSQL  │
    └──────────────┘
```

### Key Components:
- **api/auth.py** - Student authentication endpoints
- **api/submit.py** - Submission handling with inline RMSE calculation
- **api/admin.py** - Admin dashboard and management
- **api/rmse_calculator.py** - Pure Python RMSE calculator
- **api/db_helper.py** - Supabase database operations

## Prerequisites

1. **Supabase Account** - https://supabase.com
2. **Vercel Account** - https://vercel.com
3. **Git** repository with your code

## Step 1: Setup Supabase

### 1.1 Create Supabase Project
1. Go to https://supabase.com
2. Click "New Project"
3. Choose organization and set:
   - Project name: `ml-competition-platform`
   - Database password: (save this securely)
   - Region: Choose closest to your users

### 1.2 Run Database Schema
1. In Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `supabase_schema.sql`
3. Paste and click **Run**
4. Verify tables are created in **Table Editor**

### 1.3 Get Credentials
1. Go to **Settings → API**
2. Copy these values:
   - **Project URL** (looks like: https://xxxxx.supabase.co)
   - **anon public** key (for public access)
   - **service_role** key (for backend - keep secret!)

### 1.4 Create Admin User
1. Go to SQL Editor
2. Run this to hash your admin password:
   ```python
   # Run locally to generate hash
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("your-admin-password"))
   ```
3. Update the admin row in Supabase:
   ```sql
   UPDATE admin 
   SET password_hash = 'scrypt:32768:8:1$...' -- your generated hash
   WHERE username = 'isaaceinst3in';
   ```

## Step 2: Deploy to Vercel

### 2.1 Connect Repository
1. Go to https://vercel.com
2. Click **New Project**
3. Import your Git repository
4. Select the repository

### 2.2 Configure Environment Variables
In Vercel project settings, add these environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key

# Application Security
SECRET_KEY=your-random-secret-key-here

# Admin Credentials (optional - already in DB)
ADMIN_USERNAME=isaaceinst3in
ADMIN_PASSWORD=your-admin-password
```

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 2.3 Deploy
1. Click **Deploy**
2. Wait for deployment to complete
3. You'll get a URL like: `https://your-project.vercel.app`

## Step 3: Test Your Deployment

### 3.1 Test Admin Login
```bash
curl -X POST https://your-project.vercel.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "isaaceinst3in", "password": "your-password"}'
```

### 3.2 Upload Ground Truth
1. Login as admin
2. Use the upload endpoint with CSV file
3. CSV must include column headers (as per your rules)

### 3.3 Test Student Registration
```bash
curl -X POST https://your-project.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_index": "12345",
    "password": "student123",
    "name": "Test Student"
  }'
```

### 3.4 Test Submission
```bash
curl -X POST https://your-project.vercel.app/api/submit \
  -F "file=@sample_prediction.csv" \
  -H "Cookie: session=your-session-cookie"
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_KEY` | Yes | Service role key (keep secret!) |
| `SECRET_KEY` | Yes | Flask session secret (generate randomly) |
| `ADMIN_USERNAME` | No | Admin username (default: isaaceinst3in) |
| `ADMIN_PASSWORD` | No | Admin password (for reference) |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Student login
- `POST /api/auth/logout` - Logout

### Student Operations
- `POST /api/submit` - Submit prediction CSV
- `GET /api/submissions` - Get user's submissions

### Admin Operations
- `POST /api/admin/login` - Admin login
- `GET /api/admin/leaderboard` - Get leaderboard
- `POST /api/admin/upload_ground_truth` - Upload ground truth CSV
- `POST /api/admin/configure_columns` - Configure CSV columns
- `GET /api/admin/settings` - Get current settings
- `GET /api/admin/export` - Export leaderboard as CSV

## How RMSE Calculation Works

The RMSE is calculated entirely in Python code:

1. **Student uploads CSV** via `/api/submit`
2. **CSV is read into memory** (no file system)
3. **Ground truth fetched from database** (stored as text)
4. **Pandas processes both CSVs** in memory
5. **NumPy calculates RMSE**: `sqrt(mean((pred - truth)^2))`
6. **Result stored in database**

All happens in a single serverless function call!

## CSV Format Requirements

As per your rules, **CSV must include column headers**.

Example valid CSV:
```csv
id,prediction
1,10.5
2,20.3
3,15.7
```

The system auto-detects columns but you can configure:
- ID column name (default: `id`)
- Value column name (default: `value`)

## Troubleshooting

### Database Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check Supabase project is active
- Ensure service role key is used (not anon key)

### RMSE Calculation Errors
- Ensure CSV has headers
- Check column names match configuration
- Verify both files have same number of rows
- Ensure numeric values in prediction column

### Session Issues
- Verify `SECRET_KEY` is set
- Check cookies are enabled
- Sessions persist across function calls (stateless)

## Scaling Considerations

✅ **Automatic scaling** - Vercel handles traffic spikes
✅ **No cold start issues** - Functions warm up quickly
✅ **Database pooling** - Supabase handles connections
✅ **No file storage costs** - CSVs stored in database
✅ **Global CDN** - Fast worldwide access

## Cost Estimates

**Free Tier Limits:**
- Vercel: 100GB bandwidth, 100 hours compute/month
- Supabase: 500MB database, 2GB bandwidth

**Typical Usage:**
- ~100 students = Easily within free tier
- ~1000 submissions/month = Free tier sufficient
- CSV storage: ~1KB per submission = Negligible

## Security Notes

🔒 **Always change default passwords**
🔒 **Use strong SECRET_KEY in production**
🔒 **Keep service_role key secret**
🔒 **Enable HTTPS only (Vercel does this automatically)**
🔒 **Review RLS policies in Supabase**

## Migration from SQLite Version

If migrating from the SQLite version:

1. **Export existing data** from SQLite
2. **Import into Supabase** using SQL
3. **Update environment variables** in Vercel
4. **Test thoroughly** before switching DNS

## Support

For issues:
1. Check Vercel function logs
2. Check Supabase logs
3. Review error messages in API responses
4. Verify environment variables

## Next Steps

- [ ] Setup custom domain in Vercel
- [ ] Configure email notifications (optional)
- [ ] Add monitoring/analytics
- [ ] Setup automated backups in Supabase
- [ ] Create admin dashboard UI (frontend)
