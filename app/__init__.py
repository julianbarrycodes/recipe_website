# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from markupsafe import Markup

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Add nl2br filter
@app.template_filter('nl2br')
def nl2br(value):
    return Markup(value.replace('\n', '<br>'))

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, '..', 'instance', 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure the upload folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Security headers
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Register CLI commands
from . import cli
cli.init_app(app)

# Import and register blueprints
from app import routes
app.register_blueprint(routes.main)

# Add test route inside create_app
@app.route('/test-security')
def test_security():
    return {
        'secret_key_set': bool(app.config['SECRET_KEY']),
        'session_cookie_secure': app.config['SESSION_COOKIE_SECURE'],
        'session_cookie_httponly': app.config['SESSION_COOKIE_HTTPONLY']
    }

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
