from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Job

jobs_bp = Blueprint('jobs', __name__)

# --- 1. GET ALL JOBS (Public) ---
@jobs_bp.route('/', methods=['GET'])
def get_jobs():
    # Get search parameters from the URL
    title_query = request.args.get('title')
    location_query = request.args.get('location')

    # Start with all jobs
    query = Job.query

    # If user provided a title, filter by it (case-insensitive)
    if title_query:
        query = query.filter(Job.title.ilike(f'%{title_query}%'))

    # If user provided a location, filter by it
    if location_query:
        query = query.filter(Job.location.ilike(f'%{location_query}%'))

    jobs = query.all()
        
    results = []
    for job in jobs:
        results.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employer_id": job.employer_id
        })
    return jsonify(results), 200

# --- 2. POST A NEW JOB (Employer Only) ---
@jobs_bp.route('/', methods=['POST'])
@jwt_required() # This requires a valid JWT token
def create_job():
    claims = get_jwt() # Get the extra data we put in the token (role)
    
    # Check if the user is an employer
    if claims.get("role") != "employer":
        return jsonify({"msg": "Only employers can post jobs"}), 403
    
    data = request.get_json()
    user_id = get_jwt_identity() # Gets the user_id we stored in the token
    
    new_job = Job(
        title=data['title'],
        description=data['description'],
        location=data.get('location', 'Remote'),
        employer_id=user_id
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    return jsonify({"msg": "Job posted successfully", "job_id": new_job.id}), 201

@jobs_bp.route('/employer-dashboard', methods=['GET'])
@jwt_required()
def employer_dashboard():
    employer_id = get_jwt_identity()
    claims = get_jwt()
    
    # Security: Ensure only employers access this
    if claims.get("role") != "employer":
        return jsonify({"msg": "Unauthorized"}), 403
        
    # Fetch all jobs posted by this employer
    jobs = Job.query.filter_by(employer_id=employer_id).all()
    
    dashboard_data = []
    for job in jobs:
        # Count applications per status for quick stats
        total_apps = len(job.applications)
        pending_apps = len([a for a in job.applications if a.status == 'pending'])
        
        dashboard_data.append({
            "job_id": job.id,
            "title": job.title,
            "location": job.location,
            "total_applications": total_apps,
            "pending_reviews": pending_apps,
            "applicants_url": f"/applications/job/{job.id}/applicants"
        })
        
    return jsonify(dashboard_data), 200

@jobs_bp.route('/search', methods=['GET'])
def search_jobs():
    # Get search parameters
    title_query = request.args.get('title')
    location_query = request.args.get('location')
    
    # Get pagination parameters (defaults to page 1, 10 items per page)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Job.query

    if title_query:
        query = query.filter(Job.title.ilike(f"%{title_query}%"))
    
    if location_query:
        query = query.filter(Job.location.ilike(f"%{location_query}%"))

    # Use paginate instead of .all()
    # error_out=False prevents 404s if a user requests a page that doesn't exist
    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)
    jobs = pagination_obj.items

    output = []
    for job in jobs:
        output.append({
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "employer": job.employer.email
        })

    return jsonify({
        "jobs": output,
        "total_pages": pagination_obj.pages,
        "current_page": pagination_obj.page,
        "total_jobs": pagination_obj.total,
        "has_next": pagination_obj.has_next,
        "has_prev": pagination_obj.has_prev
    }), 200