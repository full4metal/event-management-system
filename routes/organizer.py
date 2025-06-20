import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from models import db, User, Event, Booking, Category, Feedback
from utils.sentiment_analyzer import SentimentAnalyzer
from functools import wraps
from datetime import datetime
import json

organizer_bp = Blueprint('organizer', __name__)

# Authentication decorator for organizer
def organizer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('main.login'))
        
        if session.get('role') != 'organizer':
            flash('Access denied. Organizer privileges required.', 'danger')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Organizer routes
@organizer_bp.route('/dashboard')
@organizer_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get statistics
    total_events = organizer.get_total_events()
    approved_events = len(organizer.get_approved_events())
    pending_events = len(organizer.get_pending_events())
    total_bookings = organizer.get_total_bookings()
    total_revenue = organizer.get_total_revenue()
    
    # Get recent events
    recent_events = Event.query.filter_by(organizer_id=organizer.organizer_id)\
                        .order_by(Event.created_at.desc()).limit(5).all()
    
    return render_template('organizer/dashboard.html', 
                          organizer=organizer,
                          total_events=total_events,
                          approved_events=approved_events,
                          pending_events=pending_events,
                          total_bookings=total_bookings,
                          total_revenue=total_revenue,
                          recent_events=recent_events)

@organizer_bp.route('/events')
@organizer_required
def events():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id)\
                .order_by(Event.event_date.desc()).all()
    
    return render_template('organizer/events.html', events=events)

