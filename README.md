# AI Career & Skill Gap Analyzer

An AI-based career guidance web application that analyzes a student's skills, identifies skill gaps, recommends suitable career roles, and provides personalized learning guidance.

## 🚀 Live Project

🌐 **Website:**  
https://ai-career-skill-analyzer.vercel.app/

## 📌 Project Overview

The **AI Career & Skill Gap Analyzer** helps students understand their current technical skills and discover what skills they need to develop for their desired career.

The system allows users to:

- Register and login securely
- Select a career goal
- Enter education and experience
- Select their current skills
- Analyze their career skill gap
- Get career recommendations
- View matched and missing skills
- Follow a personalized skill roadmap
- Track learning progress
- Explore job roles
- Take skill assessment quizzes
- Analyze a resume and identify matching/missing skills
- Find recommended learning resources

## ✨ Features

### 🔐 User Authentication
- User registration
- Secure login
- Password hashing
- User-specific data

### 🎯 Career Analysis
Analyzes the user's current skills against the required skills for the selected career.

### 💼 Career Recommendations
Suggests suitable career roles based on the user's existing skills.

### 🧠 Skill Gap Analysis
Identifies:
- Matched skills
- Missing skills
- Skill gap percentage
- Skills that should be learned

### 🗺️ Personalized Learning Roadmap
Provides a learning path based on missing skills and groups skills into different learning levels.

### 📈 Progress Tracking
Users can track the progress of individual skills.

### 📄 Resume Skill Checker
Users can upload a PDF or DOCX resume and compare the skills mentioned in the resume with the selected career requirements.

The system supports OCR for image-based PDF resumes.

### 📝 Skill Assessment
Users can test their knowledge through skill-based quizzes.

### 💻 Job Role Explorer
Explore different technical career roles and their required skills.

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn

### Database
- PostgreSQL
- Supabase

### Resume Processing
- PyMuPDF
- Tesseract OCR
- pytesseract
- python-docx
- pypdf

### Security
- Argon2 password hashing
- pwdlib

## 🏗️ Project Architecture

```text
User
  │
  ▼
Frontend
(Vercel)
  │
  ▼
FastAPI Backend
(Render)
  │
  ├── Career Analysis
  ├── Career Recommendations
  ├── Skill Progress
  └── Resume Analysis
  │
  ▼
Supabase PostgreSQL

📂 Project Structure

AI-Career-Skill-Gap-Analyzer/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── db.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   └── ...
│
└── README.md
