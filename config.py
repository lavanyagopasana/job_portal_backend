import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
import datetime

# Load variables from .env
load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY') # For session/cookies

    # 1. How long the access token lasts (e.g., 15 minutes)
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    
    # 2. How long the refresh token lasts (e.g., 30 days)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)

    UPLOAD_FOLDER = 'uploads/resumes'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit