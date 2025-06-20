from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Event, Booking, Feedback, Payment
from functools import wraps
from datetime import datetime
import json

customer_bp = Blueprint('customer', __name__)

# Authentication decorator for customer
def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('main.login'))
        
        if session.get('role') != 'customer':
            flash('Access denied. Customer privileges required.', 'danger')
            return redirect(url_for('main.index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Customer routes
@customer_bp.route('/dashboard')
@customer_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    # Get statistics
    total_bookings = customer.get_total_bookings()
    cancelled_bookings = customer.get_cancelled_bookings()
    total_spent = customer.get_total_spent()
    
    # Get upcoming events
    upcoming_events = customer.get_upcoming_events()
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(customer_id=customer.customer_id)\
                        .order_by(Booking.booking_time.desc()).limit(5).all()
    
    return render_template('customer/dashboard.html', 
                          customer=customer,
                          total_bookings=total_bookings,
                          cancelled_bookings=cancelled_bookings,
                          total_spent=total_spent,
                          upcoming_events=upcoming_events,
                          recent_bookings=recent_bookings)

@customer_bp.route('/events')
@customer_required
def events():
    # Get all approved events
    events = Event.query.filter_by(status='approved')\
                .order_by(Event.event_date).all()
    
    # Get categories for filtering
    from models import Category
    categories = Category.query.all()
    
    # Pass current time to template for date comparisons
    current_time = datetime.utcnow()
    
    return render_template('customer/events.html', 
                          events=events, 
                          categories=categories,
                          current_time=current_time)

@customer_bp.route('/events/<int:event_id>')
@customer_required
def event_details(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event is approved
    if event.status != 'approved':
        flash('This event is not available for viewing.', 'warning')
        return redirect(url_for('customer.events'))
    
    # Get feedback for this event
    feedback = Feedback.query.filter_by(event_id=event_id).all()
    
    # Check if user has booked this event
    existing_booking = Booking.query.filter_by(
        customer_id=customer.customer_id,
        event_id=event_id,
        status='booked'
    ).first()
    
    # Check if user has already submitted feedback for this event
    existing_feedback = Feedback.query.filter_by(
        customer_id=customer.customer_id,
        event_id=event_id
    ).first()
    
    # Pass current time to template for date comparisons
    current_time = datetime.utcnow()
    
    return render_template('customer/event_details.html', 
                          event=event, 
                          feedback=feedback,
                          existing_booking=existing_booking,
                          existing_feedback=existing_feedback,
                          current_time=current_time)

@customer_bp.route('/events/<int:event_id>/book', methods=['GET', 'POST'])
@customer_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if event is approved and has available seats
    if event.status != 'approved':
        flash('This event is not available for booking.', 'warning')
        return redirect(url_for('customer.events'))
    
    # Check if event date has passed
    if event.event_date and event.event_date < datetime.utcnow():
        flash('This event has already ended and is no longer available for booking.', 'warning')
        return redirect(url_for('customer.event_details', event_id=event_id))
    
    if not event.is_available():
        flash('Sorry, this event is fully booked.', 'warning')
        return redirect(url_for('customer.event_details', event_id=event_id))
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    if request.method == 'POST':
        # Get form data
        quantity = int(request.form.get('quantity', 1))
        
        # Validate quantity
        if quantity <= 0:
            flash('Please select a valid quantity', 'danger')
            return redirect(url_for('customer.book_event', event_id=event_id))
        
        if quantity > event.available_seats:
            flash(f'Only {event.available_seats} seats available', 'danger')
            return redirect(url_for('customer.book_event', event_id=event_id))
        
        # Use the event's price
        ticket_price = event.price
        total_amount = quantity * ticket_price
        
        # Create booking
        booking = Booking(
            customer_id=customer.customer_id,
            event_id=event_id,
            quantity=quantity,
            total_amount=total_amount,
            status='booked'
        )
        
        try:
            # Update available seats
            if not event.update_available_seats(quantity, 'book'):
                flash('Not enough seats available', 'danger')
                return redirect(url_for('customer.book_event', event_id=event_id))
            
            db.session.add(booking)
            db.session.commit()
            
            flash('Event booked successfully!', 'success')
            return redirect(url_for('customer.payment', booking_id=booking.booking_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking event: {str(e)}', 'danger')
    
    # GET request - show booking form
    return render_template('customer/book_event.html', event=event)

@customer_bp.route('/bookings')
@customer_required
def bookings():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    # Get all bookings by this customer
    bookings = Booking.query.filter_by(customer_id=customer.customer_id)\
                .order_by(Booking.booking_time.desc()).all()
    
    # Pass current time to template for date comparisons
    current_time = datetime.utcnow()
    
    return render_template('customer/bookings.html', 
                          bookings=bookings, 
                          current_time=current_time)

@customer_bp.route('/bookings/<int:booking_id>')
@customer_required
def booking_details(booking_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking belongs to this customer
    if booking.customer_id != customer.customer_id:
        flash('Access denied. This booking does not belong to you.', 'danger')
        return redirect(url_for('customer.bookings'))
    
    # Get payments for this booking
    payments = Payment.query.filter_by(booking_id=booking_id).all()
    
    return render_template('customer/booking_details.html', 
                          booking=booking, 
                          payments=payments)

@customer_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@customer_required
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking belongs to this customer
    if booking.customer_id != customer.customer_id:
        flash('Access denied. This booking does not belong to you.', 'danger')
        return redirect(url_for('customer.bookings'))
    
    # Check if booking can be cancelled
    if booking.status != 'booked':
        flash('This booking has already been cancelled.', 'warning')
        return redirect(url_for('customer.booking_details', booking_id=booking_id))
    
    # Cancel booking
    if booking.cancel_booking():
        try:
            db.session.commit()
            flash('Booking cancelled successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error cancelling booking: {str(e)}', 'danger')
    else:
        flash('Unable to cancel booking.', 'danger')
    
    return redirect(url_for('customer.booking_details', booking_id=booking_id))

@customer_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@customer_required
def payment(booking_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if booking belongs to this customer
    if booking.customer_id != customer.customer_id:
        flash('Access denied. This booking does not belong to you.', 'danger')
        return redirect(url_for('customer.bookings'))
    
    if request.method == 'POST':
        # Get form data
        payment_mode = request.form.get('payment_mode')
        amount = float(request.form.get('amount', 0))
        
        # Validate amount
        if amount <= 0:
            flash('Please enter a valid amount', 'danger')
            return redirect(url_for('customer.payment', booking_id=booking_id))
        
        # Create payment record
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_mode=payment_mode,
            payment_status='success',  # In a real app, this would be determined by payment gateway
            transaction_id=f'TXN-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
        )
        
        try:
            db.session.add(payment)
            db.session.commit()
            flash('Payment successful! Your tickets are confirmed.', 'success')
            # Redirect to dashboard instead of booking details
            return redirect(url_for('customer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing payment: {str(e)}', 'danger')
    
    # GET request - show payment form
    return render_template('customer/payment.html', booking=booking)

@customer_bp.route('/feedback/<int:event_id>', methods=['GET', 'POST'])
@customer_required
def submit_feedback(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event is approved
    if event.status != 'approved':
        flash('You can only provide feedback for approved events.', 'warning')
        return redirect(url_for('customer.events'))
    
    # CRITICAL: Check if user has booked this event
    booking = Booking.query.filter_by(
        customer_id=customer.customer_id,
        event_id=event_id,
        status='booked'
    ).first()
    
    if not booking:
        flash('You can only provide feedback for events you have booked.', 'warning')
        return redirect(url_for('customer.event_details', event_id=event_id))
    
    # Check if user has already submitted feedback
    existing_feedback = Feedback.query.filter_by(
        customer_id=customer.customer_id,
        event_id=event_id
    ).first()
    
    if existing_feedback:
        flash('You have already submitted feedback for this event.', 'info')
        return redirect(url_for('customer.event_details', event_id=event_id))
    
    if request.method == 'POST':
        # Get form data
        rating_str = request.form.get('rating', '').strip()
        comments = request.form.get('comments', '').strip()
        
        # Validate rating
        if not rating_str:
            flash('Please select a star rating.', 'danger')
            return render_template('customer/submit_feedback.html', event=event)
        
        try:
            rating = int(rating_str)
        except (ValueError, TypeError):
            flash('Invalid rating value.', 'danger')
            return render_template('customer/submit_feedback.html', event=event)
        
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5 stars.', 'danger')
            return render_template('customer/submit_feedback.html', event=event)
        
        # Sanitize comments (basic HTML escaping is handled by Jinja2)
        # Additional sanitization can be added here if needed
        if comments and len(comments) > 1000:
            flash('Comments must be less than 1000 characters.', 'danger')
            return render_template('customer/submit_feedback.html', event=event)
        
        # Determine sentiment based on rating
        if rating >= 4:
            sentiment = 'positive'
        elif rating == 3:
            sentiment = 'neutral'
        else:
            sentiment = 'negative'
        
        # Create feedback record
        feedback = Feedback(
            customer_id=customer.customer_id,
            event_id=event_id,
            rating=rating,
            comments=comments if comments else None,
            sentiment=sentiment
        )
        
        try:
            db.session.add(feedback)
            db.session.commit()
            flash('Thank you for your feedback! Your rating has been submitted successfully.', 'success')
            return redirect(url_for('customer.event_details', event_id=event_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting feedback: {str(e)}. Please try again.', 'danger')
            return render_template('customer/submit_feedback.html', event=event)
    
    # GET request - show feedback form
    return render_template('customer/submit_feedback.html', event=event)

@customer_bp.route('/profile', methods=['GET', 'POST'])
@customer_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    customer = user.customer
    
    if request.method == 'POST':
        # Update profile information
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        customer.preferences = request.form.get('preferences')
        
        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('customer/profile.html', user=user, customer=customer)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('customer/profile.html', user=user, customer=customer)
            
            user.set_password(new_password)
            flash('Password updated successfully', 'success')
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('customer/profile.html', user=user, customer=customer)