@organizer_bp.route('/events/create', methods=['GET', 'POST'])
@organizer_required
def create_event():
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        organizer = user.organizer
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        category_id = request.form.get('category_id')
        event_date_str = request.form.get('event_date')
        total_seats = request.form.get('total_seats')
        price = request.form.get('price', '0.00')
        image_url = request.form.get('image_url', '').strip()
        
        # Handle file upload
        image_file = request.files.get('image_file')
        final_image_url = image_url
        
        if image_file and image_file.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in image_file.filename and \
               image_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join('static', 'uploads', 'events')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate secure filename
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                # Save file
                file_path = os.path.join(upload_dir, filename)
                image_file.save(file_path)
                
                # Set the URL for database storage
                final_image_url = f'/static/uploads/events/{filename}'
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'danger')
                categories = Category.query.all()
                return render_template('organizer/create_event.html', categories=categories)
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Event title is required')
        elif len(title) > 200:
            errors.append('Event title must be less than 200 characters')
            
        if not location:
            errors.append('Event location is required')
        elif len(location) > 255:
            errors.append('Location must be less than 255 characters')
            
        if not category_id:
            errors.append('Event category is required')
        else:
            # Verify category exists
            category = Category.query.get(category_id)
            if not category:
                errors.append('Invalid category selected')
        
        if not total_seats:
            errors.append('Total seats is required')
        else:
            try:
                total_seats = int(total_seats)
                if total_seats < 1:
                    errors.append('Total seats must be at least 1')
                elif total_seats > 10000:
                    errors.append('Total seats cannot exceed 10,000')
            except ValueError:
                errors.append('Total seats must be a valid number')
        
        # Validate price
        if not price:
            errors.append('Ticket price is required')
        else:
            try:
                price = float(price)
                if price < 0:
                    errors.append('Price cannot be negative')
                elif price > 10000:
                    errors.append('Price cannot exceed $10,000')
            except ValueError:
                errors.append('Price must be a valid number')

        
        if not event_date_str:
            errors.append('Event date and time is required')
        else:
            try:
                event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
                if event_date <= datetime.now():
                    errors.append('Event date must be in the future')
            except ValueError:
                errors.append('Invalid date format')
        
        # Validate image URL if provided (and no file uploaded)
        if image_url and not image_file:
            if not (image_url.startswith('http://') or image_url.startswith('https://')):
                errors.append('Image URL must start with http:// or https://')
        
        # If there are validation errors, show them and return to form
        if errors:
            for error in errors:
                flash(error, 'danger')
            categories = Category.query.all()
            return render_template('organizer/create_event.html', categories=categories)
        
        # Create new event
        try:
            event = Event(
                organizer_id=organizer.organizer_id,
                title=title,
                description=description if description else None,
                location=location,
                category_id=int(category_id),
                event_date=event_date,
                total_seats=total_seats,
                available_seats=total_seats,
                price=price,
                image_url=final_image_url if final_image_url else None,
                status='pending'
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash('Event created successfully! It has been submitted for admin approval.', 'success')
            return redirect(url_for('organizer.events'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'danger')
            categories = Category.query.all()
            return render_template('organizer/create_event.html', categories=categories)
    
    # GET request - show form
    categories = Category.query.all()
    return render_template('organizer/create_event.html', categories=categories)

@organizer_bp.route('/events/<int:event_id>')
@organizer_required
def event_details(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to this organizer
    if event.organizer_id != organizer.organizer_id:
        flash('Access denied. This event does not belong to you.', 'danger')
        return redirect(url_for('organizer.events'))
    
    # Get bookings for this event
    bookings = Booking.query.filter_by(event_id=event_id).all()
    
    # Get feedback for this event
    feedback = Feedback.query.filter_by(event_id=event_id).all()
    
    return render_template('organizer/event_details.html', 
                          event=event, 
                          bookings=bookings,
                          feedback=feedback)

@organizer_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@organizer_required
def edit_event(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to this organizer
    if event.organizer_id != organizer.organizer_id:
        flash('Access denied. This event does not belong to you.', 'danger')
        return redirect(url_for('organizer.events'))
    
    if request.method == 'POST':
        # Get form data
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.location = request.form.get('location')
        event.category_id = request.form.get('category_id')
        event_date_str = request.form.get('event_date')
        
        # Handle price update
        price = request.form.get('price')
        try:
            event.price = float(price)
        except (ValueError, TypeError):
            flash('Invalid price format', 'danger')
            categories = Category.query.all()
            return render_template('organizer/edit_event.html', event=event, categories=categories)
        
        # Handle image update
        image_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')
        
        if image_file and image_file.filename:
            # Handle file upload (same logic as create)
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in image_file.filename and \
               image_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                
                upload_dir = os.path.join('static', 'uploads', 'events')
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                file_path = os.path.join(upload_dir, filename)
                image_file.save(file_path)
                
                event.image_url = f'/static/uploads/events/{filename}'
        elif image_url:
            event.image_url = image_url
        
        # Parse event date
        try:
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format', 'danger')
            categories = Category.query.all()
            return render_template('organizer/edit_event.html', event=event, categories=categories)
        
        try:
            # If event was approved and changes were made, set back to pending
            if event.status == 'approved':
                event.status = 'pending'
                flash('Your event has been updated and is pending admin approval again.', 'info')
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('organizer.event_details', event_id=event.event_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'danger')
    
    # GET request - show form
    categories = Category.query.all()
    return render_template('organizer/edit_event.html', event=event, categories=categories)

@organizer_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@organizer_required
def delete_event(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to this organizer
    if event.organizer_id != organizer.organizer_id:
        flash('Access denied. This event does not belong to you.', 'danger')
        return redirect(url_for('organizer.events'))
    
    try:
        # Delete the event image if it's a local file
        if event.image_url and event.image_url.startswith('/static/uploads/'):
            image_path = os.path.join(os.getcwd(), event.image_url.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the event (cascade will handle related bookings and feedback)
        db.session.delete(event)
        db.session.commit()
        
        flash('Event deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting event: {str(e)}', 'danger')
    
    return redirect(url_for('organizer.events'))

@organizer_bp.route('/bookings')
@organizer_required
def bookings():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id).all()
    event_ids = [event.event_id for event in events]
    
    # Get all bookings for these events with proper joins
    bookings = Booking.query.filter(Booking.event_id.in_(event_ids))\
                           .join(Event, Booking.event_id == Event.event_id)\
                           .join(User, Booking.customer_id == User.user_id)\
                           .order_by(Booking.booking_time.desc()).all()
    
    return render_template('organizer/bookings.html', bookings=bookings)

@organizer_bp.route('/feedbacks')
@organizer_required
def feedbacks():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id).all()
    event_ids = [event.event_id for event in events]
    
    # Get all feedback for these events
    feedbacks = Feedback.query.filter(Feedback.event_id.in_(event_ids))\
                             .join(Event, Feedback.event_id == Event.event_id)\
                             .order_by(Feedback.submitted_at.desc()).all()
    
    return render_template('organizer/feedbacks.html', feedbacks=feedbacks)

@organizer_bp.route('/events/<int:event_id>/feedbacks')
@organizer_required
def event_feedbacks(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to this organizer
    if event.organizer_id != organizer.organizer_id:
        flash('Access denied. This event does not belong to you.', 'danger')
        return redirect(url_for('organizer.events'))
    
    # Get feedback for this specific event
    feedbacks = Feedback.query.filter_by(event_id=event_id)\
                             .order_by(Feedback.submitted_at.desc()).all()
    
    return render_template('organizer/event_feedbacks.html', 
                          event=event, 
                          feedbacks=feedbacks)

@organizer_bp.route('/sentiment-analysis')
@organizer_required
def sentiment_analysis():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id).all()
    event_ids = [event.event_id for event in events]
    
    # Get all feedback for these events
    feedbacks = Feedback.query.filter(Feedback.event_id.in_(event_ids))\
                             .join(Event, Feedback.event_id == Event.event_id)\
                             .order_by(Feedback.submitted_at.desc()).all()
    
    # Prepare feedback data for analysis
    feedback_data = []
    for feedback in feedbacks:
        feedback_data.append({
            'feedback_id': feedback.feedback_id,
            'event_id': feedback.event_id,
            'comments': feedback.comments,
            'rating': feedback.rating,
            'submitted_at': feedback.submitted_at,
            'event_title': feedback.event.title if feedback.event else 'Unknown Event'
        })
    
    # Perform sentiment analysis
    analyzer = SentimentAnalyzer()
    analysis_results = analyzer.analyze_bulk_feedback(feedback_data)
    
    # Generate word cloud data
    word_cloud_data = analyzer.generate_word_cloud_data(feedback_data)
    
    return render_template('organizer/sentiment_analysis.html',
                          feedbacks=feedbacks,
                          analysis_results=analysis_results,
                          word_cloud_data=word_cloud_data,
                          events=events)

@organizer_bp.route('/api/sentiment-analysis/<int:event_id>')
@organizer_required
def api_event_sentiment_analysis(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to this organizer
    if event.organizer_id != organizer.organizer_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get feedback for this specific event
    feedbacks = Feedback.query.filter_by(event_id=event_id).all()
    
    # Prepare feedback data for analysis
    feedback_data = []
    for feedback in feedbacks:
        feedback_data.append({
            'feedback_id': feedback.feedback_id,
            'event_id': feedback.event_id,
            'comments': feedback.comments,
            'rating': feedback.rating,
            'submitted_at': feedback.submitted_at,
            'event_title': event.title
        })
    
    # Perform sentiment analysis
    analyzer = SentimentAnalyzer()
    analysis_results = analyzer.analyze_bulk_feedback(feedback_data)
    
    # Generate word cloud data
    word_cloud_data = analyzer.generate_word_cloud_data(feedback_data)
    
    return jsonify({
        'analysis_results': analysis_results,
        'word_cloud_data': word_cloud_data
    })

@organizer_bp.route('/api/sentiment-analysis')
@organizer_required
def api_sentiment_analysis():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get filter parameters
    event_id = request.args.get('event_id')
    time_filter = request.args.get('time_filter', 'all')
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id).all()
    event_ids = [event.event_id for event in events]
    
    # Filter by specific event if requested
    if event_id and event_id != 'all':
        try:
            event_id = int(event_id)
            if event_id in event_ids:
                event_ids = [event_id]
            else:
                return jsonify({'error': 'Event not found or access denied'}), 403
        except ValueError:
            return jsonify({'error': 'Invalid event ID'}), 400
    
    # Build feedback query
    feedback_query = Feedback.query.filter(Feedback.event_id.in_(event_ids))\
                                  .join(Event, Feedback.event_id == Event.event_id)
    
    # Apply time filter
    if time_filter != 'all':
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        if time_filter == 'last-week':
            start_date = now - timedelta(weeks=1)
            feedback_query = feedback_query.filter(Feedback.submitted_at >= start_date)
        elif time_filter == 'last-month':
            start_date = now - timedelta(days=30)
            feedback_query = feedback_query.filter(Feedback.submitted_at >= start_date)
        elif time_filter == 'last-quarter':
            start_date = now - timedelta(days=90)
            feedback_query = feedback_query.filter(Feedback.submitted_at >= start_date)
    
    # Get filtered feedback
    feedbacks = feedback_query.order_by(Feedback.submitted_at.desc()).all()
    
    # Prepare feedback data for analysis
    feedback_data = []
    for feedback in feedbacks:
        feedback_data.append({
            'feedback_id': feedback.feedback_id,
            'event_id': feedback.event_id,
            'comments': feedback.comments,
            'rating': feedback.rating,
            'submitted_at': feedback.submitted_at,
            'event_title': feedback.event.title if feedback.event else 'Unknown Event'
        })
    
    # Perform sentiment analysis
    analyzer = SentimentAnalyzer()
    analysis_results = analyzer.analyze_bulk_feedback(feedback_data)
    
    # Generate word cloud data
    word_cloud_data = analyzer.generate_word_cloud_data(feedback_data)
    
    return jsonify({
        'analysis_results': analysis_results,
        'word_cloud_data': word_cloud_data,
        'total_feedback': len(feedback_data)
    })

@organizer_bp.route('/profile', methods=['GET', 'POST'])
@organizer_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    if request.method == 'POST':
        # Update profile information
        organizer.name = request.form.get('name')
        organizer.organization_name = request.form.get('organization_name')
        organizer.phone = request.form.get('phone')
        organizer.bio = request.form.get('bio')
        
        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('organizer/profile.html', user=user, organizer=organizer)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('organizer/profile.html', user=user, organizer=organizer)
            
            user.set_password(new_password)
            flash('Password updated successfully', 'success')
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('organizer/profile.html', user=user, organizer=organizer)