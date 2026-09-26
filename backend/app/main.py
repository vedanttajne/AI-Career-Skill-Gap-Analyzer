import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = "tesseract"

from app.db import connection 
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from pwdlib import PasswordHash

import io

from pypdf import PdfReader
from docx import Document

app = FastAPI()

# =========================
# Career Skill Requirements
# =========================

CAREER_SKILLS = {
    "AI/ML Engineer": [
        "Python",
        "NumPy",
        "Pandas",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow"
    ],

    "Data Scientist": [
        "Python",
        "NumPy",
        "Pandas",
        "SQL",
        "Machine Learning",
        "Statistics"
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Pandas",
        "Data Visualization",
        "Statistics"
    ],

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "SQL",
        "Git & GitHub"
    ],

    "Software Developer": [
        "Python",
        "Java",
        "C++",
        "SQL",
        "Data Structures",
        "Algorithms",
        "Git & GitHub"
    ],

    "Cybersecurity Analyst": [
        "Networking",
        "Linux",
        "Python",
        "Cybersecurity",
        "Cryptography",
        "Ethical Hacking"
    ],

    "Cloud Engineer": [
        "Linux",
        "Networking",
        "AWS",
        "Docker",
        "Git & GitHub",
        "Python"
    ]
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

password_hash = PasswordHash.recommended()


# =========================
# Request Models
# =========================

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# =========================
# Home API
# =========================

@app.get("/")
def home():
    return {
        "message": "AI Career & Skill Gap Analyzer API is running!"
    }


# =========================
# Health Check API
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================
# Register API
# =========================

@app.post("/register")
def register_user(user: UserRegistration):
    cursor = connection.cursor()

    hashed_password = password_hash.hash(user.password)

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            RETURNING id, name, email;
            """,
            (user.name, user.email, hashed_password)
        )

        new_user = cursor.fetchone()
        connection.commit()

        return {
            "message": "User registered successfully!",
            "user": {
                "id": new_user[0],
                "name": new_user[1],
                "email": new_user[2]
            }
        }

    except Exception:
        connection.rollback()

        raise HTTPException(
            status_code=400,
            detail="Email may already be registered."
        )

    finally:
        cursor.close()


# =========================
# Login API
# =========================

@app.post("/login")
def login_user(user: UserLogin):
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s;
            """,
            (user.email,)
        )

        existing_user = cursor.fetchone()

        if existing_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        user_id = existing_user[0]
        name = existing_user[1]
        email = existing_user[2]
        stored_password = existing_user[3]

        if not stored_password.startswith("$argon2"):
            raise HTTPException(
                status_code=400,
                detail="This account uses an old password format. Please register again."
            )

        password_is_correct = password_hash.verify(
            user.password,
            stored_password
        )

        if not password_is_correct:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        return {
            "message": "Login successful!",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }

    finally:
        cursor.close()
        

# =========================
# Career Analysis API
# =========================

class CareerAnalysis(BaseModel):
    user_id: int
    career: str
    education: str
    experience: str
    skills: list[str]


@app.post("/analyze")
def analyze_career(data: CareerAnalysis):

    if data.career not in CAREER_SKILLS:
        raise HTTPException(
            status_code=400,
            detail="Invalid career selected."
        )

    required_skills = CAREER_SKILLS[data.career]

    student_skills = set(data.skills)

    matched_skills = [
        skill
        for skill in required_skills
        if skill in student_skills
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in student_skills
    ]

    match_percentage = round(
        (len(matched_skills) / len(required_skills)) * 100
    )

    # =========================
    # Save Analysis to Database
    # =========================

    cursor = connection.cursor()

    try:

        # Check user exists
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s;
            """,
            (data.user_id,)
        )

        user_exists = cursor.fetchone()

        if user_exists is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # Insert analysis
        cursor.execute(
            """
            INSERT INTO analysis_history
            (
                user_id,
                career,
                education,
                experience,
                skills,
                matched_skills,
                missing_skills,
                match_percentage
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                data.user_id,
                data.career,
                data.education,
                data.experience,
                data.skills,
                matched_skills,
                missing_skills,
                match_percentage
            )
        )

        connection.commit()

        print("ANALYSIS SAVED SUCCESSFULLY!")

    except HTTPException:
        connection.rollback()
        raise

    except Exception as e:
        connection.rollback()

        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to save career analysis."
        )

    finally:
        cursor.close()

    # =========================
    # Return Analysis Result
    # =========================

    return {
        "career": data.career,
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required_skills": len(required_skills)
    }
