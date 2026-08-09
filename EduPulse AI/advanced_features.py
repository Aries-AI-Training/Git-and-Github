from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

app = FastAPI(title="EduPulse AI - Integrated Academic Engine", version="10.0",redirect_slashes=False)

# Enable CORS completely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_IT_DEGREE_HOURS = 132

HU_IT_MAJORS_COURSES = {
    "AI_DS": {
        "name": "Data Science & Artificial Intelligence",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Java 1 (OOP)", "hours": 3},
            {"name": "Data Structures", "hours": 3},
            {"name": "Algorithms", "hours": 3},
            {"name": "Database Fundamentals", "hours": 3},
            {"name": "Artificial Intelligence Basics", "hours": 3},
            {"name": "Machine Learning", "hours": 3},
            {"name": "Deep Learning", "hours": 3},
            {"name": "Statistics", "hours": 3},
            {"name": "Discrete Math", "hours": 3},
            {"name": "Digital Logic", "hours": 3},
            {"name": "Computer Networks", "hours": 3}
        ]
    },
    "SWE": {
        "name": "Software Engineering",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Java 1 (OOP)", "hours": 3},
            {"name": "Data Structures", "hours": 3},
            {"name": "Software Architecture", "hours": 3},
            {"name": "Software Testing", "hours": 3},
            {"name": "Web Development", "hours": 3}
        ]
    },
    "CS": {
        "name": "Computer Science",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Java 1 (OOP)", "hours": 3},
            {"name": "Data Structures", "hours": 3},
            {"name": "Algorithms", "hours": 3},
            {"name": "Operating Systems (OS)", "hours": 3},
            {"name": "Computer Networks", "hours": 3}
        ]
    },
    "CYS": {
        "name": "Cyber Security",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Python Programming", "hours": 3},
            {"name": "Data Structures", "hours": 3},
            {"name": "Ethical Hacking", "hours": 3},
            {"name": "Malware Analysis", "hours": 3},
            {"name": "Network Security", "hours": 3}
        ]
    },
    "CIS": {
        "name": "Computer Information Systems",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Database Fundamentals", "hours": 3},
            {"name": "Systems Analysis & Design", "hours": 3},
            {"name": "Management Information Systems", "hours": 3}
        ]
    },
    "BIT": {
        "name": "Business Information Technology",
        "courses": [
            {"name": "C++ Programming", "hours": 3},
            {"name": "Web Development", "hours": 3},
            {"name": "E-Commerce", "hours": 3},
            {"name": "Cloud Computing", "hours": 3}
        ]
    }
}

MOCK_ITZONE_WEEKLY_CONTENT = {
    "Artificial Intelligence Basics": [
        {"objectives": "Intro to AI, Agents, Environments (Ch 1)", "itzone": "itzoneplus.com/search?q=AI"},
        {"objectives": "Uninformed Search (BFS, DFS) (Ch 2)", "itzone": "itzoneplus.com/search?q=BFS"}
    ],
    "Deep Learning": [
        {"objectives": "Perceptrons, Linear Regression (Ch 1)", "itzone": "itzoneplus.com/search?q=DL"}
    ],
    "Machine Learning": [
        {"objectives": "Intro to Supervised vs Unsupervised (Ch 1)", "itzone": "itzoneplus.com/search?q=ML"}
    ]
}

class ProfileRequest(BaseModel):
    name: str
    gpa: float = Field(..., ge=0.0, le=4.0)
    major: str
    credit_passed: int = Field(..., ge=0, le=132)

class WeeklyPlanRequest(BaseModel):
    selected_courses_names: List[str]
    week_number: int = 1

class QuizEvaluateRequest(BaseModel):
    week_number: int
    answers: Dict[str, int]

class FinalExamEvaluateRequest(BaseModel):
    enrolled_courses_names: List[str]
    answers: Dict[str, int]

# Handle both POST and OPTIONS to prevent Method Not Allowed
@app.api_route("/students/save-profile", methods=["POST", "GET"])
def save_profile(payload: Optional[ProfileRequest] = None):
    if payload is None:
        # Fallback dummy response for browser GET checks
        return {"status": "Endpoint Active"}

    if payload.credit_passed > MAX_IT_DEGREE_HOURS:
        raise HTTPException(
            status_code=400, 
            detail=f"Passed credit hours cannot exceed maximum degree total of {MAX_IT_DEGREE_HOURS} hours!"
        )

    major_data = HU_IT_MAJORS_COURSES.get(payload.major, {"name": "IT Major", "courses": []})
    
    support_message = "Keep pushing forward! Your potential is unlimited. 💪"
    if payload.gpa >= 3.5:
        support_message = f"Incredible work, {payload.name}! Your GPA is outstanding ({payload.gpa}). Keep up the high standard! 🌟"
    elif payload.gpa < 2.0:
        support_message = f"Don't get discouraged, {payload.name}. This semester is a fresh start. EduPulse AI is here to support you! 🎯"

    return {
        "status": "Profile Saved",
        "profile": payload,
        "available_major_courses": major_data["courses"],
        "max_degree_hours": MAX_IT_DEGREE_HOURS,
        "remaining_hours": MAX_IT_DEGREE_HOURS - payload.credit_passed,
        "support_message": support_message
    }

