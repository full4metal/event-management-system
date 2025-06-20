from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, authenticate_user, create_user_with_profile
from functools import wraps

main_bp = Blueprint('main', __name__)

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# Main routes
@main_bp.route('/')
def index():
    current_user = get_current_user()
    return render_template('index.html', current_user=current_user)

@main_bp.route('/about')
def about():
    current_user = get_current_user()
    return render_template('about.html', current_user=current_user)

@main_bp.route('/contact')
def contact():
    current_user = get_current_user()
    return render_template('contact.html', current_user=current_user)

# Authentication routes
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect_to_dashboard()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')
        
        user = authenticate_user(email, password)
        if user:
            # Create session
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['email'] = user.email
            
            # Get user profile info
            profile = user.get_profile()
            if profile:
                session['user_name'] = profile.name
            else:
                session['user_name'] = user.email
            
            # Set session permanent if remember me is checked
            if remember_me:
                session.permanent = True
            
            flash(f'Welcome back, {session["user_name"]}!', 'success')
            
            # Redirect to appropriate dashboard
            return redirect_to_dashboard()
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect_to_dashboard()
    
    if request.method == 'POST':
        # Get basic form data
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        name = request.form.get('name')
        
        # Validation
        if not all([email, password, confirm_password, role, name]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('auth/register.html')
        
        if role not in ['customer', 'organizer']:
            flash('Invalid role selected', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        from models import get_user_by_email
        if get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create profile data based on role
        profile_data = {'name': name}
        
        if role == 'organizer':
            profile_data['organization_name'] = request.form.get('organization_name', '')
            profile_data['phone'] = request.form.get('phone', '')
            profile_data['bio'] = request.form.get('bio', '')
        elif role == 'customer':
            profile_data['phone'] = request.form.get('phone', '')
            profile_data['address'] = request.form.get('address', '')
            profile_data['preferences'] = request.form.get('preferences', '')
        
        try:
            user = create_user_with_profile(email, password, role, profile_data)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('auth/register.html')

@main_bp.route('/logout')
@login_required
def logout():
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye {user_name}! You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirect to appropriate dashboard based on user role"""
    return redirect_to_dashboard()

def redirect_to_dashboard():
    """Helper function to redirect to appropriate dashboard"""
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'organizer':
        return redirect(url_for('organizer.dashboard'))
    elif role == 'customer':
        return redirect(url_for('customer.dashboard'))
    else:
        flash('Invalid user role', 'danger')
        return redirect(url_for('main.logout'))

# Context processor to make current user available in all templates
@main_bp.app_context_processor
def inject_user():
    return dict(current_user=get_current_user())
