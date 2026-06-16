# predict-it — ML Competition Platform

A Flask-based machine learning competition platform (a small, self-hostable
Kaggle-style site). Admins create competitions ("tests") with a hidden ground
truth file; participants register, upload CSV predictions, and are scored
automatically against the ground truth. Admins can view and download a
leaderboard for each competition.

## Features

- User registration and login
- Admin dashboard to create, edit, and delete competitions
- CSV prediction upload with automatic scoring
- Evaluation metrics: **Accuracy**, **RMSE**, **MAE**
- Per-competition leaderboard (best submission per user), viewable and
  downloadable as CSV by admins
- Shareable competition links
- Works on SQLite locally and PostgreSQL in production
- Upload size limit (5 MB) and clear validation errors on malformed submissions

## Tech Stack

- **Backend:** Python 3.11, Flask, Gunicorn
- **Database:** PostgreSQL in production (via `DATABASE_URL`), SQLite locally
- **Frontend:** Server-rendered Jinja2 templates + static CSS

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Then visit `http://localhost:5000`.

With no `DATABASE_URL` set, the app uses a local SQLite file (`predict_it.db`)
and prints a warning that data will not persist on ephemeral hosts.

## Configuration (Environment Variables)

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Production | Flask session signing key. Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`. If unset, a random key is generated per process (sessions reset on restart). |
| `DATABASE_URL` | Production | PostgreSQL connection string. **Required for data to persist across restarts.** Without it the app falls back to SQLite, which is wiped on redeploy on ephemeral hosts. `postgres://` URLs are auto-normalized to `postgresql://`. |
| `ADMIN_USERNAME` | Recommended | Admin login. Falls back to a built-in default if unset. |
| `ADMIN_PASSWORD` | Recommended | Admin password. Falls back to a built-in default if unset. |
| `PORT` | No | Port to bind (auto-detected by most hosts; defaults to 5000). |

> Set `ADMIN_USERNAME` / `ADMIN_PASSWORD` in production so the admin account is
> not the public default baked into the source.

## CSV Format

Both the ground truth and prediction files are two-column CSVs with a header
row. The **first column is the ID** and the **second column is the value**.
Column names themselves do not matter.

**Ground truth** (admin uploads when creating a competition):

```csv
id,target
1,0.5
2,1.2
3,0.8
```

**Predictions** (participants submit):

```csv
id,prediction
1,0.48
2,1.25
3,0.82
```

A submission is rejected with a clear message if the file is not valid UTF-8
CSV, has fewer than two columns, contains non-numeric values, or is missing
predictions for any ID present in the ground truth.

## Scoring

| Metric | Meaning | Better |
|---|---|---|
| `accuracy` | Fraction of IDs whose rounded prediction equals the rounded target | Higher |
| `rmse` | Root mean squared error | Lower |
| `mae` | Mean absolute error | Lower |

The leaderboard keeps each user's best submission and orders it appropriately
for the chosen metric.

## Deploy to Render (recommended)

Render builds from your GitHub repo. See `RENDER_DEPLOYMENT.md` for the full
walkthrough. In short:

1. **Create a PostgreSQL database** (New + → PostgreSQL, free tier) and copy its
   Internal Database URL.
2. **Create a Web Service** from this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. **Add environment variables:** `DATABASE_URL` (from step 1), `SECRET_KEY`,
   `ADMIN_USERNAME`, `ADMIN_PASSWORD`.
4. Deploy and visit your app URL.

> On Render's free tier the web service spins down after inactivity (slow first
> request after idle), and free PostgreSQL databases expire after 90 days.

Other hosts (Railway, PythonAnywhere, Heroku) work too — any platform that runs
`gunicorn app:app` and lets you set the environment variables above.

## Project Structure

```
app.py                  # Flask application (routes, DB, scoring)
templates/              # Jinja2 templates (index, login, admin, test, leaderboard, ...)
static/css/style.css    # Styles
requirements.txt        # Python dependencies
runtime.txt             # Python version for the host
Procfile                # gunicorn start command
RENDER_DEPLOYMENT.md    # Detailed Render deployment guide
```

## License

No license specified. Add one if you intend to share or open-source this project.
