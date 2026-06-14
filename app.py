import os
import csv
import sqlite3
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Reject uploads larger than 5 MB to avoid exhausting memory.
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Admin credentials - read from the environment in production, with the
# previous values kept as a local-development fallback.
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'isaac3instein')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '12zaci')
ADMIN_HASH = generate_password_hash(ADMIN_PASSWORD)

# Database configuration - use PostgreSQL if DATABASE_URL exists, else SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("WARNING: psycopg2 not available, falling back to SQLite")
        USE_POSTGRES = False

if not USE_POSTGRES:
    print("WARNING: DATABASE_URL is not set - using local SQLite. On ephemeral "
          "hosts (e.g. Render's free tier) the database file is wiped on every "
          "restart, so all users, tests, and submissions will be LOST. Set "
          "DATABASE_URL to a PostgreSQL database for persistent storage.")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if USE_POSTGRES:
            db = g._database = psycopg2.connect(DATABASE_URL)
        else:
            db = g._database = sqlite3.connect('predict_it.db')
            db.row_factory = sqlite3.Row
    return db

class DBWrapper:
    """Wrapper to make PostgreSQL queries work with ? placeholders like SQLite"""
    def __init__(self, db):
        self.db = db
        self.is_postgres = USE_POSTGRES
    
    def execute(self, query, params=()):
        if self.is_postgres:
            # Convert ? to %s for PostgreSQL
            pg_query = query.replace('?', '%s')
            cursor = self.db.cursor()
            cursor.execute(pg_query, params)
            return PGResult(cursor)
        else:
            return self.db.execute(query, params)
    
    def commit(self):
        self.db.commit()

