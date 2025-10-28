# ML Competition Platform (Serverless)

A fully serverless machine learning competition platform with inline RMSE calculation.

## 🚀 Features

- ✅ **Serverless Architecture** - Runs on Vercel + Supabase
- ✅ **RMSE Calculated in Code** - Pure Python, no external services
- ✅ **No File System** - CSV data stored in PostgreSQL
- ✅ **Auto-scaling** - Handles unlimited concurrent users
- ✅ **CSV Header Validation** - Enforces proper format
- ✅ **Student Submissions** - Upload predictions and get instant RMSE
- ✅ **Leaderboard** - Real-time rankings
- ✅ **Admin Dashboard** - Manage competitions

## 📁 Project Structure

```
.
├── api/                          # Serverless API endpoints
│   ├── auth.py                  # Student authentication
│   ├── submit.py                # Submission handling
│   ├── admin.py                 # Admin operations
│   ├── db_helper.py             # Database utilities
│   └── rmse_calculator.py       # RMSE calculation
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
├── supabase_schema.sql          # Database schema
├── generate_admin_hash.py       # Password hash generator
├── .env.serverless              # Environment template
└── SERVERLESS_DEPLOY.md         # Deployment guide
```

## 🎯 Quick Start

### 1. Setup Supabase

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Run `supabase_schema.sql` in SQL Editor
4. Get your project URL and service role key

### 2. Generate Admin Password

```bash
python3 generate_admin_hash.py
```

Copy the generated hash and update in Supabase:

```sql
UPDATE admin 
SET password_hash = 'your-generated-hash' 
WHERE username = 'isaaceinst3in';
```

### 3. Deploy to Vercel

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Add environment variables:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your service role key
   - `SECRET_KEY` - Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
5. Click Deploy

### 4. Test Your Deployment

```bash
# Test admin login
curl -X POST https://your-project.vercel.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "isaaceinst3in", "password": "your-password"}'

# Test student registration
curl -X POST https://your-project.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"student_index": "12345", "password": "test123", "name": "Test Student"}'
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register student
- `POST /api/auth/login` - Student login
- `POST /api/auth/logout` - Logout

### Student Operations
- `POST /api/submit` - Submit prediction CSV
- `GET /api/submissions` - Get your submissions

### Admin Operations
- `POST /api/admin/login` - Admin login
- `GET /api/admin/leaderboard` - Get leaderboard
- `POST /api/admin/upload_ground_truth` - Upload ground truth
- `POST /api/admin/configure_columns` - Configure CSV columns
- `GET /api/admin/settings` - Get settings
- `GET /api/admin/export` - Export results

## 📋 CSV Format

**CSV files MUST include column headers.**

Example:
```csv
id,prediction
1,10.5
2,20.3
3,15.7
```

## 💡 How RMSE Works

1. Student uploads CSV via API
2. CSV read into memory (no file system)
3. Ground truth fetched from database
4. Pandas + NumPy calculate RMSE: `sqrt(mean((pred - truth)^2))`
5. Result stored in database
6. Leaderboard updated

All happens in a single serverless function!

## 🔒 Security

- HTTPS only (automatic with Vercel)
- Password hashing with Werkzeug
- Session-based authentication
- Row Level Security in Supabase
- Service role key never exposed

## 💰 Cost

**Free Tier:**
- Vercel: 100GB bandwidth/month
- Supabase: 500MB database

Typical usage for 100 students: **$0/month**

## 📖 Documentation

See [SERVERLESS_DEPLOY.md](SERVERLESS_DEPLOY.md) for detailed deployment instructions.

## 🆘 Troubleshooting

**Database connection issues?**
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Use service role key (not anon key)

**RMSE errors?**
- Ensure CSV has headers
- Check column names match configuration
- Verify numeric values in prediction column

**Session issues?**
- Verify `SECRET_KEY` is set
- Check cookies are enabled

## 🤝 Contributing

This is a serverless version optimized for Vercel + Supabase.

## 📝 License

MIT License

---

**Need help?** Check Vercel function logs and Supabase logs for errors.
