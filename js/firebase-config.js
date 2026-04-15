// js/firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
import { getStorage } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-storage.js";

// =====================================
// STRICTLY ALPHA COIN PROJECT SETTINGS
// =====================================
const firebaseConfig = {
    apiKey: "AIzaSyCQIwr9jzX_ST0Te2OZq5ywbS1_HFgWFDg",
    authDomain: "alpha-coin-and-jewelry.firebaseapp.com",
    projectId: "alpha-coin-and-jewelry",
    storageBucket: "alpha-coin-and-jewelry.firebasestorage.app",
    messagingSenderId: "1097245876446",
    appId: "1:1097245876446:web:d6baf352d37114e8c7624f",
    measurementId: "G-RF9B1GDZW0"
};

// Initialize Firebase only if config is provided
let app, auth, db, storage;

if (firebaseConfig.apiKey) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    storage = getStorage(app);
    console.log("Firebase initialized successfully, Storage bucket connected.");
} else {
    console.warn("Firebase config is missing. Operating in mock data mode.");
}

export { auth, db, storage };
