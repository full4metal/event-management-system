// Organizer Bookings Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let allBookings = [];
    let filteredBookings = [];
    let currentPage = 1;
    const itemsPerPage = 20;
    let currentSort = { column: 'booking_id', direction: 'desc' };
    
    // Initialize the page
    initializePage();
    
    function initializePage() {
        collectBookingData();
        filteredBookings = [...allBookings];
        setupEventListeners();
        renderTable();
        updatePagination();
        
        // Auto-hide flash messages
        setTimeout(hideFlashMessages, 5000);
    }
    
    function collectBookingData() {
        const rows = document.querySelectorAll('.booking-row');
        allBookings = [];
        
        rows.forEach(row => {
            const booking = {
                booking_id: parseInt(row.dataset.bookingId),
                status: row.dataset.status,
                event_title: row.dataset.eventTitle,
                event_date: row.dataset.eventDate,
                customer_name: row.dataset.customerName,
                customer_email: row.dataset.customerEmail,
                location: row.dataset.location,
                quantity: parseInt(row.dataset.quantity),
                total_amount: parseFloat(row.dataset.totalAmount),
                element: row
            };
            allBookings.push(booking);
        });
    }
    
    function setupEventListeners() {
        // Sort headers
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', function() {
                const column = this.dataset.column;
                sortBookings(column);
            });
        });
        
        // Modal close events
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                closeModal(e.target.id);
            }
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAllModals();
            }
        });
    }
    
    // Filtering functions
    window.filterBookings = function() {
        const statusFilter = document.getElementById('status-filter').value;
        const eventFilter = document.getElementById('event-filter').value;
        const dateFilter = document.getElementById('date-filter').value;
        const searchInput = document.getElementById('search-input').value.toLowerCase();
        
        filteredBookings = allBookings.filter(booking => {
            // Status filter
            const statusMatch = statusFilter === 'all' || booking.status === statusFilter;
            
            // Event filter
            const eventMatch = eventFilter === 'all' || booking.event_title === eventFilter;
            
            // Date filter
            let dateMatch = true;
            if (dateFilter !== 'all' && booking.event_date) {
                const eventDate = new Date(booking.event_date);
                const now = new Date();
                
                switch (dateFilter) {
                    case 'upcoming':
                        dateMatch = eventDate > now;
                        break;
                    case 'past':
                        dateMatch = eventDate < now;
                        break;
                    case 'today':
                        dateMatch = eventDate.toDateString() === now.toDateString();
                        break;
                    case 'this-week':
                        const weekStart = new Date(now.setDate(now.getDate() - now.getDay()));
                        const weekEnd = new Date(now.setDate(now.getDate() - now.getDay() + 6));
                        dateMatch = eventDate >= weekStart && eventDate <= weekEnd;
                        break;
                    case 'this-month':
                        dateMatch = eventDate.getMonth() === now.getMonth() && 
                                   eventDate.getFullYear() === now.getFullYear();
                        break;
                }
            }
            
            // Search filter
            const searchMatch = !searchInput || 
                booking.customer_name.toLowerCase().includes(searchInput) ||
                booking.customer_email.toLowerCase().includes(searchInput) ||
                booking.booking_id.toString().includes(searchInput) ||
                booking.event_title.toLowerCase().includes(searchInput);
            
            return statusMatch && eventMatch && dateMatch && searchMatch;
        });
        
        currentPage = 1;
        renderTable();
        updatePagination();
    };
    
    // Sorting functions
    function sortBookings(column) {
        if (currentSort.column === column) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.column = column;
            currentSort.direction = 'asc';
        }
        
        filteredBookings.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];
            
            // Handle different data types
            if (column === 'event_date') {
                aVal = new Date(aVal || 0);
                bVal = new Date(bVal || 0);
            } else if (column === 'total_amount' || column === 'quantity') {
                aVal = parseFloat(aVal) || 0;
                bVal = parseFloat(bVal) || 0;
            } else if (column === 'booking_id') {
                aVal = parseInt(aVal) || 0;
                bVal = parseInt(bVal) || 0;
            } else {
                aVal = (aVal || '').toString().toLowerCase();
                bVal = (bVal || '').toString().toLowerCase();
            }
            
            if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
            return 0;
        });
        
        updateSortHeaders();
        renderTable();
    }
    
    function updateSortHeaders() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (header.dataset.column === currentSort.column) {
                header.classList.add(`sort-${currentSort.direction}`);
            }
        });
    }
    
    // Table rendering
    function renderTable() {
        const tbody = document.getElementById('bookingsTableBody');
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageBookings = filteredBookings.slice(startIndex, endIndex);
        
        // Hide all rows first
        allBookings.forEach(booking => {
            booking.element.style.display = 'none';
        });
        
        // Show filtered and paginated rows
        pageBookings.forEach(booking => {
            booking.element.style.display = '';
        });
        
        // Update showing info
        document.getElementById('showingStart').textContent = startIndex + 1;
        document.getElementById('showingEnd').textContent = Math.min(endIndex, filteredBookings.length);
        document.getElementById('totalBookings').textContent = filteredBookings.length;
    }
    
    // Pagination
    function updatePagination() {
        const totalPages = Math.ceil(filteredBookings.length / itemsPerPage);
        const paginationButtons = document.getElementById('paginationButtons');
        
        paginationButtons.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        // Previous button
        const prevBtn = createPaginationButton('Previous', currentPage - 1, currentPage === 1);
        paginationButtons.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationButtons.appendChild(createPaginationButton('1', 1));
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'pagination-ellipsis';
                paginationButtons.appendChild(ellipsis);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const btn = createPaginationButton(i.toString(), i, false, i === currentPage);
            paginationButtons.appendChild(btn);
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'pagination-ellipsis';
                paginationButtons.appendChild(ellipsis);
            }
            paginationButtons.appendChild(createPaginationButton(totalPages.toString(), totalPages));
        }
        
        // Next button
        const nextBtn = createPaginationButton('Next', currentPage + 1, currentPage === totalPages);
        paginationButtons.appendChild(nextBtn);
    }
    
    function createPaginationButton(text, page, disabled = false, active = false) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.className = 'pagination-btn';
        if (disabled) btn.disabled = true;
        if (active) btn.classList.add('active');
        
        btn.addEventListener('click', function() {
            if (!disabled && !active) {
                currentPage = page;
                renderTable();
                updatePagination();
            }
        });
        
        return btn;
    }
    
    // Booking actions
    window.viewBookingDetails = function(bookingId) {
        const booking = allBookings.find(b => b.booking_id === bookingId);
        if (!booking) return;
        
        const modal = document.getElementById('bookingModal');
        const modalBody = document.getElementById('bookingModalBody');
        
        const eventDate = booking.event_date ? new Date(booking.event_date) : null;
        
        modalBody.innerHTML = `
            <div class="booking-detail-section">
                <h3>Booking Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Booking ID</span>
                        <span class="detail-item-value">#${booking.booking_id}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Status</span>
                        <span class="detail-item-value">${booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Number of Attendees</span>
                        <span class="detail-item-value">${booking.quantity}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Total Amount</span>
                        <span class="detail-item-value">$${booking.total_amount.toFixed(2)}</span>
                    </div>
                </div>
            </div>
            <div class="booking-detail-section">
                <h3>Event Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Event Name</span>
                        <span class="detail-item-value">${booking.event_title}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Date & Time</span>
                        <span class="detail-item-value">${eventDate ? eventDate.toLocaleDateString() + ' at ' + eventDate.toLocaleTimeString() : 'TBA'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Venue</span>
                        <span class="detail-item-value">${booking.location}</span>
                    </div>
                </div>
            </div>
            <div class="booking-detail-section">
                <h3>Customer Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-item-label">Name</span>
                        <span class="detail-item-value">${booking.customer_name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-item-label">Email</span>
                        <span class="detail-item-value">${booking.customer_email}</span>
                    </div>
                </div>
            </div>
        `;
        
        modal.style.display = 'flex';
    };
    
    window.editBooking = function(bookingId) {
        const booking = allBookings.find(b => b.booking_id === bookingId);
        if (!booking) return;
        
        const modal = document.getElementById('editModal');
        const modalBody = document.getElementById('editModalBody');
        
        modalBody.innerHTML = `
            <form id="editBookingForm">
                <input type="hidden" id="editBookingId" value="${booking.booking_id}">
                <div class="form-group">
                    <label for="editQuantity">Number of Attendees:</label>
                    <input type="number" id="editQuantity" value="${booking.quantity}" min="1" required>
                </div>
                <div class="form-group">
                    <label for="editStatus">Status:</label>
                    <select id="editStatus" required>
                        <option value="booked" ${booking.status === 'booked' ? 'selected' : ''}>Confirmed</option>
                        <option value="cancelled" ${booking.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="editNotes">Notes (optional):</label>
                    <textarea id="editNotes" rows="3" placeholder="Add any notes about this booking..."></textarea>
                </div>
            </form>
        `;
        
        modal.style.display = 'flex';
    };
    
    window.cancelBooking = function(bookingId) {
        if (confirm('Are you sure you want to cancel this booking? This action cannot be undone.')) {
            updateBookingStatus(bookingId, 'cancelled');
        }
    };
    
    window.updateBookingStatus = function(bookingId, newStatus) {
        showLoading();
        
        // Simulate API call
        setTimeout(() => {
            const booking = allBookings.find(b => b.booking_id === bookingId);
            if (booking) {
                booking.status = newStatus;
                booking.element.dataset.status = newStatus;
                
                // Update the status dropdown in the table
                const statusDropdown = booking.element.querySelector('.status-dropdown');
                if (statusDropdown) {
                    statusDropdown.value = newStatus;
                }
                
                showToast(`Booking #${bookingId} status updated to ${newStatus}`, 'success');
            }
            
            hideLoading();
            filterBookings(); // Refresh the display
        }, 1000);
    };
    
    window.saveBookingChanges = function() {
        const bookingId = parseInt(document.getElementById('editBookingId').value);
        const quantity = parseInt(document.getElementById('editQuantity').value);
        const status = document.getElementById('editStatus').value;
        const notes = document.getElementById('editNotes').value;
        
        if (!quantity || quantity < 1) {
            showToast('Please enter a valid number of attendees', 'error');
            return;
        }
        
        showLoading();
        
        // Simulate API call
        setTimeout(() => {
            const booking = allBookings.find(b => b.booking_id === bookingId);
            if (booking) {
                booking.quantity = quantity;
                booking.status = status;
                
                // Update the table row
                booking.element.dataset.quantity = quantity;
                booking.element.dataset.status = status;
                booking.element.querySelector('.attendees-count').textContent = quantity;
                booking.element.querySelector('.status-dropdown').value = status;
                
                showToast(`Booking #${bookingId} updated successfully`, 'success');
                closeModal('editModal');
            }
            
            hideLoading();
            filterBookings(); // Refresh the display
        }, 1000);
    };
    
    // Export functions
    window.exportToCSV = function() {
        const headers = ['Booking ID', 'Event Name', 'Date', 'Venue', 'Attendees', 'Status', 'Customer Name', 'Customer Email', 'Total Cost'];
        const csvContent = [
            headers.join(','),
            ...filteredBookings.map(booking => [
                booking.booking_id,
                `"${booking.event_title}"`,
                booking.event_date ? new Date(booking.event_date).toLocaleDateString() : 'TBA',
                `"${booking.location}"`,
                booking.quantity,
                booking.status,
                `"${booking.customer_name}"`,
                `"${booking.customer_email}"`,
                booking.total_amount.toFixed(2)
            ].join(','))
        ].join('\n');
        
        downloadFile(csvContent, 'bookings.csv', 'text/csv');
        showToast('CSV export completed', 'success');
    };
    
    window.exportToPDF = function() {
        showToast('PDF export feature coming soon', 'info');
    };
    
    window.printBookings = function() {
        const printWindow = window.open('', '_blank');
        const printContent = generatePrintContent();
        
        printWindow.document.write(printContent);
        printWindow.document.close();
        printWindow.print();
    };
    
    window.printBookingDetails = function() {
        showToast('Print booking details feature coming soon', 'info');
    };
    
    // Utility functions
    function downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
    
    function generatePrintContent() {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Bookings Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .header { text-align: center; margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Bookings Report</h1>
                    <p>Generated on ${new Date().toLocaleDateString()}</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Booking ID</th>
                            <th>Event Name</th>
                            <th>Date</th>
                            <th>Attendees</th>
                            <th>Status</th>
                            <th>Customer</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredBookings.map(booking => `
                            <tr>
                                <td>#${booking.booking_id}</td>
                                <td>${booking.event_title}</td>
                                <td>${booking.event_date ? new Date(booking.event_date).toLocaleDateString() : 'TBA'}</td>
                                <td>${booking.quantity}</td>
                                <td>${booking.status}</td>
                                <td>${booking.customer_name}</td>
                                <td>$${booking.total_amount.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </body>
            </html>
        `;
    }
    
    function showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }
    
    function hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
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
    
    function hideFlashMessages() {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.opacity = '0';
            setTimeout(() => {
                flashMessages.style.display = 'none';
            }, 300);
        }
    }
    
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
});