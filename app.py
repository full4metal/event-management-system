from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
import os
from datetime import timedelta

# Import blueprints
from routes.main import main_bp
from routes.organizer import organizer_bp
from routes.customer import customer_bp
from routes.admin import admin_bp
from routes.reports import reports_bp

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/event_management'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only-change-in-production')
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'events'), exist_ok=True)
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Remember me for 7 days
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(organizer_bp, url_prefix='/organizer')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
