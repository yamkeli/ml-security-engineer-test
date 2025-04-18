let loggedIn = false;

// Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', async function() {
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

    document.getElementById('signout-btn').addEventListener('click', logOut);

    // Add event listeners to forms
    document.getElementById('signup-form').addEventListener('submit', validateSignupForm);
    document.getElementById('login-form').addEventListener('submit', validateLoginForm);
    document.getElementById('personal-form').addEventListener('submit', validatePersonalForm);

    // ---load form data on load if avalidable---
    loggedIn = await loadFormData();
    console.log(loggedIn);
    if (loggedIn) {
        showForm('personal');
        showLogOut();
    }
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

async function logOut() {
    alert("IMPORTANT: This sign out does not invalidate your session.")
    try {
        const response = await fetch(baseUrl+'/api/v1/auth/logout', {
          method: 'GET',
        });
    
        if (response.ok) {
          const result = await response.json();
          showForm('login');
          loggedIn = false;
          hideLogOut();
          alert("Sign out successful")
          
          document.getElementById('full-name').value = '';
          document.getElementById('full-name').disabled = false;
  
          document.getElementById('personal-email').value = '';
          document.getElementById('personal-email').disabled = false;
  
          document.getElementById('dob').value ='';
          document.getElementById('dob').disabled = false;
  
          document.getElementById('ssn').value = '';
          document.getElementById('ssn').disabled = false;

        
        } else {
          console.error('Failed to get:', response.statusText);
        }
      } catch (err) {
        console.error('Error getting payload:', err);
      }
}

function hideLogOut() {
    document.getElementById('signout-btn').style.display = 'none';
}

function showLogOut() {
    document.getElementById('signout-btn').style.display = 'inline';
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
        const name = sanitizeInput(result.name);
        const email = sanitizeInput(result.email);
        const dob = sanitizeInput(result.dob);
        const ssn = sanitizeInput(result.ssn);

        document.getElementById('full-name').value = name;
        document.getElementById('full-name').disabled = true;

        document.getElementById('personal-email').value = email;
        document.getElementById('personal-email').disabled = true;

        document.getElementById('dob').value =dob;
        document.getElementById('dob').disabled = true;

        document.getElementById('ssn').value = ssn;
        document.getElementById('ssn').disabled = true;

        return true
    }
    return false
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
            showForm('personal');
            showLogOut();
        } else {
            alert("An error has occured, please try again");
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

        const result = await postApi('/api/v1/auth/login', payload, true)
        const responseUsername = result.username

        if (result) {
            alert(`Login successful! Welcome ${sanitizeInput(responseUsername)}`);
            document.getElementById('login-form').reset();
            showForm('personal');
            loadFormData();
            showLogOut();
        } else {
            alert("An error has occured, please try again");
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
            loadFormData();
        } else {
            alert("An error has occured, please try again");
        }
    }
    
    return false; // Prevent form submission
}