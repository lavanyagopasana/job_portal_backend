import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Job, Application, User
from flask_jwt_extended import get_jwt

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/<int:job_id>/applicants', methods=['GET'])
@jwt_required()
def view_applicants(job_id):
    employer_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "employer":
        return jsonify({"msg": "Unauthorized access"}), 403

    # Ensure the job belongs to this employer
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if not job:
        return jsonify({"msg": "Job not found or unauthorized"}), 404

    # Fetch applications and join with User table to get resume paths
    applicants = []
    for app in job.applications:
        applicants.append({
            "application_id": app.id,
            "seeker_email": app.applicant.email,
            "status": app.status,
            "resume_url": f"/seeker/download/{os.path.basename(app.applicant.resume_path)}" if app.applicant.resume_path else None,
            "applied_on": app.applied_on
        })

    return jsonify(applicants), 200