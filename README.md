<div align="center">

# 🎓 Smart Study Planner
**The Ultimate AI-Driven & Cloud-Powered Productivity Dashboard for Students**

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-black?logo=flask)](https://flask.palletsprojects.com/)
[![Firebase](https://img.shields.io/badge/Database-Firestore-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

*An intelligent, highly-gamified application that transforms your exam preparation into a structured, rewarding, and visually stunning experience.*

</div>

---

## 🌟 Overview

The **Smart Study Planner** goes beyond traditional to-do lists. It analyzes your syllabus completion, required sleep, fixed commitments (like college hours), and distraction habits to mathematically generate a **perfectly optimized daily timetable**. 

Recently upgraded to a fully serverless cloud architecture, it features real-time data syncing, Google Sign-In, and an advanced gamification system designed to keep you motivated.

---

## 🚀 Key Features

### 🔐 Enterprise-Grade Security & Authentication
*   **Google Sign-In**: Frictionless 1-click login using Firebase Authentication.
*   **Secure Email/Password**: Fully encrypted credential management.
*   **Firebase Admin SDK**: Cryptographically secure backend routing.

### 🧠 Intelligent Timetable Engine
*   **Conflict-Free Scheduling**: Automatically schedules study blocks around your fixed college hours and ensures a minimum of 7-8 hours of sleep.
*   **Break Integration**: Micro-breaks are intelligently placed within study sessions to maximize retention.
*   **PDF Exports**: Download your custom-generated study plans natively as a beautifully formatted PDF.

### 📊 Cloud-Native Dashboard (Firestore)
*   **Real-time Synchronization**: All data (plans, stats, logs) is securely isolated and streamed from a NoSQL Google Cloud Firestore dataset.
*   **Data Insights**: Visualized charts comparing "Study vs. Distraction" hours based on your personal inputs.

### 🏆 Gamification & Progression System
*   **Dynamic Streaks**: Check in daily to build your 🔥 Study Streak.
*   **Achievement Badges**: Unlock badges in real-time as you progress:
    *   `Master Planner`: Create your first study plan.
    *   `Streak Warrior`: Maintain a 3-day study streak.
    *   `Consistent Scholar`: Successfully complete 5 separate check-ins.
    *   `Productivity King`: Achieve a study efficiency score of 90% or higher.

### 🎨 Premium UI / UX
*   **Deep Space Aesthetics**: A sleek dark mode built with deep indigo, purple gradients, and glassmorphism elements.
*   **Micro-Animations**: Fluid transitions, hover styling, and dynamic element rendering.
*   **Fluid Responsive**: Perfect scaling from 4K desktop monitors down to mobile devices.

---

## 🛠️ Tech Stack

### Backend
*   **Python 3** & **Flask** (Core Application Framework)
*   **Firebase Admin SDK** (Authentication Verification & Cloud Database Connection)
*   **XHTML2PDF** (Dynamic HTML-to-PDF compilation)

### Database
*   **Google Cloud Firestore** (NoSQL Document Database)

### Frontend
*   **HTML5 / Vanilla CSS3** (Custom Utility Classes, Glassmorphism, CSS Variables)
*   **JavaScript (ES6)** (Asynchronous Fetching, DOM Manipulation, Chart.js)
*   **Firebase JS SDK v9 Compat** (Frontend Google Provider & Session Auth)
*   **FontAwesome v6** & **Google Fonts** (Syne, Outfit, Inter)

---

## ⚙️ Local Setup & Installation

Follow these steps to run the Smart Study Planner locally on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/muletushar0007/Smart-Study-Planner.git
cd Smart-Study-Planner
```

### 2. Install Dependencies
Make sure you have Python installed. Run the following command to grab all required libraries:
```bash
pip install flask firebase-admin python-dotenv matplotlib xhtml2pdf
```

### 3. Setup Firebase Configuration
Because this app uses Google Cloud, you need to configure your own hidden environment variables.
1. Create a `.env` file in the root directory.
2. Add your Firebase Web config keys:
```env
FLASK_SECRET_KEY=your_super_secret_key_here

FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project_id.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id

FIREBASE_SERVICE_ACCOUNT_PATH=service-account-file.json
```
3. Download your Firebase Admin **Service Account JSON** from the Firebase Console (Project Settings > Service Accounts > Generate New Private Key). Name it `service-account-file.json` and place it in the root folder. **DO NOT commit this file to GitHub!**

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000/`.

---

## 📂 Project Structure

```text
Smart-Study-Planner/
│
├── app.py                      # Main Flask Backend Logic & Routes
├── requirements.txt            # Python Dependencies
├── .env                        # Environment Variables (Keep Secret) 
├── service-account-file.json   # Firebase Admin Keys (Keep Secret)
│
├── templates/
│   ├── index.html              # Landing Page
│   ├── login.html              # Login & Google Auth Portal
│   ├── register.html           # Email/Password Registration
│   ├── dashboard.html          # Main Gamified User Hub
│   ├── planner.html            # Study Plan Generation Wizard
│   └── result.html             # Generated Timetable & Stats View
│   
└── static/
    ├── style.css               # Global CSS & Design System
    ├── result.css              # Result Page specific styling
    └── firebase-config.js      # Obfuscated Frontend config logic
```

---

<div align="center">
  <p><b>Stay Focused, Stay Smart! 🚀</b></p>
  <sub>Made with ❤️ by <a href="https://github.com/muletushar0007">Tushar Mule</a></sub>
</div>
