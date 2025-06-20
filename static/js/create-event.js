// Event Creation Form JavaScript
document.addEventListener("DOMContentLoaded", () => {
  const ticketTypeCount = 1

  // Initialize form
  initializeForm()

  function initializeForm() {
    // Set minimum date to today
    const eventDateInput = document.getElementById("event_date")
    const now = new Date()
    const minDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
    eventDateInput.min = minDate

    // Image preview functionality
    const imageUrlInput = document.getElementById("image_url")
    const imageFileInput = document.getElementById("image_file")

    imageUrlInput.addEventListener("input", handleImageUrlPreview)
    imageFileInput.addEventListener("change", handleImageFilePreview)

    // Form validation
    const form = document.getElementById("eventForm")
    form.addEventListener("submit", handleFormSubmit)

    // Real-time validation
    addRealTimeValidation()
  }

  // Handle image URL preview
  function handleImageUrlPreview() {
    const imageUrl = this.value
    const imageFileInput = document.getElementById("image_file")

    // Clear file input if URL is being used
    if (imageUrl) {
      imageFileInput.value = ""
    }

    if (imageUrl && isValidUrl(imageUrl)) {
      showImagePreview(imageUrl)
    } else if (imageUrl) {
      hideImagePreview()
      showFieldError(document.getElementById("image_url"), "Invalid image URL")
    } else {
      hideImagePreview()
    }
  }

  // Handle image file preview
  function handleImageFilePreview() {
    const file = this.files[0]
    const imageUrlInput = document.getElementById("image_url")

    // Clear URL input if file is being used
    if (file) {
      imageUrlInput.value = ""
      clearFieldError(imageUrlInput)
    }

    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        showFieldError(this, "Please select a valid image file")
        this.value = ""
        return
      }

      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        showFieldError(this, "Image file must be less than 5MB")
        this.value = ""
        return
      }

      // Show preview
      const reader = new FileReader()
      reader.onload = (e) => {
        showImagePreview(e.target.result)
      }
      reader.readAsDataURL(file)

      clearFieldError(this)
    } else {
      hideImagePreview()
    }
  }

  function showImagePreview(src) {
    const preview = document.getElementById("imagePreview")
    const previewImg = document.getElementById("previewImg")

    previewImg.src = src
    preview.style.display = "block"
  }

  function hideImagePreview() {
    const preview = document.getElementById("imagePreview")
    preview.style.display = "none"
  }

  // Remove image function
  window.removeImage = () => {
    document.getElementById("image_url").value = ""
    document.getElementById("image_file").value = ""
    hideImagePreview()
  }

  // Form submission
  function handleFormSubmit(e) {
    e.preventDefault()

    if (validateForm()) {
      const submitBtn = document.querySelector(".btn-primary")
      const originalText = submitBtn.innerHTML

      // Show loading state
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Event...'
      submitBtn.disabled = true

      // Submit form
      setTimeout(() => {
        e.target.submit()
      }, 500)
    }
  }

  // Form validation
  function validateForm() {
    let isValid = true

    // Clear previous errors
    clearAllErrors()

    // Validate required fields
    const requiredFields = document.querySelectorAll("[required]")
    requiredFields.forEach((field) => {
      if (!field.value.trim()) {
        showFieldError(field, "This field is required")
        isValid = false
      }
    })

    // Validate event date
    const eventDate = document.getElementById("event_date")
    if (eventDate.value) {
      const selectedDate = new Date(eventDate.value)
      const now = new Date()
      if (selectedDate <= now) {
        showFieldError(eventDate, "Event date must be in the future")
        isValid = false
      }
    }

    // Validate total seats
    const totalSeats = document.getElementById("total_seats")
    if (totalSeats.value && (Number.parseInt(totalSeats.value) < 1 || Number.parseInt(totalSeats.value) > 10000)) {
      showFieldError(totalSeats, "Total seats must be between 1 and 10,000")
      isValid = false
    }

    // Validate image inputs
    const imageUrl = document.getElementById("image_url")
    const imageFile = document.getElementById("image_file")

    if (imageUrl.value && !isValidUrl(imageUrl.value)) {
      showFieldError(imageUrl, "Please enter a valid URL")
      isValid = false
    }

    if (imageFile.files[0]) {
      const file = imageFile.files[0]
      if (!file.type.startsWith("image/")) {
        showFieldError(imageFile, "Please select a valid image file")
        isValid = false
      }
      if (file.size > 5 * 1024 * 1024) {
        showFieldError(imageFile, "Image file must be less than 5MB")
        isValid = false
      }
    }

    return isValid
  }

  // Real-time validation
  function addRealTimeValidation() {
    const inputs = document.querySelectorAll("input, select, textarea")
    inputs.forEach((input) => {
      input.addEventListener("blur", function () {
        validateField(this)
      })

      input.addEventListener("input", function () {
        clearFieldError(this)
      })
    })
  }

  function validateField(field) {
    const value = field.value.trim()

    // Required field validation
    if (field.hasAttribute("required") && !value) {
      showFieldError(field, "This field is required")
      return false
    }

    // Specific field validations
    switch (field.type) {
      case "email":
        if (value && !isValidEmail(value)) {
          showFieldError(field, "Please enter a valid email address")
          return false
        }
        break
      case "url":
        if (value && !isValidUrl(value)) {
          showFieldError(field, "Please enter a valid URL")
          return false
        }
        break
      case "number":
        if (value && isNaN(value)) {
          showFieldError(field, "Please enter a valid number")
          return false
        }
        if (field.hasAttribute("min") && Number.parseFloat(value) < Number.parseFloat(field.min)) {
          showFieldError(field, `Value must be at least ${field.min}`)
          return false
        }
        if (field.hasAttribute("max") && Number.parseFloat(value) > Number.parseFloat(field.max)) {
          showFieldError(field, `Value must be at most ${field.max}`)
          return false
        }
        break
      case "datetime-local":
        if (value) {
          const selectedDate = new Date(value)
          const now = new Date()
          if (selectedDate <= now) {
            showFieldError(field, "Date must be in the future")
            return false
          }
        }
        break
    }

    showFieldSuccess(field)
    return true
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // Error handling
  function showFieldError(field, message) {
    const formGroup = field.closest(".form-group")
    formGroup.classList.add("error")
    formGroup.classList.remove("success")

    // Remove existing error message
    const existingError = formGroup.querySelector(".error-message")
    if (existingError) {
      existingError.remove()
    }

    // Add new error message
    const errorDiv = document.createElement("div")
    errorDiv.className = "error-message"
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`
    field.parentNode.appendChild(errorDiv)
  }

  function showFieldSuccess(field) {
    const formGroup = field.closest(".form-group")
    formGroup.classList.add("success")
    formGroup.classList.remove("error")

    // Remove error message
    const errorMessage = formGroup.querySelector(".error-message")
    if (errorMessage) {
      errorMessage.remove()
    }
  }

  function clearFieldError(field) {
    const formGroup = field.closest(".form-group")
    formGroup.classList.remove("error", "success")

    const errorMessage = formGroup.querySelector(".error-message")
    if (errorMessage) {
      errorMessage.remove()
    }
  }

  function clearAllErrors() {
    const errorMessages = document.querySelectorAll(".error-message")
    errorMessages.forEach((msg) => msg.remove())

    const formGroups = document.querySelectorAll(".form-group")
    formGroups.forEach((group) => {
      group.classList.remove("error", "success")
    })
  }

  // Save as draft functionality
  window.saveDraft = () => {
    const formData = new FormData(document.getElementById("eventForm"))
    formData.append("status", "draft")

    // Here you would typically save to localStorage or send to server
    showToast("Draft saved successfully!", "success")
  }

  // Toast notification function
  function showToast(message, type = "info") {
    const toast = document.createElement("div")
    toast.className = `toast toast-${type}`
    toast.innerHTML = `
            <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "times-circle" : "info-circle"}"></i>
            <span>${message}</span>
        `

    document.body.appendChild(toast)

    setTimeout(() => {
      toast.style.animation = "slideIn 0.3s ease reverse"
      setTimeout(() => toast.remove(), 300)
    }, 3000)
  }

  function isValidUrl(url) {
    try {
      new URL(url)
      return true
    } catch (_) {
      return false
    }
  }
})
