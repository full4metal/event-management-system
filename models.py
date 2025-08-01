from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'organizer', 'customer', name='user_roles'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organizer = db.relationship('Organizer', backref='user', uselist=False, cascade='all, delete-orphan')
    customer = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    admin = db.relationship('Admin', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_organizer(self):
        return self.role == 'organizer'
    
    def is_customer(self):
        return self.role == 'customer'
    
    def get_profile(self):
        """Get the profile based on user role"""
        if self.role == 'admin':
            return self.admin
        elif self.role == 'organizer':
            return self.organizer
        elif self.role == 'customer':
            return self.customer
        return None
    
    def to_dict(self):
        profile = self.get_profile()
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'profile': profile.to_dict() if profile else None
        }

class Organizer(db.Model):
    __tablename__ = 'organizers'
    
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='organizer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Organizer {self.name}>'
    
    def get_total_events(self):
        """Get total number of events created by this organizer"""
        return len(self.events)
    
    def get_approved_events(self):
        """Get approved events by this organizer"""
        return [event for event in self.events if event.status == 'approved']
    
    def get_pending_events(self):
        """Get pending events by this organizer"""
        return [event for event in self.events if event.status == 'pending']
    
    def get_total_bookings(self):
        """Get total bookings across all organizer's events"""
        total = 0
        for event in self.events:
            total += len(event.bookings)
        return total
    
    def get_total_revenue(self):
        """Calculate total revenue from all events"""
        total_revenue = 0
        for event in self.events:
            for booking in event.bookings:
                if booking.status == 'booked':
                    # Organizer receives 95% of booking amount (5% goes to admin)
                    booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
                    total_revenue += booking_amount * 0.95
        return total_revenue
    
    def to_dict(self):
        return {
            'organizer_id': self.organizer_id,
            'name': self.name,
            'organization_name': self.organization_name,
            'phone': self.phone,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_events': self.get_total_events(),
            'total_bookings': self.get_total_bookings(),
            'total_revenue': self.get_total_revenue()
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    preferences = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def get_total_bookings(self):
        """Get total number of bookings by this customer"""
        return len([booking for booking in self.bookings if booking.status == 'booked'])
    
    def get_cancelled_bookings(self):
        """Get cancelled bookings by this customer"""
        return len([booking for booking in self.bookings if booking.status == 'cancelled'])
    
    def get_total_spent(self):
        """Calculate total amount spent by customer"""
        total = 0
        for booking in self.bookings:
            if booking.status == 'booked':
                total += float(booking.total_amount or 0)
        return total
    
    def get_upcoming_events(self):
        """Get upcoming events for this customer"""
        upcoming = []
        for booking in self.bookings:
            if booking.status == 'booked' and booking.event.event_date > datetime.utcnow():
                upcoming.append(booking.event)
        return upcoming
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_bookings': self.get_total_bookings(),
            'cancelled_bookings': self.get_cancelled_bookings(),
            'total_spent': self.get_total_spent()
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.name}>'
    
    def get_platform_commission(self):
        """Calculate total platform commission (5% of all bookings)"""
        total_commission = 0
        # Get all booked bookings across the platform
        all_bookings = Booking.query.filter_by(status='booked').all()
        for booking in all_bookings:
            booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
            total_commission += booking_amount * 0.05
        return total_commission
    
    @staticmethod
    def get_total_platform_revenue():
        """Calculate total gross revenue across the platform"""
        total_revenue = 0
        all_bookings = Booking.query.filter_by(status='booked').all()
        for booking in all_bookings:
            booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
            total_revenue += booking_amount
        return total_revenue
    
    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'platform_commission': self.get_platform_commission(),
            'total_platform_revenue': self.get_total_platform_revenue()
        }

