import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from config import Config
from models import db
from flask_migrate import Migrate

# 1. Load env and create app
load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

# 2. Critical: Ensure the Secret Key is set in config
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# 3. Initialize Extensions
jwt = JWTManager(app) 
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# --- ADD THIS HERE FOR RENDER FREE TIER ---
with app.app_context():
    db.create_all()
    print("Database tables created/verified successfully!")
# ------------------------------------------

# 4. Import and Register Blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.applications import apps_bp
from routes.seekers import seeker_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(jobs_bp, url_prefix='/jobs')
app.register_blueprint(apps_bp, url_prefix='/applications')
app.register_blueprint(seeker_bp, url_prefix='/seeker')

from models import TokenBlocklist

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

if __name__ == "__main__":
    # This block only runs during LOCAL development
    app.run(debug=True)

# import os
# from flask import Flask
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv

# from config import Config
# from models import db
# from flask_migrate import Migrate

# # 1. Load env and create app
# load_dotenv()
# app = Flask(__name__)
# app.config.from_object(Config)

# # 2. Critical: Ensure the Secret Key is set in config
# # If Config doesn't already have it, this line is mandatory
# app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# # 3. Initialize Extensions FIRST
# jwt = JWTManager(app) 
# db.init_app(app)
# migrate = Migrate(app, db)
# CORS(app)

# # 4. Import and Register Blueprints LAST
# # (Importing inside the function or after init prevents circular imports)
# from routes.auth import auth_bp
# from routes.jobs import jobs_bp
# from routes.applications import apps_bp
# from routes.seekers import seeker_bp

# app.register_blueprint(auth_bp, url_prefix='/auth')
# app.register_blueprint(jobs_bp, url_prefix='/jobs')
# app.register_blueprint(apps_bp, url_prefix='/applications')
# app.register_blueprint(seeker_bp, url_prefix='/seeker')

# from models import TokenBlocklist

# # Callback function to check if a JWT exists in the database blocklist
# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token = TokenBlocklist.query.filter_by(jti=jti).first()
#     return token is not None

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print("Database tables created successfully!")
#     app.run(debug=True)

