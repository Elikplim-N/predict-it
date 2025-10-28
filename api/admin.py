"""Admin endpoints for platform management"""
from flask import Flask, request, jsonify, session
from werkzeug.security import check_password_hash
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.db_helper import (
    get_admin,
    get_leaderboard,
    get_active_ground_truth,
    create_ground_truth,
    get_statistics,
    set_column_settings,
    get_column_settings
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Get admin
        admin = get_admin(username)
        if not admin:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(admin['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['admin_id'] = admin['id']
        session['user_type'] = 'admin'
        
        return jsonify({
            'message': 'Login successful',
            'admin_id': admin['id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/leaderboard', methods=['GET'])
def get_leaderboard_data():
    """Get competition leaderboard"""
    try:
        # Check admin authentication
        if 'admin_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': 'Not authenticated'}), 401
        
        leaderboard = get_leaderboard()
        stats = get_statistics()
        ground_truth = get_active_ground_truth()
        
        return jsonify({
            'leaderboard': leaderboard,
            'statistics': stats,
            'ground_truth': {
                'filename': ground_truth['filename'] if ground_truth else None,
                'upload_date': ground_truth['upload_date'] if ground_truth else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/upload_ground_truth', methods=['POST'])
def upload_ground_truth():
    """Upload ground truth CSV"""
    try:
        # Check admin authentication
        if 'admin_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get file from request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Read CSV content
        csv_content = file.read().decode('utf-8')
        
        # Validate it's a proper CSV with headers
        if not csv_content.strip():
            return jsonify({'error': 'Empty CSV file'}), 400
        
        # Save ground truth
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ground_truth_{timestamp}.csv"
        
        ground_truth = create_ground_truth(filename, csv_content)
        
        return jsonify({
            'message': 'Ground truth uploaded successfully',
            'filename': filename,
            'ground_truth_id': ground_truth['id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/configure_columns', methods=['POST'])
def configure_columns():
    """Configure CSV column names"""
    try:
        # Check admin authentication
        if 'admin_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        id_col = data.get('id_column', 'id')
        value_col = data.get('value_column', 'value')
        
        if not value_col:
            return jsonify({'error': 'Value column name is required'}), 400
        
        set_column_settings(id_col, value_col)
        
        return jsonify({
            'message': 'Column configuration updated',
            'id_column': id_col,
            'value_column': value_col
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET'])
def get_settings():
    """Get current column settings"""
    try:
        # Check admin authentication
        if 'admin_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': 'Not authenticated'}), 401
        
        settings = get_column_settings()
        
        return jsonify(settings), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export', methods=['GET'])
def export_leaderboard():
    """Export leaderboard as CSV"""
    try:
        # Check admin authentication
        if 'admin_id' not in session or session.get('user_type') != 'admin':
            return jsonify({'error': 'Not authenticated'}), 401
        
        leaderboard = get_leaderboard()
        
        # Create CSV content with headers (per user rule)
        csv_data = "Rank,Student Index,Name,Best RMSE,Submissions,Last Submission\\n"
        for idx, entry in enumerate(leaderboard, 1):
            csv_data += f"{idx},{entry['student_index']},\\\"{entry['name']}\\\",{entry['best_rmse']:.6f},{entry['submission_count']},{entry['last_submission']}\\n"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return jsonify({
            'csv_content': csv_data,
            'filename': f'predict-it-results-{timestamp}.csv'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
