from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token, jwt_required, get_jwt_identity
from models import db, User
from models import TokenBlocklist
from flask_jwt_extended import get_jwt

auth_bp = Blueprint('auth', __name__)

# --- REGISTER ROUTE ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "User already exists"}), 400
        
    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(
        email=data['email'],
        password=hashed_pw,
        role=data['role'] # 'seeker' or 'employer'
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

# --- LOGIN ROUTE ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and check_password_hash(user.password, data.get('password')):
        # Access token: Used for every request (e.g., lasts 15 mins)
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={"role": user.role}
        )
        
        # Refresh token: Used ONLY to get a new access token (e.g., lasts 30 days)
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "role": user.role
        }), 200

    return jsonify({"msg": "Invalid email or password"}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Strict check: only accepts the Refresh Token
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Create a brand new access token using the user's stored role
    new_access_token = create_access_token(
        identity=str(current_user_id), 
        additional_claims={"role": user.role}
    )
    
    return jsonify({"access_token": new_access_token}), 200

from flask_jwt_extended import get_jti

@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    
    # Add the token's unique ID to our blocklist
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    
    return jsonify({"msg": "Access token revoked"}), 200