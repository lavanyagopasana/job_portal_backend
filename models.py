from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    resume_path = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False) # 'seeker' or 'employer'
    
    # Relationships
    # If employer is deleted, delete their jobs too (cascade)
    jobs_posted = db.relationship('Job', backref='employer', cascade="all, delete-orphan", lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True) # Index for faster search
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), index=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    applications = db.relationship('Application', backref='job', cascade="all, delete-orphan", lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)