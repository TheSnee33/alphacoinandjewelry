import { auth, db } from "./firebase-config.js";
import { setPersistence, browserSessionPersistence, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { doc, setDoc, getDoc, updateDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

const loginBtn = document.getElementById('login-open-btn');
const authModal = document.getElementById('auth-modal');
const closeAuth = document.getElementById('close-auth');
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');

let currentUser = null;

// Force logout on tab close
setPersistence(auth, browserSessionPersistence).catch((error) => {
  console.error("Persistence error:", error);
});

// Sync cart function for app.js to call
window.syncCart = async () => {
    if(currentUser && window.app) {
        try {
            await updateDoc(doc(db, "users", currentUser.uid), {
                cart: window.app.cartItems
            });
        } catch(e) { console.error("Error syncing cart: ", e); }
    }
};

// Session Persistence Setup
onAuthStateChanged(auth, async (user) => {
    if (user) {
        currentUser = user;
        loginBtn.innerText = "Log Out";
        // Restore cart from DB
        try {
            const userDoc = await getDoc(doc(db, "users", user.uid));
            if(userDoc.exists() && userDoc.data().cart) {
                if(window.app) {
                    window.app.cartItems = userDoc.data().cart;
                    window.app.updateCartBadge();
                    if(window.location.hash.includes('cart')) window.app.navigate('cart');
                }
            }
        } catch (e) { console.error("Cart restore error", e); }
    } else {
        currentUser = null;
        loginBtn.innerText = "Login / Register";
        if(window.app) {
            window.app.cartItems = [];
            window.app.updateCartBadge();
            if(window.location.hash.includes('cart')) window.app.navigate('cart');
        }
    }
});

// Open/Close Modal
loginBtn.addEventListener('click', async () => {
    if(currentUser) {
        try {
            await signOut(auth);
            alert("You have successfully logged out.");
            window.app.navigate('home');
        } catch (error) {
            console.error("Logout Error:", error);
        }
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

// Login Submission
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        await signInWithEmailAndPassword(auth, email, password);
        authModal.classList.remove('active');
        alert(`Welcome back, ${email}!`);
    } catch (error) {
        alert("Login Error: " + error.message);
    }
});

// Register Submission
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Auto-create Account Folder in Firestore Database for tracking future user data
        await setDoc(doc(db, "users", user.uid), {
            uid: user.uid,
            email: email,
            username: username,
            createdAt: serverTimestamp()
        });

        authModal.classList.remove('active');
        alert(`Account created successfully for ${username}!`);
    } catch (error) {
        alert("Registration Error: " + error.message);
    }
});
