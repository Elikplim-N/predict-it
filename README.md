# ML Competition Platform

A Flask-based machine learning competition platform that can be deployed to any cloud hosting service.

## Features

- User registration and authentication
- Admin dashboard for creating competitions
- CSV file upload for predictions
- Multiple evaluation metrics (Accuracy, RMSE, MAE)
- Leaderboard system
- Responsive design

## Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

## Local Testing

```bash
python app.py
```

Visit `http://localhost:5000`

## Deploy to Cloud

### Option 1: Render.com (Recommended - Free Tier Available)

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository or deploy from this directory
4. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add environment variable:
   - `SECRET_KEY` = (generate a random string)
6. Click "Create Web Service"

### Option 2: Railway.app

1. Visit [railway.app](https://railway.app)
2. Click "Start a New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Flask and deploy
5. Add environment variable `SECRET_KEY`

### Option 3: PythonAnywhere

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files via Files tab
3. Open Bash console and run: `pip install -r requirements.txt`
4. Go to Web tab → Add a new web app → Flask
5. Configure WSGI file to point to `app.py`
6. Set `SECRET_KEY` in WSGI configuration

### Option 4: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-secret-key-here
   git push heroku main
   ```

## CSV Format

### Ground Truth (Admin uploads when creating competition)
```csv
id,target
1,0.5
2,1.2
3,0.8
```

### Predictions (Users submit)
```csv
id,prediction
1,0.48
2,1.25
3,0.82
```

**Important:** Both CSV files MUST include column headers as the first row.

## Environment Variables

- `SECRET_KEY` - Flask secret key for sessions (required for production)
- `PORT` - Port to run on (auto-detected by most platforms)

## Note

This app uses in-memory storage. Data will be lost on restart. For production, integrate a database (PostgreSQL, MongoDB, etc.).
