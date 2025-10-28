# 🚀 DEPLOY NOW - Step by Step

Follow these exact steps to deploy your serverless ML competition platform.

---

## ⏱️ Estimated Time: 15 minutes

---

## ✅ Step 1: Setup Supabase (5 minutes)

### 1.1 Create Supabase Account
1. Go to https://supabase.com
2. Click **"Start your project"** or **"Sign in"**
3. Sign in with GitHub (recommended)

### 1.2 Create New Project
1. Click **"New Project"**
2. Choose your organization (or create one)
3. Fill in:
   - **Name**: `ml-competition-platform`
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to your users (e.g., US East, Europe West)
4. Click **"Create new project"**
5. ⏳ Wait 2-3 minutes for project to initialize

### 1.3 Run Database Schema
1. In Supabase dashboard, click **"SQL Editor"** in left sidebar
2. Click **"New query"**
3. Open `supabase_schema.sql` file in your project
4. Copy ALL contents and paste into the SQL Editor
5. Click **"Run"** (or press Ctrl/Cmd + Enter)
6. ✅ You should see "Success. No rows returned"

### 1.4 Verify Tables Created
1. Click **"Table Editor"** in left sidebar
2. You should see these tables:
   - `users`
   - `admin`
   - `ground_truth`
   - `submissions`
   - `settings`

### 1.5 Get Your Credentials
1. Click **"Settings"** (gear icon) in left sidebar
2. Click **"API"**
3. Copy these two values (SAVE THEM!):
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **service_role** key (NOT the anon key!) - This is your **secret** key

---

## ✅ Step 2: Generate Admin Password (2 minutes)

### 2.1 Run Password Generator
In your terminal:
```bash
python3 generate_admin_hash.py
```

### 2.2 Enter Password
- Enter your desired admin password (minimum 8 characters)
- Confirm the password
- Copy the generated hash (long string starting with `scrypt:`)

### 2.3 Update Admin in Supabase
1. Go back to Supabase **SQL Editor**
2. Create new query
3. Paste this (replace `YOUR_HASH_HERE` with the hash you copied):
```sql
UPDATE admin 
SET password_hash = 'YOUR_HASH_HERE' 
WHERE username = 'isaaceinst3in';
```
4. Click **"Run"**
5. ✅ Should see "Success. 1 rows affected"

---

## ✅ Step 3: Generate Secret Key (1 minute)

In your terminal, run:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (long random string). This is your `SECRET_KEY`.

---

## ✅ Step 4: Commit to GitHub (2 minutes)

### 4.1 Check Git Status
```bash
git status
```

### 4.2 Add All Files
```bash
git add .
```

### 4.3 Commit Changes
```bash
git commit -m "Serverless version with inline RMSE calculation"
```

### 4.4 Push to GitHub
```bash
git push origin main
```

If you don't have a remote repository:
```bash
# Create new repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## ✅ Step 5: Deploy to Vercel (5 minutes)

### 5.1 Go to Vercel
1. Open https://vercel.com
2. Click **"Sign Up"** or **"Login"**
3. Sign in with GitHub (use same account as your repo)

### 5.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Find your repository in the list
3. Click **"Import"**

### 5.3 Configure Project
1. **Framework Preset**: Select "Other"
2. **Root Directory**: Leave as `.` (current directory)
3. **Build Command**: Leave empty or default
4. **Output Directory**: Leave empty or default

### 5.4 Add Environment Variables
Click **"Environment Variables"** and add these THREE variables:

**Variable 1:**
- Name: `SUPABASE_URL`
- Value: Your Supabase Project URL (from Step 1.5)

**Variable 2:**
- Name: `SUPABASE_KEY`
- Value: Your Supabase service_role key (from Step 1.5)

**Variable 3:**
- Name: `SECRET_KEY`
- Value: The secret key you generated (from Step 3)

### 5.5 Deploy
1. Click **"Deploy"**
2. ⏳ Wait 2-3 minutes for deployment
3. ✅ You'll see "Congratulations!" when done
4. Copy your deployment URL (e.g., `https://your-project.vercel.app`)

---

## ✅ Step 6: Test Your Deployment (5 minutes)

### 6.1 Test Admin Login
Replace `YOUR_VERCEL_URL` and `YOUR_ADMIN_PASSWORD`:

```bash
curl -X POST https://YOUR_VERCEL_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "isaaceinst3in", "password": "YOUR_ADMIN_PASSWORD"}'
```

✅ You should get: `{"message": "Login successful", ...}`

### 6.2 Test Student Registration
```bash
curl -X POST https://YOUR_VERCEL_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"student_index": "TEST001", "password": "test123", "name": "Test Student"}'
```

✅ You should get: `{"message": "Registration successful", ...}`

### 6.3 Test Student Login
```bash
curl -X POST https://YOUR_VERCEL_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"student_index": "TEST001", "password": "test123"}'
```

✅ You should get: `{"message": "Login successful", ...}`

---

## 🎉 Success!

Your serverless ML competition platform is now live at:
**https://your-project.vercel.app**

---

## 📝 Next Steps

### Upload Ground Truth (Admin Task)
You need to upload a ground truth CSV before students can submit:

1. Use an API client (Postman, Insomnia, or curl)
2. Login as admin first (to get session cookie)
3. Upload ground truth CSV to `/api/admin/upload_ground_truth`

**Important:** Ground truth CSV MUST include column headers!

Example:
```csv
id,value
1,10.5
2,20.3
3,15.7
```

### Share with Students
Give your students:
- Platform URL: `https://your-project.vercel.app`
- Tell them to register and submit predictions

### Monitor
- **Vercel Logs**: Check function logs at vercel.com
- **Supabase Logs**: Monitor database at supabase.com
- **API Endpoints**: Test with curl or Postman

---

## 🆘 Troubleshooting

### "Database connection error"
- Check `SUPABASE_URL` is correct in Vercel
- Check `SUPABASE_KEY` is the **service_role** key (not anon)
- Verify Supabase project is active

### "Invalid credentials"
- Re-run `generate_admin_hash.py`
- Update admin table in Supabase with new hash
- Make sure you're using the same password

### "Function timeout"
- Check Vercel function logs
- Verify CSV files aren't too large (>16MB)
- Check Supabase database isn't overloaded

### "RMSE calculation error"
- Ensure CSV has headers
- Check column names in settings
- Verify numeric values only in prediction column

---

## 📚 Documentation

- Full deployment guide: `SERVERLESS_DEPLOY.md`
- API documentation: `README.md`
- Database schema: `supabase_schema.sql`

---

## 🔐 Security Reminders

✅ Never commit `.env` files to GitHub
✅ Keep your `SUPABASE_KEY` secret
✅ Use strong admin password
✅ Change default admin username if needed

---

**Questions?** Check the logs in Vercel and Supabase for detailed error messages.

**Good luck! 🚀**