class PGResult:
    """Wrapper to make PostgreSQL cursor results dict-accessible like SQLite Row"""
    def __init__(self, cursor):
        self.cursor = cursor
    
    def fetchone(self):
        row = self.cursor.fetchone()
        if row and self.cursor.description:
            cols = [desc[0] for desc in self.cursor.description]
            return dict(zip(cols, row))
        return None
    
    def fetchall(self):
        rows = self.cursor.fetchall()
        if rows and self.cursor.description:
            cols = [desc[0] for desc in self.cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        return []

def get_db_wrapper():
    """Get database connection wrapped for compatibility"""
    return DBWrapper(get_db())

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        if USE_POSTGRES:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tests (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    metric TEXT,
                    ground_truth TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id SERIAL PRIMARY KEY,
                    test_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    score REAL NOT NULL,
                    filename TEXT,
                    FOREIGN KEY (test_id) REFERENCES tests (id)
                )
            ''')
            db.commit()
        else:
            db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            ''')
            db.execute('''
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    metric TEXT,
                    ground_truth TEXT
                )
            ''')
            db.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    score REAL NOT NULL,
                    filename TEXT,
                    FOREIGN KEY (test_id) REFERENCES tests (id)
                )
            ''')
            db.commit()

_db_initialized = False

@app.before_request
def before_first_request():
    """Initialize the database once, on the first request."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True

@app.errorhandler(413)
def file_too_large(error):
    flash('File too large. The maximum upload size is 5 MB.')
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    db = get_db_wrapper()
    tests = db.execute('SELECT * FROM tests ORDER BY id DESC').fetchall()
    return render_template('index.html', tests=tests)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        db = get_db_wrapper()
        existing_user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                   (username, generate_password_hash(password), email))
        db.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check admin login (fixed credentials)
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_HASH, password):
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        
        # Check student login
        db = get_db_wrapper()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['is_admin'] = False
            return redirect(url_for('index'))
        
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    tests = db.execute('SELECT * FROM tests ORDER BY id DESC').fetchall()
    submissions = db.execute('SELECT * FROM submissions ORDER BY timestamp DESC').fetchall()
    return render_template('admin.html', tests=tests, submissions=submissions)

@app.route('/admin/create_test', methods=['POST'])
def create_test():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    name = request.form['name']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    metric = request.form['metric']
    ground_truth = None
    
    # Handle ground truth file upload
    if 'ground_truth' in request.files:
        file = request.files['ground_truth']
        if file and file.filename.endswith('.csv'):
            ground_truth = file.read().decode('utf-8')
    
    db = get_db_wrapper()
    db.execute('INSERT INTO tests (name, description, start_date, end_date, metric, ground_truth) VALUES (?, ?, ?, ?, ?, ?)',
               (name, description, start_date, end_date, metric, ground_truth))
    db.commit()
    
    flash('Test created successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    # Delete submissions first (foreign key constraint)
    db.execute('DELETE FROM submissions WHERE test_id = ?', (test_id,))
    # Delete the test
    db.execute('DELETE FROM tests WHERE id = ?', (test_id,))
    db.commit()
    
    flash('Test deleted successfully!')
    return '', 200

@app.route('/admin/edit_test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        metric = request.form['metric']
        
        # Handle ground truth file upload (optional on edit)
        ground_truth = None
        if 'ground_truth' in request.files:
            file = request.files['ground_truth']
            if file and file.filename.endswith('.csv'):
                ground_truth = file.read().decode('utf-8')
                # Update with new ground truth
                db.execute('UPDATE tests SET name = ?, description = ?, start_date = ?, end_date = ?, metric = ?, ground_truth = ? WHERE id = ?',
                           (name, description, start_date, end_date, metric, ground_truth, test_id))
            else:
                # Update without changing ground truth
                db.execute('UPDATE tests SET name = ?, description = ?, start_date = ?, end_date = ?, metric = ? WHERE id = ?',
                           (name, description, start_date, end_date, metric, test_id))
        else:
            # Update without changing ground truth
            db.execute('UPDATE tests SET name = ?, description = ?, start_date = ?, end_date = ?, metric = ? WHERE id = ?',
                       (name, description, start_date, end_date, metric, test_id))
        
        db.commit()
        flash('Test updated successfully!')
        return redirect(url_for('admin_dashboard'))
    
    # GET request - show edit form
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    if not test:
        flash('Test not found')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_test.html', test=test)

@app.route('/test/<int:test_id>')
def test_detail(test_id):
    db = get_db_wrapper()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    if not test:
        flash('Test not found')
        return redirect(url_for('index'))
    
    test_submissions = db.execute('SELECT * FROM submissions WHERE test_id = ? ORDER BY timestamp DESC',
                                   (test_id,)).fetchall()
    
    return render_template('test.html', test=test, submissions=test_submissions)

@app.route('/test/<int:test_id>/submit', methods=['POST'])
def submit_prediction(test_id):
    if 'username' not in session:
        flash('Please login to submit')
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    if not test:
        flash('Test not found')
        return redirect(url_for('index'))
    
    if 'prediction_file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('test_detail', test_id=test_id))
    
    file = request.files['prediction_file']
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file')
        return redirect(url_for('test_detail', test_id=test_id))
    
    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        flash('Could not read the file. Please upload a valid UTF-8 encoded CSV.')
        return redirect(url_for('test_detail', test_id=test_id))

    score, error = calculate_score(content, test['ground_truth'], test['metric'])
    if error:
        flash(f'Submission rejected: {error}')
        return redirect(url_for('test_detail', test_id=test_id))

    db.execute('INSERT INTO submissions (test_id, username, timestamp, score, filename) VALUES (?, ?, ?, ?, ?)',
               (test_id, session['username'], datetime.now().isoformat(), score, file.filename))
    db.commit()

    flash(f'Submission successful! Score: {score:.4f}')
    return redirect(url_for('test_detail', test_id=test_id))





@app.route('/leaderboard/<int:test_id>')
def leaderboard(test_id):
    # Only admins can view leaderboard
    if not session.get('is_admin'):
        flash('Admin access required to view leaderboard')
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    if not test:
        flash('Test not found')
        return redirect(url_for('index'))
    
    # Get all submissions for this test
    test_submissions = db.execute(
        'SELECT * FROM submissions WHERE test_id = ? ORDER BY score DESC',
        (test_id,)
    ).fetchall()
    
    # Get best submission per user
    user_best = {}
    for sub in test_submissions:
        username = sub['username']
        if username not in user_best:
            user_best[username] = sub
    
    # Sort by score (descending for accuracy, ascending for RMSE/MAE)
    leaderboard_data = list(user_best.values())
    if test['metric'] in ['rmse', 'mae']:
        leaderboard_data.sort(key=lambda x: x['score'])
    else:
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('leaderboard.html', test=test, leaderboard=leaderboard_data)

@app.route('/leaderboard/<int:test_id>/download')
def download_leaderboard(test_id):
    # Only admins can download leaderboard
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('login'))
    
    db = get_db_wrapper()
    test = db.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    
    if not test:
        flash('Test not found')
        return redirect(url_for('index'))
    
    # Get all submissions for this test
    test_submissions = db.execute(
        'SELECT * FROM submissions WHERE test_id = ? ORDER BY score DESC',
        (test_id,)
    ).fetchall()
    
    # Get best submission per user
    user_best = {}
    for sub in test_submissions:
        username = sub['username']
        if username not in user_best:
            user_best[username] = sub
    
    # Sort by score (descending for accuracy, ascending for RMSE/MAE)
    leaderboard_data = list(user_best.values())
    if test['metric'] in ['rmse', 'mae']:
        leaderboard_data.sort(key=lambda x: x['score'])
    else:
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Username', 'Score', 'Timestamp'])
    for idx, entry in enumerate(leaderboard_data, 1):
        writer.writerow([idx, entry['username'], entry['score'], entry['timestamp']])
    
    from flask import make_response
    csv_output = output.getvalue()
    response = make_response(csv_output)
    response.headers['Content-Disposition'] = f'attachment; filename=leaderboard_{test["name"].replace(" ", "_")}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def _parse_id_value_csv(csv_text, label):
    """Parse a two-column (id, value) CSV into a dict, raising ValueError on
    any structural or numeric problem so the caller can report it."""
    reader = csv.DictReader(StringIO(csv_text))
    cols = reader.fieldnames
    if not cols or len(cols) < 2:
        raise ValueError(f'{label} must have at least two columns (id, value).')

    data = {}
    # Row numbering starts at 2 to account for the header row.
    for line_no, row in enumerate(reader, start=2):
        key = row[cols[0]]
        raw = row[cols[1]]
        try:
            data[key] = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{label} row {line_no}: '{raw}' is not a number.")

    if not data:
        raise ValueError(f'{label} contains no data rows.')
    return data


def calculate_score(predictions_csv, ground_truth_csv, metric):
    """Calculate a score for the given metric.

    Returns a (score, error) tuple. On success error is None; on any
    validation problem score is None and error is a human-readable message.
    """
    if not ground_truth_csv:
        return None, 'This test has no ground truth file configured yet.'

    try:
        truth_data = _parse_id_value_csv(ground_truth_csv, 'Ground truth')
        pred_data = _parse_id_value_csv(predictions_csv, 'Prediction')
    except ValueError as e:
        return None, str(e)

    missing = [k for k in truth_data if k not in pred_data]
    if missing:
        sample = ', '.join(str(k) for k in missing[:3])
        return None, (f'Prediction is missing values for {len(missing)} of '
                      f'{len(truth_data)} IDs (e.g. {sample}).')

    if metric == 'accuracy':
        correct = sum(1 for k in truth_data
                      if round(pred_data[k]) == round(truth_data[k]))
        return correct / len(truth_data), None

    elif metric == 'rmse':
        import math
        mse = sum((pred_data[k] - truth_data[k]) ** 2 for k in truth_data) / len(truth_data)
        return math.sqrt(mse), None

    elif metric == 'mae':
        mae = sum(abs(pred_data[k] - truth_data[k]) for k in truth_data) / len(truth_data)
        return mae, None

    return None, f"Unknown metric '{metric}'."


if __name__ == '__main__':
    # Use PORT from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 to accept external connections
    app.run(host='0.0.0.0', port=port, debug=False)
