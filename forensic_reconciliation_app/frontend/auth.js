document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authMessage = document.getElementById('authMessage');

    // Handle Login Form Submission
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await fetch('http://localhost:5002/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(result.message, 'success');
                localStorage.setItem('token', result.token); // Store JWT token
                // Redirect to data ingestion page or dashboard
                window.location.href = 'ingestion.html';
            } else {
                showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('Error during login:', error);
            showMessage(`Error during login: ${error.message}`, 'error');
        }
    });

    // Handle Register Form Submission
    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        try {
            const response = await fetch('http://localhost:5002/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(result.message, 'success');
                // Log in the user immediately after registration
                localStorage.setItem('token', result.token);
                window.location.href = 'ingestion.html';
            } else {
                showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('Error during registration:', error);
            showMessage(`Error during registration: ${error.message}`, 'error');
        }
    });

    function showMessage(message, type) {
        authMessage.textContent = message;
        authMessage.className = `message ${type}`;
        authMessage.style.display = 'block';
        setTimeout(() => {
            authMessage.style.display = 'none';
        }, 5000);
    }
});