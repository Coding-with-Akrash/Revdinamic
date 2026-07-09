# Auth routes
from flask import request, session, jsonify
import secrets
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict

USERS: Dict[str, Dict] = {}
VERIFICATION_TOKENS: Dict[str, Dict] = {}
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def register():
    data = request.get_json() or request.form.to_dict()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    account_type = data.get('accountType', 'owner')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if email in USERS:
        return jsonify({'error': 'User already exists'}), 400
    
    for token, v in list(VERIFICATION_TOKENS.items()):
        if v['email'] == email:
            return jsonify({
                'error': 'User exists but not verified. Check your email or request new verification.',
                'needsVerification': True,
                'verificationUrl': f'/api/verify-email?token={token}'
            }), 400
    
    token = secrets.token_urlsafe(32)
    VERIFICATION_TOKENS[token] = {
        'email': email,
        'password': generate_password_hash(password),
        'name': name,
        'accountType': account_type,
        'expires': datetime.now() + timedelta(hours=24)
    }
    
    return jsonify({
        'success': True,
        'message': 'Registration successful! Check your email for verification link.',
        'verificationToken': token,
        'verificationUrl': f'/api/verify-email?token={token}'
    }), 201

def verify_email():
    token = request.args.get('token') if request.method == 'GET' else (request.get_json() or {}).get('token')
    
    if not token:
        return jsonify({'error': 'Verification token required'}), 400
    
    verification = VERIFICATION_TOKENS.get(token)
    if not verification:
        return jsonify({'error': 'Invalid or expired verification token'}), 400
    
    if verification['expires'] < datetime.now():
        del VERIFICATION_TOKENS[token]
        return jsonify({'error': 'Verification token expired'}), 400
    
    email = verification['email']
    USERS[email] = {
        'email': email,
        'password': verification['password'],
        'name': verification['name'],
        'accountType': verification['accountType'],
        'vehicles': [],
        'emailVerified': True,
        'createdAt': str(datetime.now().isoformat())
    }
    del VERIFICATION_TOKENS[token]
    
    return jsonify({'success': True, 'message': 'Email verified successfully! You can now log in.'})

def login():
    data = request.get_json() or request.form.to_dict()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    user = USERS.get(email)
    if not user:
        for token, v in VERIFICATION_TOKENS.items():
            if v['email'] == email:
                return jsonify({'error': 'Email not verified. Check your inbox or request a new verification link.', 'needsVerification': True, 'verificationUrl': f'/api/verify-email?token={token}'}), 403
        return jsonify({'error': 'User not found'}), 401
    
    if not user.get('emailVerified'):
        return jsonify({'error': 'Email not verified. Check your inbox for verification link.', 'needsVerification': True}), 403
    
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = email
    return jsonify({'success': True, 'user': {'email': email, 'name': user['name'], 'accountType': user['accountType']}})

def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

def resend_verification():
    email = (request.get_json() or {}).get('email', '').lower().strip()
    
    if email in USERS and USERS[email].get('emailVerified'):
        return jsonify({'message': 'Email already verified'})
    
    existing = None
    existing_token = None
    for token, v in VERIFICATION_TOKENS.items():
        if v['email'] == email:
            existing = v
            existing_token = token
            break
    
    if not existing:
        return jsonify({'error': 'User not found'}), 404
    
    new_token = secrets.token_urlsafe(32)
    VERIFICATION_TOKENS[new_token] = {
        **existing,
        'expires': datetime.now() + timedelta(hours=24)
    }
    del VERIFICATION_TOKENS[existing_token]
    
    return jsonify({'success': True, 'verificationUrl': f'/api/verify-email?token={new_token}'})