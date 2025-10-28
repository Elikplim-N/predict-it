import os
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# In-memory storage (replace with database for production)
users = {}
competitions = {}
submissions = {}

# Admin credentials (username: admin, password: admin123)
ADMIN_HASH = generate_password_hash('admin123')

@app.route('/')
def index():
    return render_template('index.html', competitions=competitions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if username in users:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        users[username] = {
            'password': generate_password_hash(password),
            'email': email,
            'is_admin': False
        }
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check admin login
        if username == 'admin' and check_password_hash(ADMIN_HASH, password):
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        
        # Check regular user login
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            session['is_admin'] = users[username]['is_admin']
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
    
    return render_template('admin.html', competitions=competitions, submissions=submissions)

@app.route('/admin/create_competition', methods=['POST'])
def create_competition():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    comp_id = str(len(competitions) + 1)
    competitions[comp_id] = {
        'id': comp_id,
        'name': request.form['name'],
        'description': request.form['description'],
        'start_date': request.form['start_date'],
        'end_date': request.form['end_date'],
        'metric': request.form['metric'],
        'ground_truth': None
    }
    
    # Handle ground truth file upload
    if 'ground_truth' in request.files:
        file = request.files['ground_truth']
        if file and file.filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            competitions[comp_id]['ground_truth'] = content
    
    flash('Competition created successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/competition/<comp_id>')
def competition_detail(comp_id):
    if comp_id not in competitions:
        flash('Competition not found')
        return redirect(url_for('index'))
    
    comp = competitions[comp_id]
    comp_submissions = [s for s in submissions.values() if s['competition_id'] == comp_id]
    
    return render_template('competition.html', competition=comp, submissions=comp_submissions)

@app.route('/competition/<comp_id>/submit', methods=['POST'])
def submit_prediction(comp_id):
    if 'username' not in session:
        flash('Please login to submit')
        return redirect(url_for('login'))
    
    if comp_id not in competitions:
        flash('Competition not found')
        return redirect(url_for('index'))
    
    if 'prediction_file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('competition_detail', comp_id=comp_id))
    
    file = request.files['prediction_file']
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file')
        return redirect(url_for('competition_detail', comp_id=comp_id))
    
    content = file.read().decode('utf-8')
    score = calculate_score(content, competitions[comp_id]['ground_truth'], 
                          competitions[comp_id]['metric'])
    
    submission_id = str(len(submissions) + 1)
    submissions[submission_id] = {
        'id': submission_id,
        'competition_id': comp_id,
        'username': session['username'],
        'timestamp': datetime.now().isoformat(),
        'score': score,
        'filename': file.filename
    }
    
    flash(f'Submission successful! Score: {score:.4f}')
    return redirect(url_for('competition_detail', comp_id=comp_id))

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

@app.route('/leaderboard/<comp_id>')
def leaderboard(comp_id):
    if comp_id not in competitions:
        flash('Competition not found')
        return redirect(url_for('index'))
    
    comp_submissions = [s for s in submissions.values() if s['competition_id'] == comp_id]
    
    # Get best submission per user
    user_best = {}
    for sub in comp_submissions:
        username = sub['username']
        if username not in user_best or sub['score'] > user_best[username]['score']:
            user_best[username] = sub
    
    # Sort by score (descending)
    leaderboard_data = sorted(user_best.values(), key=lambda x: x['score'], reverse=True)
    
    return render_template('leaderboard.html', 
                         competition=competitions[comp_id], 
                         leaderboard=leaderboard_data)

if __name__ == '__main__':
    # Use PORT from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 to accept external connections
    app.run(host='0.0.0.0', port=port, debug=False)
