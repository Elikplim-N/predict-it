"""Student submission endpoint"""
from flask import Flask, request, jsonify, session
from datetime import datetime
import os
import sys
import base64

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.db_helper import (
    get_active_ground_truth, 
    create_submission,
    get_user_submissions,
    get_user_best_score,
    get_column_settings
)
from api.rmse_calculator import calculate_rmse

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/api/submit', methods=['POST'])
def submit_prediction():
    """Handle student CSV submission and calculate RMSE"""
    try:
        # Check authentication
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get file from request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files allowed'}), 400
        
        # Read CSV content
        csv_content = file.read().decode('utf-8')
        
        # Get active ground truth
        ground_truth = get_active_ground_truth()
        if not ground_truth:
            return jsonify({'error': 'No ground truth available. Contact admin.'}), 400
        
        # Get column settings
        settings = get_column_settings()
        
        # Calculate RMSE
        rmse, error = calculate_rmse(
            csv_content,
            ground_truth['file_data'],
            settings['id_column'],
            settings['value_column']
        )
        
        if error:
            return jsonify({'error': f'Error calculating RMSE: {error}'}), 400
        
        # Save submission
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"user_{session['user_id']}_{timestamp}.csv"
        
        submission = create_submission(session['user_id'], filename, rmse)
        
        return jsonify({
            'message': 'Submission successful',
            'rmse': round(rmse, 6),
            'submission_id': submission['id'],
            'submission_date': submission['submission_date']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get user's submissions"""
    try:
        # Check authentication
        if 'user_id' not in session or session.get('user_type') != 'student':
            return jsonify({'error': 'Not authenticated'}), 401
        
        submissions = get_user_submissions(session['user_id'])
        best_score = get_user_best_score(session['user_id'])
        
        return jsonify({
            'submissions': submissions,
            'best_score': best_score
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
