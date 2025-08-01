# Event Management System

A comprehensive web application for managing events, bookings, and feedback.

## Overview

The Event Management System is a full-featured platform that connects event organizers with customers. It provides tools for creating and managing events, handling ticket bookings, collecting customer feedback, and analyzing sentiment to improve future events.

## Features

### For Customers
- Browse and search for events by category, date, price, and availability
- Book tickets for events with secure payment processing
- View booking history and manage reservations
- Provide feedback and ratings for attended events

### For Organizers
- Create and manage events with detailed information
- Track bookings and attendee information
- View and analyze customer feedback
- Access sentiment analysis to understand customer satisfaction
- Generate reports on event performance

### For Administrators
- Approve or reject event submissions
- Manage event categories
- Monitor platform activity
- Access comprehensive reports and analytics

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Custom user authentication system
- **Analytics**: TextBlob and VADER for sentiment analysis

## Installation and Setup

### Prerequisites
- Python 3.9+
- MySQL Server
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/event-management-system.git
   cd event-management-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the MySQL database:
   - Create a database named `event_management`
   - Import the database schema from `event_management.sql`

5. Configure the database connection in `app.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/event_management'
   ```

6. Create an admin user:
   ```
   python create_admin.py
   ```

7. Run the application:
   ```
   python app.py
   ```

8. Access the application at `http://localhost:5000`

## Project Structure

- `app.py`: Main application file with Flask configuration
- `models.py`: Database models and utility functions
- `create_admin.py`: Script to create an admin user
- `requirements.txt`: List of Python dependencies
- `routes/`: Directory containing route handlers
  - `main.py`: Main routes (home, login, register)
  - `admin.py`: Admin-specific routes
  - `organizer.py`: Organizer-specific routes
  - `customer.py`: Customer-specific routes
- `static/`: Static assets (CSS, JavaScript, images)
- `templates/`: HTML templates
- `utils/`: Utility functions
  - `sentiment_analyzer.py`: Sentiment analysis functionality

## User Roles

### Customer
- Can browse and book events
- Can view booking history
- Can provide feedback for attended events
- Can manage personal profile

### Organizer
- Can create and manage events
- Can view bookings for their events
- Can access feedback and sentiment analysis
- Can manage organizer profile

### Admin
- Can approve/reject events
- Can manage categories
- Can view all bookings and feedback
- Can access system-wide reports

## API Documentation

The application provides several internal APIs for sentiment analysis and data retrieval:

### Sentiment Analysis API
- `GET /organizer/api/sentiment-analysis`: Get sentiment analysis for all events
- `GET /organizer/api/sentiment-analysis/<event_id>`: Get sentiment analysis for a specific event

## Database Schema

The system uses the following main tables:

- `users`: Stores user authentication information
- `customers`: Customer profile information
- `organizers`: Organizer profile information
- `admins`: Admin profile information
- `events`: Event details
- `categories`: Event categories
- `bookings`: Ticket booking information
- `payments`: Payment records
- `feedback`: Customer reviews and ratings

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Demo Accounts

For testing purposes, you can use the following demo accounts:

- **Admin**:
  - Email: admin@gmail.com
  - Password: admin123

- **Organizer**:
  - Email: linkin@gmail.com
  - Password: demo123

- **Customer**:
  - Email: cathy@gmail.com
  - Password: demo123