@app.api_route("/students/generate-weekly-plan", methods=["POST", "GET"])
def generate_weekly_plan(payload: Optional[WeeklyPlanRequest] = None):
    if payload is None:
        return {"status": "Endpoint Active"}

    plan_details = []
    quiz_questions = []

    for idx, course_name in enumerate(payload.selected_courses_names):
        weekly_content = MOCK_ITZONE_WEEKLY_CONTENT.get(course_name, [{"objectives": f"Core Fundamentals & Setup for {course_name}", "itzone": "itzoneplus.com"}])
        current_content_obj = weekly_content[min(payload.week_number - 1, len(weekly_content)-1)]
        
        plan_details.append({
            "course": course_name,
            "credit_hours": 3,
            "weekly_objectives": current_content_obj["objectives"],
            "itzone_simulator_link": f"https://{current_content_obj['itzone']}"
        })

        quiz_questions.append({
            "id": f"q_{idx+1}",
            "course": course_name,
            "question": f"What is the first fundamental concept introduced in Week {payload.week_number} for {course_name}?",
            "options": [
                f"Understanding introductory rules & context of '{course_name}'",
                f"Deleting key files of '{course_name}'",
                f"Skipping preprocessing in '{course_name}'",
                f"Disabling system checks of '{course_name}'"
            ],
            "correct_index": 0
        })

    daily_breakdown = [
        "Day 1-2: Review Lecture Slides & ITZone Content.",
        "Day 3-4: Deep dive into theory concepts and practice introductory problems.",
        "Day 5-6: Solve past exam questions and practical problem sets.",
        "Day 7: Revision & preparation for Weekly Quiz Assessment."
    ]

    return {
        "week_number": payload.week_number,
        "title": f"EduPulse AI Week {payload.week_number} Study Copilot",
        "plan_details": plan_details,
        "daily_tasks": daily_breakdown,
        "quiz_questions": quiz_questions
    }

@app.api_route("/students/evaluate-quiz", methods=["POST", "GET"])
def evaluate_quiz(payload: Optional[QuizEvaluateRequest] = None):
    if payload is None:
        return {"status": "Endpoint Active"}

    total_questions = len(payload.answers)
    if total_questions == 0:
        return {"passed": False, "score": 0}

    correct_count = sum(1 for q_id, ans in payload.answers.items() if ans == 0)
    score_percentage = round((correct_count / total_questions) * 100, 1)
    passed = score_percentage >= 85.0

    weak_areas = []
    if not passed:
        weak_areas.append({
            "topic": "Fundamental Concept Retention",
            "reason": "Lower scores indicate gaps in understanding initial definitions/setups.",
            "recommendation": "Review ITZonePlus introductory chapters and solve practice exercises again."
        })

    return {
        "score_percentage": score_percentage,
        "required_pass_score": 85.0,
        "passed": passed,
        "unlocked_next_week": payload.week_number + 1 if passed else payload.week_number,
        "status_message": "Congratulations! Passed & Unlocked Next Week! 🎉" if passed else "Score is below 85%. Review weak spots before retry.",
        "weak_areas": weak_areas
    }

@app.api_route("/students/evaluate-final-exam", methods=["POST", "GET"])
def evaluate_final_exam(payload: Optional[FinalExamEvaluateRequest] = None):
    if payload is None:
        return {"status": "Endpoint Active"}

    total_q = len(payload.answers)
    if total_q == 0:
        return {"final_score": 0, "message": "No answers submitted!"}

    correct_count = sum(1 for q_id, ans in payload.answers.items() if ans == 0)
    score_percentage = round((correct_count / total_q) * 100, 1)

    return {
        "final_score": score_percentage,
        "message": f"Congratulations! You completed the Comprehensive Semester Exam with {score_percentage}%.",
        "analysis": f"Comprehensive exam covered {len(payload.enrolled_courses_names)} courses."
    }