@app.post("/career-recommendations")
def career_recommendations(data: CareerAnalysis):

    student_skills = set(data.skills)

    recommendations = []

    for career, required_skills in CAREER_SKILLS.items():

        matched_skills = [
            skill
            for skill in required_skills
            if skill in student_skills
        ]

        missing_skills = [
            skill
            for skill in required_skills
            if skill not in student_skills
        ]

        match_percentage = round(
            (len(matched_skills) / len(required_skills)) * 100
        )

        recommendations.append({
            "career": career,
            "match_percentage": match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        })

    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return {
        "recommendations": recommendations
    }
# =========================
# SKILL PROGRESS TRACKING
# =========================

class SkillProgress(BaseModel):
    user_id: int
    skill: str
    status: str = "Not Started"
    progress: int = 0


@app.post("/skill-progress")
def save_skill_progress(data: SkillProgress):

    if data.status not in [
        "Not Started",
        "In Progress",
        "Completed"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status."
        )

    if data.progress < 0 or data.progress > 100:
        raise HTTPException(
            status_code=400,
            detail="Progress must be between 0 and 100."
        )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM skill_progress
            WHERE user_id = %s AND skill = %s
            """,
            (data.user_id, data.skill)
        )

        existing = cursor.fetchone()

        if existing:

            cursor.execute(
                """
                UPDATE skill_progress
                SET status = %s,
                    progress = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND skill = %s
                """,
                (
                    data.status,
                    data.progress,
                    data.user_id,
                    data.skill
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO skill_progress
                (
                    user_id,
                    skill,
                    status,
                    progress
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    data.user_id,
                    data.skill,
                    data.status,
                    data.progress
                )
            )

        connection.commit()
        cursor.close()

        return {
            "message": "Skill progress saved successfully.",
            "user_id": data.user_id,
            "skill": data.skill,
            "status": data.status,
            "progress": data.progress
        }

    except Exception as e:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/skill-progress/{user_id}")
def get_skill_progress(user_id: int):

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                skill,
                status,
                progress,
                updated_at
            FROM skill_progress
            WHERE user_id = %s
            ORDER BY id
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        cursor.close()

        progress_data = []

        for row in rows:

            progress_data.append({
                "id": row[0],
                "skill": row[1],
                "status": row[2],
                "progress": row[3],
                "updated_at": row[4]
            })

        return {
            "user_id": user_id,
            "skills": progress_data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.delete("/skill-progress/{user_id}/{skill}")
def delete_skill_progress(
    user_id: int,
    skill: str
):

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM skill_progress
            WHERE user_id = %s AND skill = %s
            """,
            (user_id, skill)
        )

        connection.commit()

        deleted = cursor.rowcount

        cursor.close()

        if deleted == 0:
            raise HTTPException(
                status_code=404,
                detail="Skill progress not found."
            )

        return {
            "message": "Skill progress deleted successfully."
        }

    except HTTPException:
        raise

    except Exception as e:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    
# =========================
# RESUME SKILL ANALYZER
# =========================

@app.post("/resume-analyze")
async def analyze_resume(
    career: str = Form(...),
    file: UploadFile = File(...)
):

    if career not in CAREER_SKILLS:
        raise HTTPException(
            status_code=400,
            detail="Invalid career selected."
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume."
        )

    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    resume_text = ""

    try:

        # =========================
        # PDF FILE
        # =========================

        if filename.endswith(".pdf"):

            pdf = fitz.open(stream=file_bytes, filetype="pdf")

            for page in pdf:

                # First try normal PDF text extraction
                text = page.get_text()

                if text.strip():

                    resume_text += text + "\n"

                else:

                    # If PDF is image-based, use OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

                    img = Image.frombytes(
                        "RGB",
                        [pix.width, pix.height],
                        pix.samples
                    )

                    ocr_text = pytesseract.image_to_string(img)

                    resume_text += ocr_text + "\n"

            pdf.close()

        # =========================
        # DOCX FILE
        # =========================

        else:

            document = Document(io.BytesIO(file_bytes))

            for paragraph in document.paragraphs:

                resume_text += paragraph.text + "\n"

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read resume: {str(e)}"
        )

    resume_text = resume_text.lower()

    required_skills = CAREER_SKILLS[career]

    skills_found = []

    for skill in required_skills:

        if skill.lower() in resume_text:
            skills_found.append(skill)

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in skills_found
    ]

    match_percentage = round(
        (len(skills_found) / len(required_skills)) * 100
    )

    return {
        "filename": file.filename,
        "career": career,
        "match_percentage": match_percentage,
        "skills_found": skills_found,
        "missing_skills": missing_skills,
        "skills_to_learn": missing_skills
    }