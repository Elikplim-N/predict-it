"""Authentication endpoints for students"""
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from api.db_helper import get_user_by_index, create_user

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new student"""
    try:
        data = request.get_json()
        student_index = data.get('student_index')
        password = data.get('password')
        name = data.get('name')
        
        if not all([student_index, password, name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        existing_user = get_user_by_index(student_index)
        if existing_user:
            return jsonify({'error': 'Student index already exists'}), 409
        
        # Create user
        password_hash = generate_password_hash(password)
        user = create_user(student_index, password_hash, name)
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user['id']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Student login"""
    try:
        data = request.get_json()
        student_index = data.get('student_index')
        password = data.get('password')
        
        if not all([student_index, password]):
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Get user
        user = get_user_by_index(student_index)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_id'] = user['id']
        session['student_index'] = user['student_index']
        session['user_type'] = 'student'
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user['id'],
            'student_index': user['student_index'],
            'name': user['name']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
