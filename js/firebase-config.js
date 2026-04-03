// js/firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

// TODO: Replace the following with your app's Firebase project configuration
const firebaseConfig = {
    // apiKey: "YOUR_API_KEY",
    // authDomain: "your-app.firebaseapp.com",
    // projectId: "your-project",
    // storageBucket: "your-project.appspot.com",
    // messagingSenderId: "123456789",
    // appId: "YOUR_APP_ID"
};

// Initialize Firebase only if config is provided
let app, auth, db;

if (firebaseConfig.apiKey) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    console.log("Firebase initialized successfully");
} else {
    console.warn("Firebase config is missing. Operating in mock data mode.");
}

export { auth, db };
