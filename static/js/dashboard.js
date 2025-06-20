// Dashboard JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Auto-hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll(".alert")
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 5000)
  })

  // User menu dropdown functionality
  const userMenuBtn = document.querySelector(".user-menu-btn")
  const userDropdown = document.querySelector(".user-dropdown")

  if (userMenuBtn && userDropdown) {
    // Close dropdown when clicking outside
    document.addEventListener("click", (event) => {
      if (!userMenuBtn.contains(event.target) && !userDropdown.contains(event.target)) {
        userDropdown.style.opacity = "0"
        userDropdown.style.visibility = "hidden"
        userDropdown.style.transform = "translateY(-10px)"
      }
    })
  }

  // Sidebar menu active state
  const currentPath = window.location.pathname
  const menuItems = document.querySelectorAll(".menu-item")

  menuItems.forEach((item) => {
    if (item.getAttribute("href") === currentPath) {
      // Remove active class from all items
      menuItems.forEach((menuItem) => {
        menuItem.classList.remove("active")
      })
      // Add active class to current item
      item.classList.add("active")
    }
  })

  // Animate stat cards on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1"
        entry.target.style.transform = "translateY(0)"
      }
    })
  }, observerOptions)

  // Observe stat cards
  const statCards = document.querySelectorAll(".stat-card")
  statCards.forEach((card) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(20px)"
    card.style.transition = "opacity 0.6s ease, transform 0.6s ease"
    observer.observe(card)
  })

  // Table row hover effects
  const tableRows = document.querySelectorAll("tbody tr")
  tableRows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.backgroundColor = "#f8f9fa"
    })

    row.addEventListener("mouseleave", function () {
      this.style.backgroundColor = ""
    })
  })

  // Confirm delete actions
  const deleteButtons = document.querySelectorAll("[data-confirm]")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      const message = this.getAttribute("data-confirm") || "Are you sure?"
      if (!confirm(message)) {
        e.preventDefault()
      }
    })
  })

  // Auto-refresh dashboard data every 5 minutes
  if (window.location.pathname.includes("/dashboard")) {
    setInterval(() => {
      // Only refresh if the page is visible
      if (!document.hidden) {
        window.location.reload()
      }
    }, 300000) // 5 minutes
  }

  // Add logout confirmation
  const logoutLinks = document.querySelectorAll('a[href*="logout"]')
  logoutLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const confirmLogout = confirm("Are you sure you want to logout?")
      if (!confirmLogout) {
        e.preventDefault()
      }
    })
  })

  // Add visual feedback for logout links
  const logoutMenuItems = document.querySelectorAll(".logout-menu, .logout-link")
  logoutMenuItems.forEach((item) => {
    item.addEventListener("mouseenter", function () {
      this.style.transform = "translateX(5px)"
      this.style.transition = "transform 0.2s ease"
    })

    item.addEventListener("mouseleave", function () {
      this.style.transform = "translateX(0)"
    })
  })
})

// Utility functions
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount)
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

// Show loading state for buttons
function showLoading(button) {
  const originalText = button.textContent
  button.textContent = "Loading..."
  button.disabled = true

  return () => {
    button.textContent = originalText
    button.disabled = false
  }
}

// Toast notification system
function showToast(message, type = "info") {
  const toast = document.createElement("div")
  toast.className = `toast toast-${type}`
  toast.innerHTML = `
        <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "times-circle" : "info-circle"}"></i>
        <span>${message}</span>
    `

  // Add toast styles if not already present
  if (!document.querySelector("#toast-styles")) {
    const styles = document.createElement("style")
    styles.id = "toast-styles"
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
            .toast-info { border-left: 4px solid #2196f3; }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `
    document.head.appendChild(styles)
  }

  document.body.appendChild(toast)

  setTimeout(() => {
    toast.style.animation = "slideIn 0.3s ease reverse"
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}
