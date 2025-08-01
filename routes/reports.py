from flask import Blueprint, render_template, request, jsonify, session
from models import db, User, Event, Booking, Category, Feedback, Payment
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

reports_bp = Blueprint('reports', __name__)

# Authentication decorator for organizer
def organizer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        if session.get('role') != 'organizer':
            return jsonify({'error': 'Organizer privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/organizer/reports')
@organizer_required
def organizer_reports():
    """Main reports dashboard for organizers"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get all events by this organizer
    events = Event.query.filter_by(organizer_id=organizer.organizer_id).all()
    
    # Get default date range (last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Get initial revenue data
    revenue_data = get_revenue_data(organizer.organizer_id, start_date, end_date)
    
    return render_template('organizer/reports.html', 
                          events=events,
                          revenue_data=revenue_data,
                          start_date=start_date.strftime('%Y-%m-%d'),
                          end_date=end_date.strftime('%Y-%m-%d'))

@reports_bp.route('/organizer/api/revenue-report')
@organizer_required
def api_revenue_report():
    """API endpoint for revenue report data"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
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
    
    # Get revenue data
    revenue_data = get_revenue_data(organizer.organizer_id, start_date, end_date, event_id)
    
    return jsonify(revenue_data)

@reports_bp.route('/organizer/api/event-performance')
@organizer_required
def api_event_performance():
    """API endpoint for individual event performance data"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    event_id = request.args.get('event_id')
    if not event_id:
        return jsonify({'error': 'Event ID is required'}), 400
    
    try:
        event_id = int(event_id)
    except ValueError:
        return jsonify({'error': 'Invalid event ID'}), 400
    
    # Verify event belongs to organizer
    event = Event.query.filter_by(
        event_id=event_id, 
        organizer_id=organizer.organizer_id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found or access denied'}), 404
    
    # Get event performance data
    performance_data = get_event_performance_data(event)
    
    return jsonify(performance_data)

@reports_bp.route('/organizer/api/revenue-trends')
@organizer_required
def api_revenue_trends():
    """API endpoint for revenue trends over time"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    organizer = user.organizer
    
    # Get parameters
    period = request.args.get('period', 'monthly')  # daily, weekly, monthly
    months = int(request.args.get('months', 12))  # number of months to look back
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    # Get trends data
    trends_data = get_revenue_trends(organizer.organizer_id, start_date, end_date, period)
    
    return jsonify(trends_data)

def get_revenue_data(organizer_id, start_date, end_date, event_id=None):
    """Get comprehensive revenue data for the organizer"""
    
    # Base query for events by this organizer
    events_query = Event.query.filter_by(organizer_id=organizer_id)
    
    # Filter by specific event if provided
    if event_id and event_id != 'all':
        try:
            event_id = int(event_id)
            events_query = events_query.filter_by(event_id=event_id)
        except ValueError:
            pass
    
    events = events_query.all()
    event_ids = [event.event_id for event in events]
    
    if not event_ids:
        return get_empty_revenue_data()
    
    # Get bookings in date range
    bookings_query = Booking.query.filter(
        Booking.event_id.in_(event_ids),
        Booking.booking_time.between(start_date, end_date),
        Booking.status == 'booked'
    )
    
    bookings = bookings_query.all()
    
    # Calculate metrics
    # Organizer receives 95% of booking amount (5% goes to admin)
    total_revenue = sum((float(booking.total_amount) if booking.total_amount else 0.0) * 0.95 for booking in bookings)
    total_bookings = len(bookings)
    total_tickets = sum(booking.quantity for booking in bookings)
    
    # Revenue by event
    revenue_by_event = {}
    bookings_by_event = {}
    tickets_by_event = {}
    
    for booking in bookings:
        event_title = booking.event.title if booking.event else 'Unknown Event'
        # Organizer receives 95% of booking amount
        booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
        revenue_by_event[event_title] = revenue_by_event.get(event_title, 0) + booking_amount * 0.95
        bookings_by_event[event_title] = bookings_by_event.get(event_title, 0) + 1
        tickets_by_event[event_title] = tickets_by_event.get(event_title, 0) + booking.quantity
    
    # Top performing events
    top_events = sorted(revenue_by_event.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Revenue by month
    revenue_by_month = {}
    for booking in bookings:
        month_key = booking.booking_time.strftime('%Y-%m') if booking.booking_time else 'Unknown'
        # Organizer receives 95% of booking amount
        booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
        revenue_by_month[month_key] = revenue_by_month.get(month_key, 0) + booking_amount * 0.95
    
    # Average metrics
    avg_revenue_per_booking = total_revenue / total_bookings if total_bookings > 0 else 0
    avg_revenue_per_event = total_revenue / len(events) if events else 0
    
    # Event status breakdown
    approved_events = len([e for e in events if e.status == 'approved'])
    pending_events = len([e for e in events if e.status == 'pending'])
    
    # Get payment methods breakdown
    payment_methods = {}
    for booking in bookings:
        for payment in booking.payments:
            if payment.payment_status == 'success':
                method = payment.payment_mode or 'Unknown'
                # Organizer receives 95% of payment amount
                payment_amount = float(payment.amount) if payment.amount else 0.0
                payment_methods[method] = payment_methods.get(method, 0) + payment_amount * 0.95
    
    return {
        'summary': {
            'total_revenue': round(total_revenue, 2),
            'total_bookings': total_bookings,
            'total_tickets': total_tickets,
            'total_events': len(events),
            'approved_events': approved_events,
            'pending_events': pending_events,
            'avg_revenue_per_booking': round(avg_revenue_per_booking, 2),
            'avg_revenue_per_event': round(avg_revenue_per_event, 2)
        },
        'revenue_by_event': dict(sorted(revenue_by_event.items(), key=lambda x: x[1], reverse=True)),
        'bookings_by_event': bookings_by_event,
        'tickets_by_event': tickets_by_event,
        'top_events': top_events,
        'revenue_by_month': dict(sorted(revenue_by_month.items())),
        'payment_methods': payment_methods,
        'date_range': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    }

def get_event_performance_data(event):
    """Get detailed performance data for a specific event"""
    
    # Basic event info
    event_data = {
        'event_id': event.event_id,
        'title': event.title,
        'event_date': event.event_date.isoformat() if event.event_date else None,
        'location': event.location,
        'total_seats': event.total_seats,
        'available_seats': event.available_seats,
        'price': float(event.price) if event.price else 0
    }
    
    # Booking metrics
    bookings = Booking.query.filter_by(event_id=event.event_id, status='booked').all()
    # Organizer receives 95% of booking amount (5% goes to admin)
    total_revenue = sum((float(booking.total_amount) if booking.total_amount else 0.0) * 0.95 for booking in bookings)
    total_tickets_sold = sum(booking.quantity for booking in bookings)
    
    # Booking timeline (bookings per day)
    booking_timeline = {}
    for booking in bookings:
        date_key = booking.booking_time.strftime('%Y-%m-%d') if booking.booking_time else 'Unknown'
        booking_timeline[date_key] = booking_timeline.get(date_key, 0) + booking.quantity
    
    # Customer demographics (simplified)
    unique_customers = len(set(booking.customer_id for booking in bookings))
    
    # Feedback metrics
    feedback = Feedback.query.filter_by(event_id=event.event_id).all()
    avg_rating = sum(f.rating for f in feedback) / len(feedback) if feedback else 0
    
    sentiment_breakdown = {
        'positive': len([f for f in feedback if f.sentiment == 'positive']),
        'neutral': len([f for f in feedback if f.sentiment == 'neutral']),
        'negative': len([f for f in feedback if f.sentiment == 'negative'])
    }
    
    return {
        'event_info': event_data,
        'revenue_metrics': {
            'total_revenue': round(total_revenue, 2),
            'total_bookings': len(bookings),
            'total_tickets_sold': total_tickets_sold,
            'unique_customers': unique_customers,
            'avg_revenue_per_ticket': round(total_revenue / total_tickets_sold, 2) if total_tickets_sold > 0 else 0,
            'occupancy_rate': round((total_tickets_sold / event.total_seats) * 100, 1) if event.total_seats > 0 else 0
        },
        'booking_timeline': dict(sorted(booking_timeline.items())),
        'feedback_metrics': {
            'total_feedback': len(feedback),
            'average_rating': round(avg_rating, 1),
            'sentiment_breakdown': sentiment_breakdown
        }
    }

def get_revenue_trends(organizer_id, start_date, end_date, period='monthly'):
    """Get revenue trends over time"""
    
    # Get all events by organizer
    event_ids = [e.event_id for e in Event.query.filter_by(organizer_id=organizer_id).all()]
    
    if not event_ids:
        return {'trends': [], 'period': period}
    
    # Get bookings in date range
    bookings = Booking.query.filter(
        Booking.event_id.in_(event_ids),
        Booking.booking_time.between(start_date, end_date),
        Booking.status == 'booked'
    ).all()
    
    # Group by period
    trends = {}
    
    for booking in bookings:
        if not booking.booking_time:
            continue
            
        if period == 'daily':
            key = booking.booking_time.strftime('%Y-%m-%d')
        elif period == 'weekly':
            # Get start of week (Monday)
            week_start = booking.booking_time - timedelta(days=booking.booking_time.weekday())
            key = week_start.strftime('%Y-%m-%d')
        else:  # monthly
            key = booking.booking_time.strftime('%Y-%m')
        
        # Organizer receives 95% of booking amount
        booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
        trends[key] = trends.get(key, 0) + booking_amount * 0.95
    
    # Convert to list of dictionaries for easier frontend consumption
    trends_list = [
        {'period': period_key, 'revenue': round(revenue, 2)}
        for period_key, revenue in sorted(trends.items())
    ]
    
    return {
        'trends': trends_list,
        'period': period,
        'total_periods': len(trends_list),
        'total_revenue': round(sum(trends.values()), 2)
    }

def get_empty_revenue_data():
    """Return empty revenue data structure"""
    return {
        'summary': {
            'total_revenue': 0,
            'total_bookings': 0,
            'total_tickets': 0,
            'total_events': 0,
            'approved_events': 0,
            'pending_events': 0,
            'avg_revenue_per_booking': 0,
            'avg_revenue_per_event': 0
        },
        'revenue_by_event': {},
        'bookings_by_event': {},
        'tickets_by_event': {},
        'top_events': [],
        'revenue_by_month': {},
        'payment_methods': {},
        'date_range': {
            'start_date': '',
            'end_date': ''
        }
    }