class Event(db.Model):
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizers.organizer_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    event_date = db.Column(db.DateTime)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False, default=0.00)
    image_url = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='event_status'), default='pending')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='event', lazy=True, cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_events_category_id', 'category_id'),
        db.Index('idx_events_date', 'event_date'),
        db.Index('idx_events_organizer_id', 'organizer_id'),
    )
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    def is_available(self):
        """Check if event has available seats"""
        return self.available_seats > 0
    
    def is_upcoming(self):
        """Check if event is in the future"""
        return self.event_date > datetime.utcnow() if self.event_date else False
    
    def is_past(self):
        """Check if event is in the past"""
        return self.event_date < datetime.utcnow() if self.event_date else False
    
    def get_booked_seats(self):
        """Calculate total booked seats"""
        return self.total_seats - self.available_seats
    
    def get_booking_percentage(self):
        """Calculate booking percentage"""
        if self.total_seats == 0:
            return 0
        return (self.get_booked_seats() / self.total_seats) * 100
    
    def get_total_revenue(self):
        """Calculate total revenue from this event"""
        total = 0
        for booking in self.bookings:
            if booking.status == 'booked':
                # Organizer receives 95% of booking amount (5% goes to admin)
                booking_amount = float(booking.total_amount) if booking.total_amount else 0.0
                total += booking_amount * 0.95
        return total
    
    def get_average_rating(self):
        """Calculate average rating from feedback"""
        if not self.feedback:
            return 0
        total_rating = sum(f.rating for f in self.feedback)
        return total_rating / len(self.feedback)
    
    def get_total_feedback_count(self):
        """Get total number of feedback entries"""
        return len(self.feedback)
    
    def update_available_seats(self, quantity, operation='book'):
        """Update available seats when booking/cancelling"""
        if operation == 'book':
            if self.available_seats >= quantity:
                self.available_seats -= quantity
                return True
            return False
        elif operation == 'cancel':
            self.available_seats += quantity
            if self.available_seats > self.total_seats:
                self.available_seats = self.total_seats
            return True
        return False
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'organizer_id': self.organizer_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'total_seats': self.total_seats,
            'available_seats': self.available_seats,
            'booked_seats': self.get_booked_seats(),
            'booking_percentage': self.get_booking_percentage(),
            'price': float(self.price) if self.price else 0.00,
            'image_url': self.image_url,
            'status': self.status,
            'is_available': self.is_available(),
            'is_upcoming': self.is_upcoming(),
            'is_past': self.is_past(),
            'total_revenue': self.get_total_revenue(),
            'average_rating': self.get_average_rating(),
            'feedback_count': self.get_total_feedback_count(),
            'organizer_name': self.organizer.name if self.organizer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.DECIMAL(10, 2))
    booking_time = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    status = db.Column(db.Enum('booked', 'cancelled', name='booking_status'), default='booked')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True, cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_bookings_customer_id', 'customer_id'),
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    def __repr__(self):
        return f'<Booking {self.booking_id}>'
    
    def cancel_booking(self):
        """Cancel the booking and update event seats"""
        if self.status == 'booked':
            self.status = 'cancelled'
            self.event.update_available_seats(self.quantity, 'cancel')
            return True
        return False
    
    def get_payment_status(self):
        """Get the latest payment status"""
        if self.payments:
            latest_payment = max(self.payments, key=lambda p: p.payment_date)
            return latest_payment.payment_status
        return 'pending'
    
    def get_total_paid(self):
        """Calculate total amount paid"""
        total = 0
        for payment in self.payments:
            if payment.payment_status == 'success':
                total += float(payment.amount)
        return total
    
    def is_fully_paid(self):
        """Check if booking is fully paid"""
        return self.get_total_paid() >= float(self.total_amount or 0)
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'event_date': self.event.event_date.isoformat() if self.event and self.event.event_date else None,
            'quantity': self.quantity,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'booking_time': self.booking_time.isoformat() if self.booking_time else None,
            'status': self.status,
            'payment_status': self.get_payment_status(),
            'total_paid': self.get_total_paid(),
            'is_fully_paid': self.is_fully_paid(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    submitted_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_feedback_event_id', 'event_id'),
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range'),
    )
    
    def __repr__(self):
        return f'<Feedback {self.feedback_id}>'
    
    def get_sentiment_emoji(self):
        """Get emoji based on sentiment"""
        sentiment_map = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }
        return sentiment_map.get(self.sentiment, '😐')
    
    def get_rating_stars(self):
        """Get star representation of rating"""
        return '⭐' * self.rating + '☆' * (5 - self.rating)
    
    def to_dict(self):
        return {
            'feedback_id': self.feedback_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else None,
            'rating': self.rating,
            'rating_stars': self.get_rating_stars(),
            'comments': self.comments,
            'sentiment': self.sentiment,
            'sentiment_emoji': self.get_sentiment_emoji(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    payment_mode = db.Column(db.String(50))
    payment_status = db.Column(db.Enum('success', 'failed', 'pending', name='payment_status'), default='pending')
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('amount >= 0', name='check_amount_non_negative'),
    )
    
    def __repr__(self):
        return f'<Payment {self.payment_id}>'
    
    def is_successful(self):
        """Check if payment was successful"""
        return self.payment_status == 'success'
    
    def is_pending(self):
        """Check if payment is pending"""
        return self.payment_status == 'pending'
    
    def is_failed(self):
        """Check if payment failed"""
        return self.payment_status == 'failed'
    
    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'booking_id': self.booking_id,
            'amount': float(self.amount) if self.amount else 0,
            'payment_mode': self.payment_mode,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_successful': self.is_successful(),
            'is_pending': self.is_pending(),
            'is_failed': self.is_failed()
        }

# Utility Functions
def create_user_with_profile(email, password, role, profile_data):
    """Create a user with their corresponding profile"""
    try:
        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user_id without committing
        
        # Create profile based on role
        if role == 'admin':
            profile = Admin(admin_id=user.user_id, **profile_data)
        elif role == 'organizer':
            profile = Organizer(organizer_id=user.user_id, **profile_data)
        elif role == 'customer':
            profile = Customer(customer_id=user.user_id, **profile_data)
        else:
            raise ValueError(f"Invalid role: {role}")
        
        db.session.add(profile)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter_by(email=email).first()

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if user and user.check_password(password):
        return user
    return None

def seed_database():
    """Seed the database with initial data"""
    try:
        # Create categories
        categories = [
            'Conference', 'Workshop', 'Concert', 'Sports', 'Social',
            'Technology', 'Business', 'Education', 'Entertainment', 'Health'
        ]
        
        for cat_name in categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name)
                db.session.add(category)
        
        # Create default admin
        admin_email = 'admin@eventhub.com'
        if not get_user_by_email(admin_email):
            create_user_with_profile(
                email=admin_email,
                password='admin123',
                role='admin',
                profile_data={'name': 'System Administrator'}
            )
        
        db.session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")

# Event listeners for automatic timestamp updates
from sqlalchemy import event

@event.listens_for(User, 'before_update')
def update_user_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()

@event.listens_for(Event, 'before_update')
def update_event_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()

@event.listens_for(Booking, 'before_update')
def update_booking_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()
