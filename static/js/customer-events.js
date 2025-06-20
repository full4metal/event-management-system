// Global variables
let currentView = "grid"
let currentEventId = null
let currentTicketPrice = 0
let maxAvailableSeats = 0

// Initialize when document is ready
document.addEventListener("DOMContentLoaded", () => {
  // Initialize user dropdown
  const userMenuBtn = document.querySelector(".user-menu-btn")
  const userDropdown = document.querySelector(".user-dropdown")

  if (userMenuBtn) {
    userMenuBtn.addEventListener("click", () => {
      userDropdown.classList.toggle("show")
    })

    // Close dropdown when clicking outside
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".user-menu")) {
        userDropdown.classList.remove("show")
      }
    })
  }

  // Initialize filters
  filterEvents()
})

// Filter events based on selected criteria
function filterEvents() {
  const categoryFilter = document.getElementById("category-filter").value
  const dateFilter = document.getElementById("date-filter").value
  const priceFilter = document.getElementById("price-filter").value
  const availabilityFilter = document.getElementById("availability-filter").value
  const searchInput = document.getElementById("search-input").value.toLowerCase()

  let visibleCount = 0
  const eventCards = document.querySelectorAll(".event-card")

  eventCards.forEach((card) => {
    const category = card.dataset.category
    const dateStr = card.dataset.date
    const price = Number.parseFloat(card.dataset.price)
    const availability = card.dataset.availability
    const title = card.dataset.title.toLowerCase()
    const location = card.dataset.location.toLowerCase()

    // Category filter
    const categoryMatch = categoryFilter === "all" || category === categoryFilter

    // Date filter
    let dateMatch = true
    if (dateFilter !== "all" && dateStr) {
      const eventDate = new Date(dateStr)
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)

      const nextWeek = new Date(today)
      nextWeek.setDate(nextWeek.getDate() + 7)

      const nextMonth = new Date(today)
      nextMonth.setMonth(nextMonth.getMonth() + 1)

      switch (dateFilter) {
        case "today":
          dateMatch = eventDate.toDateString() === today.toDateString()
          break
        case "tomorrow":
          dateMatch = eventDate.toDateString() === tomorrow.toDateString()
          break
        case "this-week":
          dateMatch = eventDate >= today && eventDate < nextWeek
          break
        case "this-month":
          dateMatch = eventDate >= today && eventDate < nextMonth
          break
      }
    }

    // Price filter
    let priceMatch = true
    if (priceFilter !== "all") {
      switch (priceFilter) {
        case "free":
          priceMatch = price === 0
          break
        case "paid":
          priceMatch = price > 0
          break
        case "under-25":
          priceMatch = price < 25
          break
        case "25-50":
          priceMatch = price >= 25 && price <= 50
          break
        case "50-100":
          priceMatch = price > 50 && price <= 100
          break
        case "over-100":
          priceMatch = price > 100
          break
      }
    }

    // Availability filter
    const availabilityMatch =
      availabilityFilter === "all" ||
      (availabilityFilter === "available" && availability !== "sold-out") ||
      (availabilityFilter === "limited" && availability === "limited")

    // Search filter
    const searchMatch = title.includes(searchInput) || location.includes(searchInput)

    // Apply all filters
    if (categoryMatch && dateMatch && priceMatch && availabilityMatch && searchMatch) {
      card.style.display = ""
      visibleCount++
    } else {
      card.style.display = "none"
    }
  })

  // Show/hide no results message
  const noResults = document.getElementById("no-results")
  const eventsGrid = document.getElementById("events-grid")

  if (visibleCount === 0) {
    noResults.style.display = "flex"
    eventsGrid.style.display = "none"
  } else {
    noResults.style.display = "none"
    eventsGrid.style.display = ""
  }

  // Apply current sort after filtering
  sortEvents()
}

// Sort events based on selected criteria
function sortEvents() {
  const sortSelect = document.getElementById("sort-select")
  const sortValue = sortSelect.value

  const eventsGrid = document.getElementById("events-grid")
  const eventCards = Array.from(document.querySelectorAll(".event-card"))

  // Only sort visible cards
  const visibleCards = eventCards.filter((card) => card.style.display !== "none")

  visibleCards.sort((a, b) => {
    switch (sortValue) {
      case "date-asc":
        return new Date(a.dataset.date) - new Date(b.dataset.date)
      case "date-desc":
        return new Date(b.dataset.date) - new Date(a.dataset.date)
      case "price-asc":
        return Number.parseFloat(a.dataset.price) - Number.parseFloat(b.dataset.price)
      case "price-desc":
        return Number.parseFloat(b.dataset.price) - Number.parseFloat(a.dataset.price)
      case "title-asc":
        return a.dataset.title.localeCompare(b.dataset.title)
      case "title-desc":
        return b.dataset.title.localeCompare(a.dataset.title)
      case "seats-desc":
        return Number.parseInt(b.dataset.seats) - Number.parseInt(a.dataset.seats)
      case "seats-asc":
        return Number.parseInt(a.dataset.seats) - Number.parseInt(b.dataset.seats)
      default:
        return 0
    }
  })

  // Reorder the DOM elements
  visibleCards.forEach((card) => {
    eventsGrid.appendChild(card)
  })
}

