// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAaWadVjfxsww6KWuuPqRnsGlxBjlQqVLQ",
  authDomain: "verifeye-85cb9.firebaseapp.com",
  projectId: "verifeye-85cb9",
  storageBucket: "verifeye-85cb9.firebasestorage.app",
  messagingSenderId: "779518475172",
  appId: "1:779518475172:web:9320c355b3ea85b01edf31",
  measurementId: "G-R03D1D7JNC"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);