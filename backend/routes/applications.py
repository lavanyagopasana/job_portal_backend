from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Application, Job, User
import os
from flask import send_from_directory

apps_bp = Blueprint('applications', __name__)

# --- 1. APPLY FOR A JOB (Seeker Only) ---
@apps_bp.route('/apply/<int:job_id>', methods=['POST'])
@jwt_required()
def apply_to_job(job_id):
    claims = get_jwt()
    
    # Security: Only seekers can apply
    if claims.get("role") != "seeker":
        return jsonify({"msg": "Only seekers can apply for jobs"}), 403
    
    user_id = get_jwt_identity()
    
    # Check if job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"msg": "Job not found"}), 404
    
    # Check if already applied
    existing_app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing_app:
        return jsonify({"msg": "You have already applied for this job"}), 400
    
    new_application = Application(
        user_id=user_id,
        job_id=job_id
    )
    
    db.session.add(new_application)
    db.session.commit()
    
    return jsonify({"msg": "Application submitted successfully"}), 201

# --- 2. VIEW MY APPLICATIONS (Seeker Only) ---
@apps_bp.route('/my-applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    user_id = get_jwt_identity()
    apps = Application.query.filter_by(user_id=user_id).all()
    
    output = []
    for app in apps:
        output.append({
            "application_id": app.id,
            "job_title": app.job.title,  # Using the 'job' backref from models
            "status": app.status,
            "applied_on": app.applied_on
        })
    return jsonify(output), 200


@apps_bp.route('/download-resume/<int:user_id>', methods=['GET'])
@jwt_required()
def secure_employer_download(user_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    # 1. Fetch the seeker
    seeker = User.query.get_or_404(user_id)

    # 2. Authorization Logic
    if role == 'seeker':
        # Seekers can only download their own resume
        if current_user_id != user_id:
            return jsonify({"msg": "Permission denied"}), 403
    
    elif role == 'employer':
        # Check if the seeker has applied to ANY job owned by this employer
        # This joins Application and Job to verify ownership
        application_exists = db.session.query(Application).join(Job).filter(
            Application.user_id == user_id,
            Job.employer_id == current_user_id
        ).first()

        if not application_exists:
            return jsonify({"msg": "You do not have permission to view this resume"}), 403
    
    else:
        return jsonify({"msg": "Unauthorized role"}), 403

    # 3. Serve the file if checks pass
    if not seeker.resume_path:
        return jsonify({"msg": "Resume not found"}), 404

    directory = os.path.dirname(seeker.resume_path)
    filename = os.path.basename(seeker.resume_path)
    
    return send_from_directory(directory, filename, as_attachment=True)


@apps_bp.route('/job/<int:job_id>/applicants', methods=['GET'])
@jwt_required()
def get_job_applicants(job_id):
    employer_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "employer":
        return jsonify({"msg": "Unauthorized"}), 403

    # Ensure the job belongs to the current employer
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first_or_404()

    applicants = []
    for app in job.applications:
        applicants.append({
            "application_id": app.id,
            "seeker_email": app.applicant.email,
            "seeker_id": app.user_id,
            "status": app.status,
            "resume_url": f"/applications/download-resume/{app.user_id}"
        })

    return jsonify({"job_title": job.title, "applicants": applicants}), 200


@apps_bp.route('/update-status/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    employer_id = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get("role") != "employer":
        return jsonify({"msg": "Only employers can update status"}), 403
    
    data = request.get_json()
    new_status = data.get('status') # Expected: 'accepted', 'rejected', or 'pending'
    
    if new_status not in ['accepted', 'rejected', 'pending']:
        return jsonify({"msg": "Invalid status"}), 400

    # Find the application AND ensure the job belongs to this employer
    application = Application.query.join(Job).filter(
        Application.id == app_id, 
        Job.employer_id == employer_id
    ).first_or_404()

    application.status = new_status
    db.session.commit()

    return jsonify({"msg": f"Application status updated to {new_status}"}), 200