document.addEventListener('DOMContentLoaded', function() {
    // Card number formatting
    const cardNumberInput = document.getElementById('card_number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            // Remove all non-digits
            let value = this.value.replace(/\D/g, '');
            
            // Limit to 16 digits
            if (value.length > 16) {
                value = value.slice(0, 16);
            }
            
            // Add spaces after every 4 digits
            let formattedValue = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            
            this.value = formattedValue;
        });
    }
    
    // Password validation
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            validatePassword(this.value);
        });
    }
    
    // Form validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = passwordInput.value;
            const isValid = validatePassword(password);
            
            if (!isValid) {
                e.preventDefault();
                alert('Please make sure your password meets all requirements.');
            }
        });
    }
    
    // Password validation function
    function validatePassword(password) {
        const lengthRequirement = document.getElementById('length');
        const uppercaseRequirement = document.getElementById('uppercase');
        const lowercaseRequirement = document.getElementById('lowercase');
        const numberRequirement = document.getElementById('number');
        const specialRequirement = document.getElementById('special');
        
        // Check length
        if (password.length >= 8) {
            lengthRequirement.classList.add('valid');
        } else {
            lengthRequirement.classList.remove('valid');
        }
        
        // Check uppercase
        if (/[A-Z]/.test(password)) {
            uppercaseRequirement.classList.add('valid');
        } else {
            uppercaseRequirement.classList.remove('valid');
        }
        
        // Check lowercase
        if (/[a-z]/.test(password)) {
            lowercaseRequirement.classList.add('valid');
        } else {
            lowercaseRequirement.classList.remove('valid');
        }
        
        // Check number
        if (/[0-9]/.test(password)) {
            numberRequirement.classList.add('valid');
        } else {
            numberRequirement.classList.remove('valid');
        }
        
        // Check special character
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            specialRequirement.classList.add('valid');
        } else {
            specialRequirement.classList.remove('valid');
        }
        
        // Return true if all requirements are met
        return (
            password.length >= 8 &&
            /[A-Z]/.test(password) &&
            /[a-z]/.test(password) &&
            /[0-9]/.test(password) &&
            /[!@#$%^&*(),.?":{}|<>]/.test(password)
        );
    }
    
    // Phone number field validation (numbers only)
    const phoneNumberInput = document.getElementById('phone_number');
    if (phoneNumberInput) {
        phoneNumberInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^\d]/g, '');
        });
    }
    
    // Country code field validation (plus sign and numbers only)
    const countryCodeInput = document.getElementById('country_code');
    if (countryCodeInput) {
        countryCodeInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^\d+]/g, '');
            
            // Ensure it starts with a +
            if (!this.value.startsWith('+')) {
                this.value = '+' + this.value.replace(/\+/g, '');
            }
        });
    }
});