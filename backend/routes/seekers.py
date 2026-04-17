import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, User
from flask import current_app

seeker_bp = Blueprint('seeker', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@seeker_bp.route('/upload-resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    if file and allowed_file(file.filename):
        user_id = get_jwt_identity()
        filename = secure_filename(f"user_{user_id}_{file.filename}")
        
        # Ensure the directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Update user record in database
        user = User.query.get(user_id)

        # If user already has a resume, delete the old file first
        if user.resume_path and os.path.exists(user.resume_path):
            os.remove(user.resume_path)

        # Proceed to save the NEW file
        file.save(file_path)
        
        user.resume_path = file_path
        db.session.commit()

        return jsonify({"msg": "Resume uploaded successfully", "path": file_path}), 200
    
    return jsonify({"msg": "File type not allowed"}), 400


@seeker_bp.route('/delete-resume', methods=['DELETE'])
@jwt_required()
def delete_resume():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Check if the user even has a resume uploaded
    if not user.resume_path:
        return jsonify({"msg": "No resume found to delete"}), 404

    try:
        # 1. Delete the physical file from the folder
        if os.path.exists(user.resume_path):
            os.remove(user.resume_path)
        
        # 2. Clear the path in the database
        user.resume_path = None
        db.session.commit()

        return jsonify({"msg": "Resume deleted successfully"}), 200

    except Exception as e:
        return jsonify({"msg": f"Error deleting file: {str(e)}"}), 500
    

from flask import send_from_directory

@seeker_bp.route('/download-my-resume', methods=['GET'])
@jwt_required()
def download_my_resume():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if not user.resume_path:
        return jsonify({"msg": "No resume found"}), 404

    # Extract directory and filename from the stored path
    directory = os.path.dirname(user.resume_path)
    filename = os.path.basename(user.resume_path)
    
    return send_from_directory(directory, filename)