// Toggle between grid and list view
function toggleView(view) {
  const eventsGrid = document.getElementById("events-grid")
  const gridBtn = document.querySelector('[data-view="grid"]')
  const listBtn = document.querySelector('[data-view="list"]')

  if (view === "grid") {
    eventsGrid.classList.remove("events-list")
    eventsGrid.classList.add("events-grid")
    gridBtn.classList.add("active")
    listBtn.classList.remove("active")
  } else {
    eventsGrid.classList.remove("events-grid")
    eventsGrid.classList.add("events-list")
    gridBtn.classList.remove("active")
    listBtn.classList.add("active")
  }

  currentView = view
}

// Clear all filters and reset to default
function clearFilters() {
  document.getElementById("category-filter").value = "all"
  document.getElementById("date-filter").value = "all"
  document.getElementById("price-filter").value = "all"
  document.getElementById("availability-filter").value = "all"
  document.getElementById("search-input").value = ""
  document.getElementById("sort-select").value = "date-asc"

  filterEvents()
}

// Open booking modal
function openBookingModal(eventId, eventTitle, availableSeats, ticketPrice) {
  const modal = document.getElementById("bookingModal")
  const modalTitle = document.getElementById("modalEventTitle")
  const bookingForm = document.getElementById("bookingForm")
  const quantityInput = document.getElementById("ticket-quantity")
  const summaryAvailable = document.getElementById("summary-available")
  const summaryPrice = document.getElementById("summary-price")

  // Set global variables
  currentEventId = eventId
  maxAvailableSeats = availableSeats
  currentTicketPrice = ticketPrice

  // Update modal content
  modalTitle.textContent = eventTitle
  bookingForm.action = `/customer/events/${eventId}/book`
  summaryAvailable.textContent = availableSeats
  summaryPrice.textContent = `$${ticketPrice.toFixed(2)}`

  // Reset quantity to 1
  quantityInput.value = 1
  document.getElementById("summary-quantity").textContent = 1
  updateTotalPrice()

  // Set max quantity based on available seats (max 10)
  const maxQuantity = Math.min(10, availableSeats)
  quantityInput.max = maxQuantity

  // Show modal
  modal.style.display = "flex"

  // Add animation class
  setTimeout(() => {
    modal.querySelector(".modal-content").classList.add("show")
  }, 10)
}

// Close booking modal
function closeBookingModal() {
  const modal = document.getElementById("bookingModal")
  const modalContent = modal.querySelector(".modal-content")

  // Remove animation class
  modalContent.classList.remove("show")

  // Hide modal after animation
  setTimeout(() => {
    modal.style.display = "none"
  }, 300)
}

// Change ticket quantity
function changeQuantity(delta) {
  const quantityInput = document.getElementById("ticket-quantity")
  const summaryQuantity = document.getElementById("summary-quantity")

  let newQuantity = Number.parseInt(quantityInput.value) + delta

  // Enforce min/max constraints
  newQuantity = Math.max(1, Math.min(newQuantity, Number.parseInt(quantityInput.max)))

  // Update input and summary
  quantityInput.value = newQuantity
  summaryQuantity.textContent = newQuantity

  // Update total price
  updateTotalPrice()
}

// Update total price based on quantity
function updateTotalPrice() {
  const quantity = Number.parseInt(document.getElementById("ticket-quantity").value)
  const summaryTotal = document.getElementById("summary-total")

  const totalPrice = quantity * currentTicketPrice
  summaryTotal.textContent = `$${totalPrice.toFixed(2)}`
}

// Submit booking form
function submitBooking() {
  const bookingForm = document.getElementById("bookingForm")
  bookingForm.submit()
}

// Close flash messages after a delay
setTimeout(() => {
  const flashMessages = document.querySelector(".flash-messages")
  if (flashMessages) {
    flashMessages.style.opacity = "0"
    setTimeout(() => {
      flashMessages.style.display = "none"
    }, 500)
  }
}, 5000)
