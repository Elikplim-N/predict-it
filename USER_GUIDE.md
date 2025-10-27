# 📘 Predict-It User Guide

A simple platform for ML testing where students submit predictions and get instant scores.

---

## 🎯 What is Predict-It?

Think of it like a grading system for ML models:
- You (teacher) have the **correct answers**
- Students upload their model's **predictions**
- System automatically calculates how close they are
- Leaderboard shows who's doing best

---

## 👨‍🏫 FOR TEACHERS/ADMINS

### Login to Admin Dashboard

1. Go to the website URL
2. Click **"Admin Login"**
3. Enter username and password you were given
4. You're in! 🎉

### Step 1️⃣: Upload the Correct Answers (Ground Truth)

This is the answer key for your test.

**How to do it:**
1. Prepare a CSV file with your correct answers
2. In admin dashboard, find **"Upload Ground Truth"** section
3. Click **"📁 Select CSV"**
4. Pick your file
5. Click **"⬆️ Upload"**

**CSV Format Example:**
```
id,value
1,23.5
2,45.2
3,67.8
4,12.3
```

**Important:** The system automatically finds the right columns, so don't worry about exact names!

---

### Step 2️⃣: Configure Columns (Optional)

If your CSV uses different column names, tell the system:

1. Find **"⚙️ Configure Columns"** section
2. Enter your column names (e.g., if you use "sample_id" instead of "id")
3. Click **"💾 Save Configuration"**

**The system auto-detects columns, so you usually don't need to do this.**

---

### Step 3️⃣: Monitor the Leaderboard

Watch students' scores in real-time!

**You'll see:**
- 🥇 Student rankings (best to worst)
- 📊 Their RMSE scores (lower is better)
- 📤 Number of attempts
- ⏱️ When they submitted

**Color coding:**
- 🟢 Green RMSE = Good score
- 🟡 Yellow RMSE = OK score  
- 🔴 Red RMSE = Needs improvement

---

## 👨‍🎓 FOR STUDENTS

### Register & Login

**First time:**
1. Click **"Register"**
2. Enter:
   - Full Name
   - Student Index (e.g., "20230001")
   - Password
3. Click **"Register"**
4. Now login with your index & password

**Login next time:**
1. Click **"Student Login"**
2. Enter index & password
3. You'll see your dashboard

---

### Upload Your Predictions

1. In your dashboard, find **"📤 Upload Your Predictions"**
2. Click **"📁 Select CSV File"**
3. Pick your predictions CSV file
4. Click **"⚡ Upload & Calculate RMSE"**
5. **Boom!** You'll see your score immediately! 🎯

**CSV Format (must have these columns):**
```
id,prediction
1,24.1
2,45.5
3,68.2
4,12.8
```

**Tips:**
- You can upload multiple times to improve your score
- Your **best score** is highlighted at the top
- The system keeps track of all your attempts

---

## 📊 Understanding Your Score (RMSE)

**RMSE** = How far off your predictions are from the correct answers

**Example:**
- Correct answer: 100
- Your prediction: 105
- Error: 5

**Lower RMSE = Better predictions**

---

## 🆘 Troubleshooting

### "Ground truth not found"
**Solution:** Admin hasn't uploaded the correct answers yet. Wait for them to upload.

### "Column not found" error
**Solution:** Your CSV has different column names. Contact admin to configure column names.

### "RMSE calculation failed"
**Solution:** Check your CSV:
- Columns must have numbers, not text
- Must have same number of rows as ground truth
- No blank cells

### Can't login
**Solution:**
- Check spelling of username/index
- Make sure caps lock is OFF
- Clear browser cookies and try again

### Upload button is disabled
**Solution:** 
- File must be .csv (not .xlsx or .txt)
- File size must be under 16MB

---

## 📋 CSV File Tips

### ✅ GOOD FORMAT:
```
id,prediction
1,50.5
2,75.2
3,89.1
```

### ❌ BAD FORMAT:
- `sample,output,extra` ← Too many columns
- `id` ← Missing prediction column
- Empty cells or text like "N/A"

---

## 🔐 Security Notes

- Don't share your password
- Don't edit your CSV after upload (upload a new one instead)
- Admin credentials are kept confidential

---

## ❓ FAQs

**Q: Can I see other students' scores?**  
A: No, you only see your own scores and the leaderboard ranking.

**Q: How many times can I submit?**  
A: Unlimited! Your best score is recorded.

**Q: What if I make a mistake in my CSV?**  
A: Just upload a corrected version. Your best score will update automatically.

**Q: When is the test due?**  
A: Your teacher will tell you. The system accepts submissions anytime.

**Q: Why is my RMSE so high?**  
A: Your predictions are far from correct answers. Improve your model and try again!

---

## 📞 Need Help?

Ask your teacher/admin for assistance!

---

**Happy predicting! 🎯**
