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

# Admin API routes for reports
@admin_bp.route('/api/platform-report')
@admin_required
def api_platform_report():
    """API endpoint for platform revenue report data"""
    # Get parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    organizer_id = request.args.get('organizer_id')
    event_id = request.args.get('event_id')
    
    try:
        # Parse dates
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.utcnow()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get platform report data
    report_data = get_platform_report_data(start_date, end_date, organizer_id, event_id)
    
    return jsonify(report_data)

def get_platform_report_data(start_date, end_date, organizer_id=None, event_id=None):
    """Get comprehensive platform revenue data"""
    from models import Organizer
    
    # Base query for bookings in date range
    bookings_query = Booking.query.filter(
        Booking.booking_time.between(start_date, end_date),
        Booking.status == 'booked'
    )
    
    # Filter by organizer if specified
    if organizer_id and organizer_id != 'all':
        try:
            organizer_id = int(organizer_id)
            event_ids = [e.event_id for e in Event.query.filter_by(organizer_id=organizer_id).all()]
            if event_ids:
                bookings_query = bookings_query.filter(Booking.event_id.in_(event_ids))
            else:
                bookings_query = bookings_query.filter(Booking.event_id == -1)  # No results
        except ValueError:
            pass
    
    # Filter by event if specified
    if event_id and event_id != 'all':
        try:
            event_id = int(event_id)
            bookings_query = bookings_query.filter_by(event_id=event_id)
        except ValueError:
            pass
    
    bookings = bookings_query.all()
    
    # Calculate summary metrics
    gross_revenue = sum(float(booking.total_amount) if booking.total_amount else 0.0 for booking in bookings)
    platform_commission = gross_revenue * 0.05
    total_bookings = len(bookings)
    total_tickets = sum(booking.quantity for booking in bookings)
    
    # Get unique organizers with bookings
    organizer_ids = list(set(booking.event.organizer_id for booking in bookings if booking.event))
    active_organizers = len(organizer_ids)
    
    # Commission by month
    commission_by_month = {}
    for booking in bookings:
        month_key = booking.booking_time.strftime('%Y-%m') if booking.booking_time else 'Unknown'
        booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
        commission_by_month[month_key] = commission_by_month.get(month_key, 0) + booking_amount * 0.05
    
    # Organizer breakdown
    organizer_breakdown = []
    for org_id in organizer_ids:
        organizer = Organizer.query.get(org_id)
        if not organizer:
            continue
            
        org_bookings = [b for b in bookings if b.event and b.event.organizer_id == org_id]
        org_events = list(set(b.event_id for b in org_bookings))
        
        org_gross_revenue = sum(float(b.total_amount) if b.total_amount else 0.0 for b in org_bookings)
        org_commission = org_gross_revenue * 0.05
        org_net_revenue = org_gross_revenue * 0.95
        
        organizer_breakdown.append({
            'organizer_id': org_id,
            'name': organizer.name,
            'email': organizer.user.email if organizer.user else 'N/A',
            'organization_name': organizer.organization_name,
            'event_count': len(org_events),
            'booking_count': len(org_bookings),
            'gross_revenue': org_gross_revenue,
            'commission': org_commission,
            'net_revenue': org_net_revenue
        })
    
    # Sort by commission (highest first)
    organizer_breakdown.sort(key=lambda x: x['commission'], reverse=True)
    
    # Event breakdown
    event_breakdown = []
    event_revenue = {}
    
    for booking in bookings:
        if not booking.event:
            continue
            
        event_id = booking.event_id
        if event_id not in event_revenue:
            event_revenue[event_id] = {
                'event': booking.event,
                'bookings': [],
                'gross_revenue': 0
            }
        
        event_revenue[event_id]['bookings'].append(booking)
        booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
        event_revenue[event_id]['gross_revenue'] += booking_amount
    
    for event_id, data in event_revenue.items():
        event = data['event']
        gross_revenue = data['gross_revenue']
        commission = gross_revenue * 0.05
        
        event_breakdown.append({
            'event_id': event_id,
            'title': event.title,
            'organizer_name': event.organizer.name if event.organizer else 'N/A',
            'event_date': event.event_date,
            'booking_count': len(data['bookings']),
            'gross_revenue': gross_revenue,
            'commission': commission
        })
    
    # Sort by commission (highest first)
    event_breakdown.sort(key=lambda x: x['commission'], reverse=True)
    
    return {
        'summary': {
            'platform_commission': round(platform_commission, 2),
            'gross_revenue': round(gross_revenue, 2),
            'total_bookings': total_bookings,
            'total_tickets': total_tickets,
            'active_organizers': active_organizers,
            'avg_commission_per_booking': round(platform_commission / total_bookings, 2) if total_bookings > 0 else 0
        },
        'commission_by_month': dict(sorted(commission_by_month.items())),
        'organizer_breakdown': organizer_breakdown,
        'event_breakdown': event_breakdown,
        'date_range': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    }

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
    # Calculate admin commission (5% of all bookings)
    gross_revenue = db.session.query(db.func.sum(Booking.total_amount))\
                    .filter(Booking.status == 'booked').scalar() or 0
    admin_commission = float(gross_revenue) * 0.05
    
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
                          admin_commission=admin_commission,
                          gross_revenue=gross_revenue,
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
    # Get default date range for reports (last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Get all organizers and events for filter dropdowns
    from models import Organizer
    organizers = Organizer.query.join(User).all()
    events = Event.query.all()
    
    # Get initial report data
    report_data = get_platform_report_data(start_date, end_date)
    
    return render_template('admin/reports.html',
                          organizers=organizers,
                          events=events,
                          report_data=report_data,
                          start_date=start_date.strftime('%Y-%m-%d'),
                          end_date=end_date.strftime('%Y-%m-%d'))

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
