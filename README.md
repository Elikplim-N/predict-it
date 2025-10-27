# ML Competition Platform

A web application for conducting ML prediction competitions in your class. Students can upload CSV predictions, get RMSE scores, and compete on a leaderboard.

## Features

- **Student Portal**: Register, login, upload predictions, view RMSE scores
- **Admin Dashboard**: Upload ground truth, view leaderboard, track submissions
- **RMSE Calculation**: Automatic calculation of Root Mean Squared Error
- **Multiple Submissions**: Students can submit multiple times to improve their score
- **Real-time Leaderboard**: Ranked by best RMSE score
- **Cloud Deployment**: Deploy to Railway, Render, or Heroku for internet access

## Quick Start - Cloud Deployment (Recommended)

For students to access from anywhere:

```bash
cd ml-competition-platform
./deploy.sh
```

Then follow instructions to deploy on Railway, Render, or Heroku.

**📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for complete cloud deployment guide**

## Setup Instructions (Local Network)

### 1. Install Dependencies

```bash
cd ml-competition-platform
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will start on `http://0.0.0.0:5000`

### 3. Find Your IP Address

To allow students on the network to access the platform:

```bash
# On Linux/Mac
hostname -I

# On Windows
ipconfig
```

Students will access the platform using: `http://YOUR_IP_ADDRESS:5000`

For example: `http://192.168.1.100:5000`

## Usage Guide

### For Admin (You)

1. **Login**
   - Go to Admin Login
   - Default credentials:
     - Username: `admin`
     - Password: `admin123`
   - **IMPORTANT**: Change these in `app.py` line 55 before production use!

2. **Upload Ground Truth**
   - Upload your CSV file with the true values
   - This is what student predictions will be compared against
   - CSV format example:
     ```csv
     id,value
     1,0.234
     2,0.567
     3,0.891
     ```

3. **Monitor Leaderboard**
   - See all students ranked by best RMSE
   - View submission counts and timestamps
   - Track competition progress in real-time

### For Students

1. **Register**
   - Enter student index (e.g., "20210001")
   - Create a password
   - Enter full name

2. **Login**
   - Use student index and password

3. **Upload Predictions**
   - Upload CSV file with predictions
   - CSV format should match ground truth:
     ```csv
     id,prediction
     1,0.245
     2,0.560
     3,0.895
     ```
   - RMSE is calculated immediately
   - Can submit multiple times to improve score

4. **View Results**
   - See all your submissions
   - Track your best RMSE score
   - View submission history

## CSV File Format

Both student predictions and ground truth must follow this format:

- **Column 1**: `id` (optional, used for alignment)
- **Column 2**: `prediction` or `value` (the actual numerical values)
- **Same number of rows** in both files

Example:
```csv
id,prediction
1,0.234
2,0.567
3,0.891
4,1.234
```

## Network Setup for Class

1. **Ensure all students are on the same WiFi network** as your computer
2. **Check firewall settings** - port 5000 should be open
3. **Share your IP address** with students (e.g., `192.168.1.100:5000`)
4. Students can access from any browser on their phones or laptops

## Troubleshooting

### Students can't connect
- Verify you're all on the same network
- Check firewall isn't blocking port 5000
- On Linux: `sudo ufw allow 5000`
- Try accessing from your browser first: `http://localhost:5000`

### RMSE calculation errors
- Ensure both CSVs have the same number of rows
- Check column names (should be 'prediction' or 'value')
- Verify all values are numeric (no missing values)

### Database issues
- Delete `competition.db` to reset everything
- Database is created automatically on first run

## Security Notes

**For classroom use:**
- Default admin password should be changed (line 55 in `app.py`)
- Secret key should be changed (line 11 in `app.py`)
- This is designed for local network use during class time
- Not suitable for internet-facing deployment without additional security

## Data Storage

- **Database**: SQLite (`competition.db`)
- **Uploaded files**: `uploads/` directory
- **All data is stored locally** on your machine

## Resetting for a New Competition

1. Stop the application (Ctrl+C)
2. Delete `competition.db`
3. Delete files in `uploads/` directory
4. Restart the application

## Support

If issues arise during the test:
1. Check the terminal for error messages
2. Verify ground truth is uploaded
3. Confirm CSV formats match requirements
4. Restart the application if needed
