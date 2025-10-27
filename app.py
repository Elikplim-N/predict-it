from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')  # Use env var in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    
    # Users table (students)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_index TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  name TEXT)''')
    
    # Ground truth table (admin uploads)
    c.execute('''CREATE TABLE IF NOT EXISTS ground_truth
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT NOT NULL,
                  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_active INTEGER DEFAULT 1)''')
    
    # Submissions table
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  filename TEXT NOT NULL,
                  rmse REAL,
                  submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
    
    # Settings table for column configuration
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  setting_key TEXT UNIQUE NOT NULL,
                  setting_value TEXT)''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM admin WHERE username = 'isaaceinst3in'")
    if not c.fetchone():
        admin_hash = generate_password_hash('12zaci')
        c.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                  ('isaaceinst3in', admin_hash))
    
    conn.commit()
    conn.close()

def get_column_settings():
    """Get column configuration from database"""
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    c.execute("SELECT setting_value FROM settings WHERE setting_key = 'id_column'")
    id_col = c.fetchone()
    c.execute("SELECT setting_value FROM settings WHERE setting_key = 'value_column'")
    value_col = c.fetchone()
    conn.close()
    
    return {
        'id_column': id_col[0] if id_col else 'id',
        'value_column': value_col[0] if value_col else 'value'
    }

def set_column_settings(id_col, value_col):
    """Save column configuration to database"""
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
              ('id_column', id_col))
    c.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
              ('value_column', value_col))
    conn.commit()
    conn.close()

def find_value_column(df, preferred_name):
    """Auto-detect numeric column if configured column doesn't exist"""
    # First try configured name
    if preferred_name in df.columns:
        return preferred_name
    
    # Try common variations
    common_names = ['prediction', 'value', 'output', 'target', 'y', 'predictions', 'values', 'outputs']
    for name in common_names:
        if name.lower() in [c.lower() for c in df.columns]:
            # Find case-insensitive match
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
    
    # Last resort: use last numeric column
    for col in reversed(df.columns):
        try:
            pd.to_numeric(df[col], errors='coerce').sum()
            return col
        except:
            pass
    
    return None

def find_id_column(df, preferred_name):
    """Auto-detect ID column if configured column doesn't exist"""
    # First try configured name
    if preferred_name in df.columns:
        return preferred_name
    
    # Try common ID column names
    common_names = ['id', 'index', 'sample_id', 'sample', 'record_id', 'idx']
    for name in common_names:
        if name.lower() in [c.lower() for c in df.columns]:
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
    
    # Use first column if it looks like ID
    if len(df.columns) > 1:
        return df.columns[0]
    return None

