// js/auth.js
// Future Firebase Auth integration

const loginBtn = document.getElementById('login-open-btn');
const authModal = document.getElementById('auth-modal');
const closeAuth = document.getElementById('close-auth');
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');

let currentUser = null;

// Open/Close Modal
loginBtn.addEventListener('click', () => {
    if(currentUser) {
        // Logout logic
        currentUser = null;
        loginBtn.innerText = "Login / Register";
        alert("You have successfully logged out.");
    } else {
        authModal.classList.add('active');
    }
});

closeAuth.addEventListener('click', () => {
    authModal.classList.remove('active');
});

// Click outside to close
authModal.addEventListener('click', (e) => {
    if(e.target === authModal) {
        authModal.classList.remove('active');
    }
});

// Tab Switching
authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        authTabs.forEach(t => t.classList.remove('active'));
        authForms.forEach(f => f.classList.remove('active'));
        
        tab.classList.add('active');
        document.getElementById(`${tab.dataset.tab}-form`).classList.add('active');
    });
});

// Form Submissions
document.getElementById('login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    
    // Mock login successful
    currentUser = { email };
    loginBtn.innerText = "Log Out";
    authModal.classList.remove('active');
    alert(`Welcome back, ${email}!`);
});

document.getElementById('register-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    
    // Mock register successful
    currentUser = { email, username };
    loginBtn.innerText = "Log Out";
    authModal.classList.remove('active');
    alert(`Account created successfully for ${username}!`);
});
