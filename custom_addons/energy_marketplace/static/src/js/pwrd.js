try {
    document.addEventListener('DOMContentLoaded', function () {
        var form = document.querySelector('form');
        var continueButton = '';
        var requiredInputs = '';
        var emailInput = '';
        var passwordInput = '';
        var confirmPasswordInput = '';
        var emailError = '';
        var buttons = '';
        var input = '';
        
        if(form){
            continueButton = form.querySelector('button[type="submit"]');
            requiredInputs = form.querySelectorAll('input[required], select[required]');
            emailInput = form.querySelector('input[name="email"]');
            passwordInput = form.querySelector('input[name="password"]');
            confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
            emailError = form.querySelector('.email-feedback');
            buttons = document.querySelectorAll(".user-type-btn");
            if(document.getElementById("user_type")){
                input = document.getElementById("user_type");
                buttons.forEach(btn => {
                    btn.addEventListener("click", function () {
                        input.value = btn.dataset.type;
                        buttons.forEach(b => b.classList.remove("active"));
                        btn.classList.add("active");
                    });
                });
            }
        }

        const passwordError = document.getElementById('password-error');

        let emailValid = false;
        let emailAvailable = false;

        if(emailInput) {
            if (!emailError) {
                emailError = document.createElement('p');
                emailError.className = 'text-danger mt-1 small email-feedback';
                emailInput.parentNode.insertBefore(emailError, emailInput.nextSibling);
            }
        }

        function isValidEmailFormat(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        }

        function validatePasswords() {
            if (!passwordInput || !confirmPasswordInput) return;

            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();

            if (!password || !confirmPassword) {
                if (passwordError) passwordError.style.display = 'none';
                return;
            }

            if (password !== confirmPassword) {
                if (passwordError) {
                    passwordError.textContent = "Passwords do not match.";
                    passwordError.style.display = 'block';
                }
            } else {
                if (passwordError) {
                    passwordError.style.display = 'none';
                }
            }
        }

        function checkAllRequirements() {
            let allFilled = true;
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    allFilled = false;
                    input.classList.remove('input-valid');
                } else if (emailInput){
                    input.classList.remove('input-valid');
                } else {
                    input.classList.add('input-valid');
                }
            });

            let passwordsMatch = true;
            if (passwordInput && confirmPasswordInput) {
                passwordsMatch = passwordInput.value === confirmPasswordInput.value;
            }
            if(emailInput) {
                continueButton.disabled = !(allFilled && emailValid && emailAvailable && passwordsMatch);
            } else{
                continueButton.disabled = !(allFilled);
            }
        }

        async function validateEmail() {
            const email = emailInput.value.trim();

            if (!email) {
                emailError.textContent = "";
                emailValid = false;
                emailAvailable = false;
                emailError.style.display = 'none';
                emailError.style.opacity = '0';
                checkAllRequirements();
                return;
            }

            if (!isValidEmailFormat(email)) {
                emailError.textContent = "Please enter a valid email address.";
                emailValid = false;
                emailAvailable = false;
                checkAllRequirements();
                console.log("Please enter a valid email address.");
                return;
            }

            emailValid = true;

            try {
                const response = await fetch('/register/check_email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: { email: email }
                    })
                });

                const data = await response.json();
                const status = data.result.status;

                if (status === 'free_email') {
                    emailError.textContent = "Please use a business email address.";
                    emailError.style.display = 'block';
                    emailError.style.opacity = '1';
                    if (emailInput) emailInput.classList.remove('valid-input');
                    emailAvailable = false;
                } else if (status === 'domain_used') {
                    emailError.textContent = "This domain is already registered.";
                    emailError.style.display = 'block';
                    emailError.style.opacity = '1';
                    if (emailInput) emailInput.classList.remove('valid-input');
                    emailAvailable = false;
                } else if (status === 'email_taken') {
                    emailError.textContent = "This email is already registered.";
                    emailError.style.display = 'block';
                    emailError.style.opacity = '1';
                    if (emailInput) emailInput.classList.remove('valid-input');
                    emailAvailable = false;
                } else if (status === 'ok') {
                    emailError.textContent = "";
                    emailError.style.display = 'none';
                    emailError.style.opacity = '0';
                    if (emailInput) emailInput.classList.add('valid-input');
                    emailAvailable = true;
                } else {
                    emailError.textContent = "Invalid email. Please try again.";
                    emailError.style.display = 'block';
                    emailError.style.opacity = '1';
                    if (emailInput) emailInput.classList.remove('valid-input');
                    emailAvailable = false;
                }

                checkAllRequirements();

            } catch (error) {
                console.error("Error checking email:", error);
                emailError.textContent = "Server error. Please try again later.";
                emailAvailable = false;
                checkAllRequirements();
            }
        }

        if (passwordInput && confirmPasswordInput) {
            passwordInput.addEventListener('input', function() {
                validatePasswords();
                checkAllRequirements();
            });
            confirmPasswordInput.addEventListener('input', function() {
                validatePasswords();
                checkAllRequirements();
            });
        }

        if (emailInput) {
            emailInput.addEventListener('blur', validateEmail);
        }

        if (requiredInputs && typeof requiredInputs.forEach === 'function') {
            requiredInputs.forEach(input => {
                input.addEventListener('input', checkAllRequirements);
            });
        }
    });
} catch (err) {
    console.error("Error loading pwrd.js:", err);
}

function togglePasswordVisibility(fieldId, icon) {
    const input = document.getElementById(fieldId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash', 'active');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash', 'active');
        icon.classList.add('fa-eye');
    }
}