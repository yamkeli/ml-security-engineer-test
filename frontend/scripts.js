// Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Anti-clickjacking protection
    if (self === top) {
        document.body.style.display = 'block';
    } else {
        top.location = self.location;
    }

    // Initialize CSRF tokens
    initializeCSRFTokens();

    // Add event listeners to navigation buttons
    document.querySelectorAll('nav button').forEach(button => {
        button.addEventListener('click', function() {
            showForm(this.getAttribute('data-form'));
        });
    });

    // Add event listeners to forms
    document.getElementById('signup-form').addEventListener('submit', validateSignupForm);
    document.getElementById('login-form').addEventListener('submit', validateLoginForm);
    document.getElementById('personal-form').addEventListener('submit', validatePersonalForm);
});

// Generate and set CSRF tokens
function generateCSRFToken() {
    return Array.from(crypto.getRandomValues(new Uint8Array(16)))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

function initializeCSRFTokens() {
    document.getElementById('signup-csrf').value = generateCSRFToken();
    document.getElementById('login-csrf').value = generateCSRFToken();
    document.getElementById('personal-csrf').value = generateCSRFToken();
}

// Safe DOM manipulation
function setErrorMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        // Use textContent instead of innerHTML to prevent XSS
        element.textContent = DOMPurify.sanitize(message);
    }
}

// Show the selected form and hide others
function showForm(formId) {
    document.querySelectorAll('.form-section').forEach(form => {
        form.classList.remove('active');
    });
    const formElement = document.getElementById(formId);
    if (formElement) {
        formElement.classList.add('active');
    }
}

// Sanitize input for XSS prevention
function sanitizeInput(input) {
    return DOMPurify.sanitize(input.trim());
}

// Rate limiting state
const attemptCount = {
    signup: 0,
    login: 0,
    personal: 0
};
const lastAttemptTime = {
    signup: 0,
    login: 0,
    personal: 0
};

// Check rate limits
function checkRateLimit(formType) {
    const now = Date.now();
    const timeSinceLastAttempt = now - lastAttemptTime[formType];
    
    // Reset count if more than 10 minutes have passed
    if (timeSinceLastAttempt > 600000) {
        attemptCount[formType] = 0;
    }
    
    // Check attempt count
    if (attemptCount[formType] >= 5) {
        const waitTime = Math.ceil((600000 - timeSinceLastAttempt) / 60000);
        return `Too many attempts. Please try again in ${waitTime} minutes.`;
    }
    
    // Update attempt count and time
    attemptCount[formType]++;
    lastAttemptTime[formType] = now;
    return null;
}

// Validate Sign Up Form
function validateSignupForm(event) {
    event.preventDefault();
    
    // Check rate limit
    const rateLimitError = checkRateLimit('signup');
    if (rateLimitError) {
        alert(rateLimitError);
        return false;
    }
    
    const username = sanitizeInput(document.getElementById('signup-username').value);
    const email = sanitizeInput(document.getElementById('signup-email').value);
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(error => {
        error.textContent = '';
    });
    
    // Username validation
    if (username.length < 3) {
        setErrorMessage('username-error', 'Username must be at least 3 characters');
        isValid = false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        setErrorMessage('signup-email-error', 'Please enter a valid email address');
        isValid = false;
    }
    
    // Password validation
    if (password.length < 8) {
        setErrorMessage('password-error', 'Password must be at least 8 characters');
        isValid = false;
    } else if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
        setErrorMessage('password-error', 'Password must include uppercase, lowercase, and numbers');
        isValid = false;
    }
    
    // Confirm password validation
    if (password !== confirmPassword) {
        setErrorMessage('confirm-password-error', 'Passwords do not match');
        isValid = false;
    }
    
    if (isValid) {
        // In a real app, we would encrypt the data before sending
        alert('Sign up successful!');
        document.getElementById('signup-form').reset();
        document.getElementById('signup-csrf').value = generateCSRFToken();
    }
    
    return false; // Prevent form submission
}

// Validate Login Form
function validateLoginForm(event) {
    event.preventDefault();
    
    // Check rate limit
    const rateLimitError = checkRateLimit('login');
    if (rateLimitError) {
        alert(rateLimitError);
        return false;
    }
    
    const email = sanitizeInput(document.getElementById('login-email').value);
    const password = document.getElementById('login-password').value;
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(error => {
        error.textContent = '';
    });
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        setErrorMessage('login-email-error', 'Please enter a valid email address');
        isValid = false;
    }
    
    // Password validation
    if (password.length < 1) {
        setErrorMessage('login-password-error', 'Please enter your password');
        isValid = false;
    }
    
    if (isValid) {
        // In a real app, we would encrypt the data before sending
        alert('Login successful!');
        document.getElementById('login-form').reset();
        document.getElementById('login-csrf').value = generateCSRFToken();
    }
    
    return false; // Prevent form submission
}

// Validate Personal Information Form
function validatePersonalForm(event) {
    event.preventDefault();
    
    // Check rate limit
    const rateLimitError = checkRateLimit('personal');
    if (rateLimitError) {
        alert(rateLimitError);
        return false;
    }
    
    const fullName = sanitizeInput(document.getElementById('full-name').value);
    const email = sanitizeInput(document.getElementById('personal-email').value);
    const dob = sanitizeInput(document.getElementById('dob').value);
    const ssn = sanitizeInput(document.getElementById('ssn').value);
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(error => {
        error.textContent = '';
    });
    
    // Name validation
    if (fullName.length < 2) {
        setErrorMessage('name-error', 'Please enter your full name');
        isValid = false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        setErrorMessage('personal-email-error', 'Please enter a valid email address');
        isValid = false;
    }
    
    // DOB validation
    if (!dob) {
        setErrorMessage('dob-error', 'Please enter your date of birth');
        isValid = false;
    } else {
        // Validate age (must be at least 18)
        const dobDate = new Date(dob);
        const today = new Date();
        const age = today.getFullYear() - dobDate.getFullYear();
        const monthDiff = today.getMonth() - dobDate.getMonth();
        
        if (age < 18 || (age === 18 && monthDiff < 0) || 
            (age === 18 && monthDiff === 0 && today.getDate() < dobDate.getDate())) {
            setErrorMessage('dob-error', 'You must be at least 18 years old');
            isValid = false;
        }
    }
    
    // SSN validation
    const ssnRegex = /^\d{3}-\d{2}-\d{4}$/;
    if (!ssnRegex.test(ssn)) {
        setErrorMessage('ssn-error', 'Please enter a valid SSN (XXX-XX-XXXX)');
        isValid = false;
    }
    
    if (isValid) {
        // In a real app, we would encrypt the data before sending
        alert('Personal information submitted successfully!');
        document.getElementById('personal-form').reset();
        document.getElementById('personal-csrf').value = generateCSRFToken();
    }
    
    return false; // Prevent form submission
}