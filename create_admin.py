from flask import Flask
from models import db, User, Admin, get_user_by_email
import os

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/event_management'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only-change-in-production')
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def create_admin_user(email, password, name):
    """Create an admin user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            if existing_user.role == 'admin':
                print(f"Admin user {email} already exists.")
                return existing_user
            else:
                print(f"User {email} exists but is not an admin. Please use a different email.")
                return None
        
        # Create user with admin role
        user = User(email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user_id without committing
        
        # Create admin profile
        admin = Admin(admin_id=user.user_id, name=name)
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user {email} created successfully!")
        return user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")
        return None

if __name__ == "__main__":
    # Create Flask app context
    app = create_app()
    
    # Admin credentials
    admin_email = "admin@gmail.com"
    admin_password = "admin123"
    admin_name = "System Administrator"
    
    with app.app_context():
        # Create admin user
        create_admin_user(admin_email, admin_password, admin_name)
        
        # Verify admin was created
        admin = get_user_by_email(admin_email)
        if admin and admin.role == 'admin':
            print("\nAdmin Account Details:")
            print("----------------------")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
            print(f"Name: {admin_name}")
            print(f"Role: {admin.role}")
            print("\nYou can now log in with these credentials at: http://localhost:5000/login")