def calculate_rmse(predictions, ground_truth):
    """Calculate RMSE between predictions and ground truth"""
    try:
        pred_df = pd.read_csv(predictions)
        truth_df = pd.read_csv(ground_truth)
        
        # Get configured column names
        settings = get_column_settings()
        
        # Auto-detect columns
        value_col = find_value_column(pred_df, settings['value_column'])
        id_col = find_id_column(pred_df, settings['id_column'])
        
        if not value_col:
            return None, f"Could not find numeric column for values. Available columns: {', '.join(pred_df.columns)}"
        
        truth_value_col = find_value_column(truth_df, settings['value_column'])
        if not truth_value_col:
            return None, f"Could not find numeric column in ground truth. Available columns: {', '.join(truth_df.columns)}"
        
        # Try to align by ID column if found
        if id_col:
            truth_id_col = find_id_column(truth_df, settings['id_column'])
            if truth_id_col and id_col in pred_df.columns and truth_id_col in truth_df.columns:
                try:
                    pred_df = pred_df.sort_values(id_col).reset_index(drop=True)
                    truth_df = truth_df.sort_values(truth_id_col).reset_index(drop=True)
                except:
                    pass
        
        predictions_array = pd.to_numeric(pred_df[value_col], errors='coerce').values
        truth_array = pd.to_numeric(truth_df[truth_value_col], errors='coerce').values
        
        # Remove NaN values
        mask = ~(np.isnan(predictions_array) | np.isnan(truth_array))
        predictions_array = predictions_array[mask]
        truth_array = truth_array[mask]
        
        if len(predictions_array) == 0:
            return None, "No valid numeric values found in CSV files"
        
        if len(predictions_array) != len(truth_array):
            return None, f"Row count mismatch: {len(predictions_array)} predictions vs {len(truth_array)} ground truth values"
        
        rmse = np.sqrt(np.mean((predictions_array - truth_array) ** 2))
        return rmse, None
    except Exception as e:
        return None, f"Error processing CSV: {str(e)}"

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Student login"""
    if request.method == 'POST':
        student_index = request.form.get('student_index')
        password = request.form.get('password')
        
        conn = sqlite3.connect('competition.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE student_index = ?", (student_index,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['student_index'] = user[1]
            session['user_type'] = 'student'
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration"""
    if request.method == 'POST':
        student_index = request.form.get('student_index')
        password = request.form.get('password')
        name = request.form.get('name')
        
        conn = sqlite3.connect('competition.db')
        c = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            c.execute("INSERT INTO users (student_index, password_hash, name) VALUES (?, ?, ?)",
                      (student_index, password_hash, name))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Student index already exists', 'error')
    
    return render_template('register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('competition.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username = ?", (username,))
        admin = c.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin[2], password):
            session['admin_id'] = admin[0]
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard - view submissions"""
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    c.execute("""SELECT filename, rmse, submission_date 
                 FROM submissions 
                 WHERE user_id = ? 
                 ORDER BY submission_date DESC""", (session['user_id'],))
    submissions = c.fetchall()
    
    # Get best score
    c.execute("""SELECT MIN(rmse) FROM submissions WHERE user_id = ?""", (session['user_id'],))
    best_score = c.fetchone()[0]
    
    conn.close()
    
    return render_template('student_dashboard.html', 
                           submissions=submissions, 
                           best_score=best_score,
                           student_index=session['student_index'])

@app.route('/student/upload', methods=['POST'])
def upload_prediction():
    """Handle student CSV upload"""
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('student_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('student_dashboard'))
    
    if not file.filename.endswith('.csv'):
        flash('Only CSV files allowed', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get active ground truth
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM ground_truth WHERE is_active = 1 ORDER BY upload_date DESC LIMIT 1")
    ground_truth = c.fetchone()
    
    if not ground_truth:
        conn.close()
        flash('No ground truth available. Contact admin.', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"user_{session['user_id']}_{timestamp}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Calculate RMSE
    ground_truth_path = os.path.join(app.config['UPLOAD_FOLDER'], ground_truth[0])
    rmse, error = calculate_rmse(filepath, ground_truth_path)
    
    if error:
        os.remove(filepath)
        conn.close()
        flash(f'Error calculating RMSE: {error}', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Save submission
    c.execute("INSERT INTO submissions (user_id, filename, rmse) VALUES (?, ?, ?)",
              (session['user_id'], filename, rmse))
    conn.commit()
    conn.close()
    
    flash(f'Submission successful! RMSE: {rmse:.6f}', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with leaderboard"""
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    
    # Get leaderboard - best RMSE per student
    c.execute("""
        SELECT u.student_index, u.name, MIN(s.rmse) as best_rmse, 
               COUNT(s.id) as submission_count,
               MAX(s.submission_date) as last_submission
        FROM users u
        LEFT JOIN submissions s ON u.id = s.user_id
        WHERE s.rmse IS NOT NULL
        GROUP BY u.id
        ORDER BY best_rmse ASC
    """)
    leaderboard = c.fetchall()
    
    # Get ground truth status
    c.execute("SELECT filename, upload_date FROM ground_truth WHERE is_active = 1 ORDER BY upload_date DESC LIMIT 1")
    ground_truth = c.fetchone()
    
    # Get total stats
    c.execute("SELECT COUNT(*) FROM users")
    total_students = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM submissions")
    total_submissions = c.fetchone()[0]
    
    conn.close()
    
    # Get column settings
    settings = get_column_settings()
    
    return render_template('admin_dashboard.html', 
                           leaderboard=leaderboard,
                           ground_truth=ground_truth,
                           total_students=total_students,
                           total_submissions=total_submissions,
                           settings=settings)

@app.route('/admin/configure_columns', methods=['POST'])
def configure_columns():
    """Configure CSV column names"""
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Not authenticated'}), 401
    
    id_col = request.form.get('id_column', 'id')
    value_col = request.form.get('value_column', 'value')
    
    if not value_col:
        flash('Value column name is required', 'error')
        return redirect(url_for('admin_dashboard'))
    
    set_column_settings(id_col, value_col)
    flash(f'Column configuration updated: ID column = "{id_col}", Value column = "{value_col}"', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/upload_ground_truth', methods=['POST'])
def upload_ground_truth():
    """Admin upload ground truth CSV"""
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        flash('Invalid file', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ground_truth_{timestamp}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Deactivate old ground truths
    conn = sqlite3.connect('competition.db')
    c = conn.cursor()
    c.execute("UPDATE ground_truth SET is_active = 0")
    
    # Add new ground truth
    c.execute("INSERT INTO ground_truth (filename, is_active) VALUES (?, 1)", (filename,))
    conn.commit()
    conn.close()
    
    flash('Ground truth uploaded successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # Use PORT from environment variable (for cloud hosting) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Debug mode only for local development
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
