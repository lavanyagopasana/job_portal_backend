# 🚀 Job Portal Backend API

A secure, relational backend built with **Python Flask** and **MySQL**, designed to handle job postings, seeker applications, and role-based authentication.

---

## 🛠 Tech Stack
* **Language:** Python 3.13.5
* **Framework:** Flask
* **Database:** MySQL
* **ORM:** SQLAlchemy
* **Security:** JWT (JSON Web Tokens) & Password Hashing (Bcrypt)



---
## ⚙️ Setup Instructions

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd job_portal_backend
```

### 2. Virtual Environment
Bash
```
python -m venv venv
```
 Windows
```
venv\Scripts\activate
```
 Mac/Linux
```
source venv/bin/activate
```

### 3. Install Dependencies
Bash
```
pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Migrate Flask-CORS PyMySQL python-dotenv
```
### 4. Configuration (.env)
Create a .env file in the root folder and add your credentials
```
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost/job_db
JWT_SECRET_KEY=generate_a_random_secret_here
SECRET_KEY=another_random_secret
```
### 5. Database Migrations
Run these commands to create the tables in your MySQL database:
Bash
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
## 📡 API Endpoints
### 🔑Authentication
| Method | Endpoint |Description |Access|
|:---|:---:|:---:|:---:|
|POST |/auth/register |Create a new user account |Public
|POST |/auth/login |Returns JWT access token |Public
### 💼Jobs 
| Method | Endpoint |Description |Access|
|:---|:---:|:---:|:---:|
|GET |/jobs/ |List all jobs (supports ?location= filter) |Public
|POST |/jobs/ |Create a new job post |Employer Only
### 📝Applications
| Method | Endpoint |Description |Access|
|:---|:---:|:---:|:---:|
|POST |/applications/apply/<id> |Apply for a specific job |Seeker Only
|GET |/applications/my-applications |View all jobs applied to |Seeker Only

## 🧪 Testing with Postman
* Register a user with the role employer.
* Login to receive the access_token.
* In your next request (e.g., Post a Job), go to the Authorization tab.
* Select Bearer Token and paste the JWT.
* Send your request and check the database!

## 📂 Project Structure
```
├── routes/             # API Endpoints (auth.py, jobs.py, applications.py)
├── models.py           # SQLAlchemy Database Schema
├── config.py           # Configuration classes
├── app.py              # Application Entry Point & Blueprint Registration
├── .env                # Secret Keys (Excluded from Git)
└── requirements.txt    # Python Dependencies
```
## 🔒 Security Features
* **Password Hashing** : Passwords are never stored in plain text.
* **JWT Identity** : User ID and Role are encoded within tokens.
* **CORS Enabled** : Ready to be connected to a React/Vue/Angular frontend.
