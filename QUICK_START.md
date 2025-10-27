# Quick Start Guide - Test Day

## Before Class

1. **Install dependencies** (one time only):
   ```bash
   cd ml-competition-platform
   pip install -r requirements.txt
   ```

2. **Prepare your ground truth CSV** with actual values

3. **Change admin password** (optional but recommended):
   - Edit `app.py` line 55
   - Change `'admin123'` to your preferred password

## On Test Day

### Step 1: Start the Server (5 minutes before class)

```bash
cd ml-competition-platform
./start.sh
```

Or:
```bash
python3 app.py
```

### Step 2: Get Your IP Address

The `start.sh` script will show your IP, or run:
```bash
hostname -I
```

Example output: `192.168.1.100`

### Step 3: Share with Students

Write on the board:
```
Competition URL: http://192.168.1.100:5000
```

Students access this from their browsers (laptop or phone).

### Step 4: Upload Ground Truth

1. Go to `http://localhost:5000/admin/login`
2. Login (username: `admin`, password: `admin123`)
3. Upload your ground truth CSV
4. Leave this page open to monitor the leaderboard

### Step 5: Students Participate

Students should:
1. Go to the URL you shared
2. Register with their student index
3. Upload their prediction CSV
4. See their RMSE score immediately
5. Can submit multiple times to improve

### Step 6: Monitor Competition

- Admin dashboard shows live leaderboard
- Refresh page to see new submissions
- Top 3 students get gold/silver/bronze badges

## During the Test

### If a student can't connect:
- ✅ Confirm they're on the same WiFi
- ✅ Verify the IP address is correct
- ✅ Check your firewall (run: `sudo ufw allow 5000`)

### If RMSE calculation fails:
- ✅ Check their CSV has same number of rows as ground truth
- ✅ Verify column names ('id' and 'prediction' or 'value')
- ✅ Ensure all values are numeric

### If you need to restart:
```bash
# Stop server: Ctrl+C
# Restart:
./start.sh
```

## After the Test

### Export Results
The database `competition.db` contains all submissions. You can:
- Keep the leaderboard page open
- Take a screenshot
- Query the database directly if needed

### Reset for Next Time
```bash
rm competition.db
rm uploads/*
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't access admin page | Go to `/admin/login` not just `/admin` |
| Students see "No ground truth" | You need to upload ground truth first as admin |
| Port 5000 already in use | Change port in `app.py` line 328 |
| Students can't upload | Check file size < 16MB and file is .csv |

## CSV Format Reminder

**Ground Truth** (`sample_ground_truth.csv`):
```csv
id,value
1,2.345
2,3.456
3,4.567
```

**Student Predictions** (`sample_prediction.csv`):
```csv
id,prediction
1,2.350
2,3.450
3,4.560
```

Both must have:
- Same number of rows
- Numeric values only
- Column names: 'id', 'value'/'prediction'

## Contact Info for Students

Print this for students:

```
═══════════════════════════════════════
    ML COMPETITION - INSTRUCTIONS
═══════════════════════════════════════

1. Connect to WiFi: [YOUR_WIFI_NAME]

2. Go to: http://[YOUR_IP]:5000

3. Register with your student index

4. Upload your predictions.csv

5. Check your RMSE score

6. Submit again to improve!

═══════════════════════════════════════
```

Good luck with your competition! 🎉
