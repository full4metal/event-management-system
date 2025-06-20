// Bookings Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let allBookings = [];
    let filteredBookings = [];
    let currentBookingId = null;
    
    // Initialize the page
    initializePage();
    
    function initializePage() {
        // Collect booking data from DOM elements
        collectBookingDataFromDOM();
        
        if (allBookings.length > 0) {
            filteredBookings = [...allBookings];
            updateVisibility();
        }
        
        // Initialize event listeners
        initializeEventListeners();
        
        // Auto-hide flash messages
        setTimeout(hideFlashMessages, 5000);
    }
    
    function collectBookingDataFromDOM() {
        const bookingCards = document.querySelectorAll('.booking-card');
        allBookings = [];
        
        bookingCards.forEach(card => {
            const booking = {
                booking_id: parseInt(card.dataset.bookingId),
                event_id: parseInt(card.dataset.eventId),
                status: card.dataset.status,
                event_date: card.dataset.eventDate,
                event_title: card.dataset.eventTitle,
                total_amount: parseFloat(card.dataset.totalAmount),
                quantity: parseInt(card.dataset.quantity),
                booking_time: card.dataset.bookingTime,
                payment_status: card.dataset.paymentStatus,
                is_upcoming: card.dataset.isUpcoming === 'true'
            };
            allBookings.push(booking);
        });
    }
    
    function initializeEventListeners() {
        // Modal close events
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                closeModal(e.target.id);
            }
        });
        
        // Star rating events
        const starInputs = document.querySelectorAll('.star-rating input');
        starInputs.forEach(input => {
            input.addEventListener('change', updateStarDisplay);
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAllModals();
            }
        });
    }
    
    function updateVisibility() {
        const upcomingSection = document.getElementById('upcomingSection');
        const pastSection = document.getElementById('pastSection');
        const upcomingBookings = document.getElementById('upcomingBookings');
        const pastBookings = document.getElementById('pastBookings');
        const upcomingCount = document.getElementById('upcomingCount');
        const pastCount = document.getElementById('pastCount');
        
        // Count visible bookings
        const visibleUpcoming = upcomingBookings.querySelectorAll('.booking-card:not([style*="display: none"])').length;
        const visiblePast = pastBookings.querySelectorAll('.booking-card:not([style*="display: none"])').length;
        
        // Update counts
        upcomingCount.textContent = visibleUpcoming;
        pastCount.textContent = visiblePast;
        
        // Show/hide sections
        upcomingSection.style.display = visibleUpcoming > 0 ? 'block' : 'none';
        pastSection.style.display = visiblePast > 0 ? 'block' : 'none';
        
        // Show/hide no results message
        const noResults = document.getElementById('noResults');
        const bookingsContent = document.getElementById('bookingsContent');
        
        if (visibleUpcoming === 0 && visiblePast === 0 && allBookings.length > 0) {
            bookingsContent.style.display = 'none';
            noResults.style.display = 'block';
        } else {
            bookingsContent.style.display = 'block';
            noResults.style.display = 'none';
        }
    }
    
    // Global functions for button actions
    window.viewBookingDetails = function(bookingId) {
        const booking = allBookings.find(b => b.booking_id === bookingId);
        if (!booking) return;
        
        const modal = document.getElementById('bookingModal');
        const modalBody = document.getElementById('bookingModalBody');
        
        const eventDate = new Date(booking.event_date);
        const formattedDate = eventDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const formattedTime = eventDate.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        modalBody.innerHTML = `
            <div class="booking-detail-section">
                <h3>Event Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Event Name</span>
                        <span class="detail-item-value">${booking.event_title || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Date</span>
                        <span class="detail-item-value">${formattedDate}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Time</span>
                        <span class="detail-item-value">${formattedTime}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Status</span>
                        <span class="detail-item-value">${booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}</span>
                    </div>
                </div>
            </div>
            <div class="booking-detail-section">
                <h3>Booking Details</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Booking ID</span>
                        <span class="detail-item-value">#${booking.booking_id}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Booking Date</span>
                        <span class="detail-item-value">${new Date(booking.booking_time).toLocaleDateString()}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Tickets</span>
                        <span class="detail-item-value">${booking.quantity}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Total Amount</span>
                        <span class="detail-item-value">$${booking.total_amount.toFixed(2)}</span>
                    </div>
                </div>
            </div>
            <div class="booking-detail-section">
                <h3>Payment Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Payment Status</span>
                        <span class="detail-item-value">${booking.payment_status || 'Pending'}</span>
                    </div>
                </div>
            </div>
        `;
        
        currentBookingId = bookingId;
        modal.style.display = 'flex';
    };
    
    window.cancelBooking = function(bookingId) {
        const booking = allBookings.find(b => b.booking_id === bookingId);
        if (!booking) return;
        
        const modal = document.getElementById('cancelModal');
        const eventDate = new Date(booking.event_date);
        
        document.getElementById('cancelEventName').textContent = booking.event_title || 'N/A';
        document.getElementById('cancelEventDate').textContent = eventDate.toLocaleDateString();
        document.getElementById('cancelAmount').textContent = `$${booking.total_amount.toFixed(2)}`;
        document.getElementById('cancelForm').action = `/customer/bookings/${bookingId}/cancel`;
        
        modal.style.display = 'flex';
    };
    
    window.rateEvent = function(bookingId) {
        const booking = allBookings.find(b => b.booking_id === bookingId);
        if (!booking) {
            showToast('Booking not found', 'error');
            return;
        }
        
        // Validate that the event has occurred
        const eventDate = new Date(booking.event_date);
        const now = new Date();
        
        if (eventDate > now) {
            showToast('You can only rate events that have already occurred', 'warning');
            return;
        }
        
        // Validate that the booking is confirmed
        if (booking.status !== 'booked') {
            showToast('You can only rate events you have successfully booked', 'warning');
            return;
        }
        
        // Redirect to the feedback form
        window.location.href = `/customer/feedback/${booking.event_id}`;
    };
    
    window.downloadReceipt = function(bookingId) {
        // Show loading state
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        btn.disabled = true;
        
        // Simulate download process
        setTimeout(() => {
            // In a real application, this would trigger an actual download
            // For now, we'll just show a success message
            showToast('Receipt downloaded successfully!', 'success');
            
            // Reset button
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 1500);
    };
    
    // Filter and search functions
    window.filterBookings = function() {
        const statusFilter = document.getElementById('status-filter').value;
        const dateFilter = document.getElementById('date-filter').value;
        const searchInput = document.getElementById('search-input').value.toLowerCase();
        
        const bookingCards = document.querySelectorAll('.booking-card');
        
        bookingCards.forEach(card => {
            const booking = {
                status: card.dataset.status,
                event_date: card.dataset.eventDate,
                event_title: card.dataset.eventTitle,
                is_upcoming: card.dataset.isUpcoming === 'true'
            };
            
            // Status filter
            const statusMatch = statusFilter === 'all' || booking.status === statusFilter;
            
            // Date filter
            let dateMatch = true;
            if (dateFilter !== 'all') {
                const eventDate = new Date(booking.event_date);
                const now = new Date();
                
                switch (dateFilter) {
                    case 'upcoming':
                        dateMatch = booking.is_upcoming;
                        break;
                    case 'past':
                        dateMatch = !booking.is_upcoming;
                        break;
                    case 'this-month':
                        const thisMonth = now.getMonth();
                        const thisYear = now.getFullYear();
                        dateMatch = eventDate.getMonth() === thisMonth && eventDate.getFullYear() === thisYear;
                        break;
                }
            }
            
            // Search filter
            const searchMatch = !searchInput || 
                (booking.event_title && booking.event_title.toLowerCase().includes(searchInput));
            
            // Apply filters
            if (statusMatch && dateMatch && searchMatch) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
        
        updateVisibility();
    };
    
    window.sortBookings = function() {
        const sortValue = document.getElementById('sort-filter').value;
        const upcomingContainer = document.getElementById('upcomingBookings');
        const pastContainer = document.getElementById('pastBookings');
        
        // Sort upcoming bookings
        const upcomingCards = Array.from(upcomingContainer.querySelectorAll('.booking-card'));
        const pastCards = Array.from(pastContainer.querySelectorAll('.booking-card'));
        
        [upcomingCards, pastCards].forEach((cards, index) => {
            const container = index === 0 ? upcomingContainer : pastContainer;
            
            cards.sort((a, b) => {
                const aData = {
                    event_date: new Date(a.dataset.eventDate),
                    total_amount: parseFloat(a.dataset.totalAmount),
                    status: a.dataset.status
                };
                const bData = {
                    event_date: new Date(b.dataset.eventDate),
                    total_amount: parseFloat(b.dataset.totalAmount),
                    status: b.dataset.status
                };
                
                switch (sortValue) {
                    case 'date-asc':
                        return aData.event_date - bData.event_date;
                    case 'date-desc':
                        return bData.event_date - aData.event_date;
                    case 'price-asc':
                        return aData.total_amount - bData.total_amount;
                    case 'price-desc':
                        return bData.total_amount - aData.total_amount;
                    case 'status':
                        return aData.status.localeCompare(bData.status);
                    default:
                        return 0;
                }
            });
            
            // Reorder DOM elements
            cards.forEach(card => container.appendChild(card));
        });
    };
    
    window.clearFilters = function() {
        document.getElementById('status-filter').value = 'all';
        document.getElementById('date-filter').value = 'all';
        document.getElementById('search-input').value = '';
        document.getElementById('sort-filter').value = 'date-desc';
        
        // Show all booking cards
        const bookingCards = document.querySelectorAll('.booking-card');
        bookingCards.forEach(card => {
            card.style.display = '';
        });
        
        updateVisibility();
    };
    
    // Modal functions
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    function closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    // Star rating functions
    function updateStarDisplay() {
        const starInputs = document.querySelectorAll('.star-rating input');
        const starLabels = document.querySelectorAll('.star-rating label');
        
        starLabels.forEach(label => {
            label.style.color = '#ddd';
        });
        
        const checkedInput = document.querySelector('.star-rating input:checked');
        if (checkedInput) {
            const rating = parseInt(checkedInput.value);
            for (let i = 0; i < rating; i++) {
                starLabels[4 - i].style.color = '#ffc107';
            }
        }
    }
    
    // Utility functions
    function hideFlashMessages() {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.opacity = '0';
            setTimeout(() => {
                flashMessages.style.display = 'none';
            }, 300);
        }
    }
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add toast styles if not already present
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                }
                .toast-success { border-left: 4px solid #4caf50; }
                .toast-error { border-left: 4px solid #f44336; }
                .toast-warning { border-left: 4px solid #ff9800; }
                .toast-info { border-left: 4px solid #2196f3; }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});