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

# Fixed admin credentials - cannot be changed via signup
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
ADMIN_HASH = generate_password_hash(ADMIN_PASSWORD)

DATABASE = 'predict_it.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
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

@app.route('/')
def index():
    db = get_db()
    tests = db.execute('SELECT * FROM tests ORDER BY id DESC').fetchall()
    return render_template('index.html', tests=tests)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        db = get_db()
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
        db = get_db()
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
    
    db = get_db()
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
    
    db = get_db()
    db.execute('INSERT INTO tests (name, description, start_date, end_date, metric, ground_truth) VALUES (?, ?, ?, ?, ?, ?)',
               (name, description, start_date, end_date, metric, ground_truth))
    db.commit()
    
    flash('Test created successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/test/<int:test_id>')
def test_detail(test_id):
    db = get_db()
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
    
    db = get_db()
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
    
    content = file.read().decode('utf-8')
    score = calculate_score(content, test['ground_truth'], test['metric'])
    
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
    
    db = get_db()
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

def calculate_score(predictions_csv, ground_truth_csv, metric):
    """Calculate score based on metric type"""
    if not ground_truth_csv:
        return 0.0
    
    try:
        pred_reader = csv.DictReader(StringIO(predictions_csv))
        truth_reader = csv.DictReader(StringIO(ground_truth_csv))
        
        pred_data = {row['id']: float(row['prediction']) for row in pred_reader}
        truth_data = {row['id']: float(row['target']) for row in truth_reader}
        
        if metric == 'accuracy':
            correct = sum(1 for k in pred_data if k in truth_data and 
                         round(pred_data[k]) == round(truth_data[k]))
            return correct / len(truth_data) if truth_data else 0.0
        
        elif metric == 'rmse':
            import math
            mse = sum((pred_data.get(k, 0) - truth_data[k])**2 for k in truth_data)
            return math.sqrt(mse / len(truth_data)) if truth_data else 0.0
        
        elif metric == 'mae':
            mae = sum(abs(pred_data.get(k, 0) - truth_data[k]) for k in truth_data)
            return mae / len(truth_data) if truth_data else 0.0
    
    except Exception as e:
        print(f"Error calculating score: {e}")
        return 0.0
    
    return 0.0


if __name__ == '__main__':
    # Initialize database
    init_db()
    # Use PORT from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 to accept external connections
    app.run(host='0.0.0.0', port=port, debug=False)
