from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Event, Booking, Category, Feedback, Payment, Admin
from functools import wraps
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

# Authentication decorator for admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('main.login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_organizers = User.query.filter_by(role='organizer').count()
    total_customers = User.query.filter_by(role='customer').count()
    total_events = Event.query.count()
    pending_events = Event.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Booking.total_amount))\
                    .filter(Booking.status == 'booked').scalar() or 0
    
    # Get recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_time.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          total_organizers=total_organizers,
                          total_customers=total_customers,
                          total_events=total_events,
                          pending_events=pending_events,
                          total_bookings=total_bookings,
                          total_revenue=total_revenue,
                          recent_events=recent_events,
                          recent_bookings=recent_bookings)

@admin_bp.route('/users')
@admin_required
def users():
    # Get all users
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_details.html', user=user)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # In a real app, you would have a status field to toggle
    # For now, we'll just show a message
    flash(f'User status toggled for {user.email}', 'success')
    return redirect(url_for('admin.user_details', user_id=user_id))

@admin_bp.route('/events')
@admin_required
def events():
    # Get filter parameters
    status = request.args.get('status', 'all')
    
    # Filter events based on status
    if status != 'all':
        events = Event.query.filter_by(status=status).order_by(Event.created_at.desc()).all()
    else:
        events = Event.query.order_by(Event.created_at.desc()).all()
    
    return render_template('admin/events.html', events=events, current_status=status)

@admin_bp.route('/events/<int:event_id>')
@admin_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Get bookings for this event
    bookings = Booking.query.filter_by(event_id=event_id).all()
    
    # Get feedback for this event
    feedback = Feedback.query.filter_by(event_id=event_id).all()
    
    return render_template('admin/event_details.html', 
                          event=event, 
                          bookings=bookings,
                          feedback=feedback)

@admin_bp.route('/events/<int:event_id>/approve', methods=['POST'])
@admin_required
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.status == 'pending' or event.status == 'rejected':
        event.status = 'approved'
        try:
            db.session.commit()
            flash(f'Event "{event.title}" has been approved successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error approving event: {str(e)}', 'danger')
    else:
        flash('Event is not in a state that can be approved', 'warning')
    
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/<int:event_id>/reject', methods=['POST'])
@admin_required
def reject_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.status == 'pending' or event.status == 'approved':
        event.status = 'rejected'
        try:
            db.session.commit()
            flash(f'Event "{event.title}" has been rejected.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error rejecting event: {str(e)}', 'danger')
    else:
        flash('Event is not in a state that can be rejected', 'warning')
    
    return redirect(url_for('admin.events'))

@admin_bp.route('/categories')
@admin_required
def categories():
    # Get all categories
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@admin_required
def create_category():
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Category already exists', 'warning')
            return redirect(url_for('admin.categories'))
        
        # Create new category
        category = Category(name=name)
        
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating category: {str(e)}', 'danger')
    
    return render_template('admin/create_category.html')

@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Check if category name already exists
        existing = Category.query.filter(Category.name == name, Category.category_id != category_id).first()
        if existing:
            flash('Category name already exists', 'warning')
            return render_template('admin/edit_category.html', category=category)
        
        category.name = name
        
        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'danger')
    
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if category is being used by events
    events_count = Event.query.filter_by(category_id=category_id).count()
    if events_count > 0:
        flash(f'Cannot delete category. It is being used by {events_count} events.', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/bookings')
@admin_required
def bookings():
    # Get all bookings
    bookings = Booking.query.order_by(Booking.booking_time.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/reports')
@admin_required
def reports():
    # Get date range for reports
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Last 30 days by default
    
    # Get events created in date range
    events_created = Event.query.filter(
        Event.created_at.between(start_date, end_date)
    ).count()
    
    # Get bookings made in date range
    bookings_made = Booking.query.filter(
        Booking.booking_time.between(start_date, end_date)
    ).count()
    
    # Calculate revenue in date range
    revenue = db.session.query(db.func.sum(Booking.total_amount))\
              .filter(Booking.booking_time.between(start_date, end_date))\
              .filter(Booking.status == 'booked').scalar() or 0
    
    # Get top categories
    top_categories = db.session.query(
        Category.name, db.func.count(Event.event_id).label('event_count')
    ).join(Event, Category.category_id == Event.category_id)\
     .group_by(Category.name)\
     .order_by(db.desc('event_count'))\
     .limit(5).all()
    
    # Get top events by bookings
    top_events = db.session.query(
        Event.title, db.func.count(Booking.booking_id).label('booking_count')
    ).join(Booking, Event.event_id == Booking.event_id)\
     .group_by(Event.title)\
     .order_by(db.desc('booking_count'))\
     .limit(5).all()
    
    return render_template('admin/reports.html',
                          start_date=start_date,
                          end_date=end_date,
                          events_created=events_created,
                          bookings_made=bookings_made,
                          revenue=revenue,
                          top_categories=top_categories,
                          top_events=top_events)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    admin = user.admin
    
    if request.method == 'POST':
        # Update profile information
        admin.name = request.form.get('name')
        
        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('admin/profile.html', user=user, admin=admin)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('admin/profile.html', user=user, admin=admin)
            
            user.set_password(new_password)
            flash('Password updated successfully', 'success')
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('admin/profile.html', user=user, admin=admin)
