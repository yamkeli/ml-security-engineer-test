// Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Anti-clickjacking protection
    if (self === top) {
        document.body.style.display = 'block';
    } else {
        top.location = self.location;
    }

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

    // ---load form data on load if avalidable---
    loadFormData();

});

const baseUrl = ''

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

async function postApi(url, payload, credentials) {
    try {
        const response = await fetch(baseUrl+url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload),
          ...(credentials ? { credentials: "include" } : {})
        });
    
        if (response.ok) {
          const result = await response.json();
          return result
        } else {
          console.error('Failed to submit:', response.statusText);
        }
      } catch (err) {
        console.error('Error submitting payload:', err);
      }
    
}

async function loadFormData() {
    let result = null;
    try {
        const response = await fetch(baseUrl+'/api/v1/form/load', {
          method: 'GET',
        });
    
        if (response.ok) {
          result = await response.json();
        } else {
          console.error('Failed to get:', response.statusText);
        }
      } catch (err) {
        console.error('Error getting payload:', err);
      }
      if (result) {
        const name = result.name;
        const email = result.email;
        const dob = result.dob;
        const ssn = result.ssn;

        document.getElementById('full-name').value = name;
        document.getElementById('full-name').disabled = true;

        document.getElementById('personal-email').value = email;
        document.getElementById('personal-email').disabled = true;

        document.getElementById('dob').value =dob;
        document.getElementById('dob').disabled = true;

        document.getElementById('ssn').value = ssn;
        document.getElementById('ssn').disabled = true;

    }
}


// Validate Sign Up Form
async function validateSignupForm(event) {
    event.preventDefault();
    
   
    const username = sanitizeInput(document.getElementById('signup-username').value);
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(error => {
        error.textContent = '';
    });
    
    // Username validation
    if (username.length < 3 || !username.match(/^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$/)) {
        setErrorMessage('username-error', 'Username must be at least 3 characters and follow the format.');
        isValid = false;
    }
    
    // Password validation
    if (password.length < 8) {
        setErrorMessage('password-error', 'Password must be at least 8 characters');
        isValid = false;
    } else if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password) || !/[^a-zA-Z0-9\s]/.test(password)) {
        setErrorMessage('password-error', 'Password must include uppercase, lowercase, numbers and symbols.');
        isValid = false;
    }
    
    // Confirm password validation
    if (password !== confirmPassword) {
        setErrorMessage('confirm-password-error', 'Passwords do not match');
        isValid = false;
    }
    
    if (isValid) {
        const payload = {
            username: username,
            password: password,
            confirm_password: confirmPassword,
        }

        const result = await postApi('/api/v1/auth/signup', payload)
        const responseUsername = result.username

        if (result) {
            alert(`Sign up successful! Welcome ${sanitizeInput(responseUsername)}`);
            document.getElementById('signup-form').reset();
        }
    }
    
    return false; // Prevent form submission
}

// Validate Login Form
async function validateLoginForm(event) {
    event.preventDefault();
    
    const username = sanitizeInput(document.getElementById('login-username').value);
    const password = document.getElementById('login-password').value;
    
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('.error').forEach(error => {
        error.textContent = '';
    });
    
    // Username validation
    if (username.length < 3 || !username.match(/^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$/)) {
        setErrorMessage('login-username-error', 'Username must be at least 3 characters and follow the format.');
        isValid = false;
    }
    
    // Password validation
    if (password.length < 1) {
        setErrorMessage('login-password-error', 'Please enter your password');
        isValid = false;
    }
    
    if (isValid) {
        const payload = {
            username: username,
            password: password        
        }

        const result = await postApi('/api/v1/auth/login', payload)
        const responseUsername = result.username

        if (result) {
            alert(`Login successful! Welcome ${sanitizeInput(responseUsername)}`);
            document.getElementById('login-form').reset();
        }
    }
    
    return false; // Prevent form submission
}

// Validate Personal Information Form
async function validatePersonalForm(event) {
    event.preventDefault();
    
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
    }
    
    // SSN validation
    const ssnRegex = /^\d{3}-\d{2}-\d{4}$/;
    if (!ssnRegex.test(ssn)) {
        setErrorMessage('ssn-error', 'Please enter a valid SSN (XXX-XX-XXXX)');
        isValid = false;
    }
    
    if (isValid) {
        const payload = {
            name: fullName,
            dob: dob,
            email: email,        
            ssn: ssn,        
        }

        const result = await postApi('/api/v1/form/submit', payload)
        if (result) {
            alert('Personal information submitted successfully!');
            document.getElementById('personal-form').reset();
        }
    }
    
    return false; // Prevent form submission
}