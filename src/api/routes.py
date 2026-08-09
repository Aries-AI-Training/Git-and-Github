import json
import os
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import List
from src.models.student import (
    StudentCreate, StudentLogin, ProfileUpdate, SemesterSetup, 
    TaskCreate, QuizScoreSubmit, EmergencyPlanRequest, ChapterToggle, ExamCreate,
    GpaCourseItem, GpaSaveRequest
)
from src.metrics import average_score, attendance_rate
from src.risk import student_risk_level

# Path to the old project data
def find_data_path():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "../../../data/students.json"),
        os.path.join(os.path.dirname(__file__), "../../data/students.json"),
        os.path.join(os.path.dirname(__file__), "../../../../data/students.json"),
        os.path.abspath("data/students.json")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/students.json"))

DATA_PATH = find_data_path()

# Path to the new EduPulse data
EDUPULSE_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(DATA_PATH), "edupulse_data.json"))

# --- Helper functions for Old Project ---
def load_students_from_file():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_students_to_file(students_data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(students_data, f, indent=4, ensure_ascii=False)

# --- Helper functions for EduPulse AI ---
def load_edupulse_data():
    if not os.path.exists(EDUPULSE_DATA_PATH):
        return {}
    with open(EDUPULSE_DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_edupulse_data(data):
    os.makedirs(os.path.dirname(EDUPULSE_DATA_PATH), exist_ok=True)
    with open(EDUPULSE_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_default_student_record(student_id, name, major, gpa, completed_hours):
    return {
        "profile": {
            "fullName": name,
            "studentId": student_id,
            "university": "Hashemite University",
            "major": major,
            "gpa": str(gpa),
            "completedHours": int(completed_hours),
            "targetGpa": str(round(min(4.0, float(gpa) + 0.2), 2))
        },
        "selectedCourseIds": [],
        "semesterDates": {
            "start": "",
            "firstExam": "",
            "secondExam": ""
        },
        "quizScores": {},
        "tasks": [
            {
                "id": 1,
                "title": "Study Chapter 4 of Data Structures",
                "category": "Academic",
                "priority": "High",
                "completed": False
            },
            {
                "id": 2,
                "title": "Complete backend code for FastAPI Student System",
                "category": "Projects",
                "priority": "High",
                "completed": True
            },
            {
                "id": 3,
                "title": "Read 10 pages of a technical book",
                "category": "Habits",
                "priority": "Medium",
                "completed": False
            }
        ],
        "chapterProgress": {},
        "pomodoroSessions": 0,
        "examEvents": []
    }


router = APIRouter(
    prefix="/students",  
    tags=["Students Profile"]  
)

root_router = APIRouter()

# ==================== OLD PROJECT ENDPOINTS ====================

@router.get("", response_model=List[dict])
def get_all_students():
    students = load_students_from_file()
    processed_students = []
    
    for student in students:
        mapped_student = {
            "Previous_Scores": student.get("previous_scores", student.get("Previous_Scores", 0)),
            "Exam_Score": student.get("exam_score", student.get("Exam_Score", 0)),
            "Attendance": student.get("attendance", student.get("Attendance", 0)),
            "Hours_Studied": student.get("study_hours", student.get("Hours_Studied", 0))
        }
        
        avg_score = average_score(mapped_student)
        att_rate = attendance_rate(mapped_student)
        risk = student_risk_level(mapped_student)
        
        hours = float(mapped_student["Hours_Studied"])
        lesson_completion = min(100.0, (hours / 20.0) * 100.0)
        
        processed_students.append({
            "name": student.get("name"),
            "average_quiz_score": round(avg_score, 2),
            "lesson_completion_percentage": round(lesson_completion, 2),
            "risk_level": risk
        })
        
    return processed_students

@router.get("/summary", response_model=dict)
def get_academy_summary():
    students = load_students_from_file()
    
    if not students:
        return {
            "total_students": 0,
            "average_score": 0.0,
            "average_attendance": 0.0,
            "high_risk_students": 0,
            "students_per_risk_level": {
                "Low Risk": 0,
                "Medium Risk": 0,
                "High Risk": 0
            }
        }
    
    total_students = len(students)
    total_attendance = 0
    total_average_score = 0
    high_risk_students = 0
    risk_counts = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
    
    for student in students:
        mapped_student = {
            "Previous_Scores": student.get("previous_scores", student.get("Previous_Scores", 0)),
            "Exam_Score": student.get("exam_score", student.get("Exam_Score", 0)),
            "Attendance": student.get("attendance", student.get("Attendance", 0)),
            "Hours_Studied": student.get("study_hours", student.get("Hours_Studied", 0))
        }
        
        avg_score = average_score(mapped_student)
        att_rate = attendance_rate(mapped_student)
        risk = student_risk_level(mapped_student)
        
        total_attendance += att_rate
        total_average_score += avg_score
        risk_counts[risk] += 1
        if risk == "High Risk":
            high_risk_students += 1
            
    return {
        "total_students": total_students,
        "average_score": round(total_average_score / total_students, 2),
        "average_attendance": round(total_attendance / total_students, 2),
        "high_risk_students": high_risk_students,
        "students_per_risk_level": risk_counts
    }

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    student_dict = student.dict()
    
    mapped_student = {
        "name": student_dict["name"],
        "Hours_Studied": student_dict["study_hours"],
        "Attendance": student_dict["attendance"],
        "Sleep_Hours": student_dict["sleep_hours"],
        "Previous_Scores": student_dict["previous_scores"],
        "Exam_Score": student_dict["exam_score"],
        "Motivation_Level": student_dict["motivation_level"]
    }
    
    from src.validation import validate_student
    is_valid, error_msg = validate_student(mapped_student)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
        
    students = load_students_from_file()
    students.append(student_dict)
    save_students_to_file(students)
    
    return {"message": "Student created successfully", "student": student_dict}

# ==================== NEW EDUPULSE AI PROJECT ENDPOINTS ====================

@router.post("/edupulse/login", response_model=dict)
def edupulse_login(login_data: StudentLogin):
    data = load_edupulse_data()
    student_id = login_data.studentId
    
    if student_id not in data:
        # Create a new student profile
        data[student_id] = get_default_student_record(
            student_id, login_data.fullName, login_data.major, login_data.gpa, login_data.completedHours
        )
        save_edupulse_data(data)
    else:
        # Optionally update their current basic credentials
        data[student_id]["profile"]["fullName"] = login_data.fullName
        data[student_id]["profile"]["major"] = login_data.major
        data[student_id]["profile"]["gpa"] = str(login_data.gpa)
        data[student_id]["profile"]["completedHours"] = int(login_data.completedHours)
        save_edupulse_data(data)
        
    return {"message": "Login successful", "data": data[student_id]}

@router.get("/edupulse/profile/{student_id}", response_model=dict)
def edupulse_get_profile(student_id: str):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return data[student_id]

@router.put("/edupulse/profile/{student_id}", response_model=dict)
def edupulse_update_profile(student_id: str, profile: ProfileUpdate):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    data[student_id]["profile"] = {
        "fullName": profile.fullName,
        "studentId": student_id,
        "university": "Hashemite University",
        "major": profile.major,
        "gpa": profile.gpa,
        "completedHours": profile.completedHours,
        "targetGpa": profile.targetGpa
    }
    save_edupulse_data(data)
  #  return {"message": "Profile updated successfully", "profile": data[student_id]["profile"]}

@router.post("/edupulse/semester-setup/{student_id}", response_model=dict)
def edupulse_setup_semester(student_id: str, setup: SemesterSetup):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    data[student_id]["semesterDates"] = {
        "start": setup.start,
        "firstExam": setup.firstExam,
        "secondExam": setup.secondExam
    }
    data[student_id]["selectedCourseIds"] = setup.selectedCourseIds
    save_edupulse_data(data)
    return {"message": "Semester setup complete", "data": data[student_id]}

@router.get("/edupulse/tasks/{student_id}", response_model=List[dict])
def edupulse_get_tasks(student_id: str):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return data[student_id].get("tasks", [])

@router.post("/edupulse/tasks/{student_id}", response_model=dict)
def edupulse_add_task(student_id: str, task: TaskCreate):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not logged in")
        
    new_task = {
        "id": int(os.urandom(4).hex(), 16) % 10000000,
        "title": task.title,
        "category": task.category,
        "priority": task.priority,
        "completed": False
    }
    data[student_id]["tasks"].insert(0, new_task)
    save_edupulse_data(data)
    return {"message": "Task added successfully", "task": new_task}

@router.put("/edupulse/tasks/{student_id}/{task_id}", response_model=dict)
def edupulse_toggle_task(student_id: str, task_id: int):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    for task in data[student_id].get("tasks", []):
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            save_edupulse_data(data)
            return {"message": "Task status updated", "task": task}
            
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/edupulse/tasks/{student_id}/{task_id}", response_model=dict)
def edupulse_delete_task(student_id: str, task_id: int):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    original_len = len(data[student_id]["tasks"])
    data[student_id]["tasks"] = [t for t in data[student_id]["tasks"] if t["id"] != task_id]
    
    if len(data[student_id]["tasks"]) == original_len:
        raise HTTPException(status_code=404, detail="Task not found")
        
    save_edupulse_data(data)
    return {"message": "Task deleted successfully"}

@router.post("/edupulse/quiz-score/{student_id}", response_model=dict)
def edupulse_save_quiz_score(student_id: str, quiz_score: QuizScoreSubmit):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if "quizScores" not in data[student_id]:
        data[student_id]["quizScores"] = {}
        
    data[student_id]["quizScores"][str(quiz_score.weekIndex)] = quiz_score.score
    save_edupulse_data(data)
    return {"message": "Score saved successfully", "scores": data[student_id]["quizScores"]}

@router.post("/edupulse/emergency-plan/{student_id}", response_model=dict)
def edupulse_generate_emergency(student_id: str, req: EmergencyPlanRequest):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    available = req.availableHours
    hours_label = f"{available} hours" if available != "5" else "more than 5 hours"
    
    tasks = [
        f"Focus on the main concepts and key topics of your registered courses for {int(available) * 30} minutes.",
        "Practice solving available questions in the (Test Bank) tab for 45 minutes.",
        "Avoid reading fine details and focus on summaries and completed practical solutions.",
        "Do a quick Pomodoro session for each course focusing on weak points, then take enough rest."
    ]
    
    if int(available) <= 2:
        tasks = [
            "Read chapter summaries directly and focus on main headings and key definitions.",
            "Solve quizzes in the test bank for registered courses for 30 minutes to test quick understanding and important patterns.",
            "Make sure to get enough sleep, as staying up and studying at the last minute reduces exam focus."
        ]
        
    plan = {
        "summary": f"Suggested emergency plan based on your situation ({req.reason}) and available time ({hours_label}):",
        "urgentTasks": tasks,
        "advice": "Academic emergencies are normal and happen to everyone! Focus on core material, stay calm, and trust yourself 🤍"
    }
    
    return plan

@router.post("/edupulse/chapters/{student_id}", response_model=dict)
def edupulse_toggle_chapter(student_id: str, chapter: ChapterToggle):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if "chapterProgress" not in data[student_id]:
        data[student_id]["chapterProgress"] = {}
        
    c_id = chapter.courseId
    ch_num = str(chapter.chapterNum)
    
    if c_id not in data[student_id]["chapterProgress"]:
        data[student_id]["chapterProgress"][c_id] = {}
        
    current_status = data[student_id]["chapterProgress"][c_id].get(ch_num, False)
    data[student_id]["chapterProgress"][c_id][ch_num] = not current_status
    
    save_edupulse_data(data)
    return {"message": "Chapter toggled", "progress": data[student_id]["chapterProgress"][c_id]}

@router.delete("/edupulse/chapters/{student_id}/{course_id}", response_model=dict)
def edupulse_reset_chapters(student_id: str, course_id: str):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if "chapterProgress" in data[student_id] and course_id in data[student_id]["chapterProgress"]:
        data[student_id]["chapterProgress"][course_id] = {}
        save_edupulse_data(data)
        
    return {"message": "Chapters reset successfully"}

@router.post("/edupulse/pomodoro/{student_id}", response_model=dict)
def edupulse_pomodoro_complete(student_id: str):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    data[student_id]["pomodoroSessions"] = data[student_id].get("pomodoroSessions", 0) + 1
    save_edupulse_data(data)
    return {"message": "Pomodoro study session registered", "sessions": data[student_id]["pomodoroSessions"]}

def get_course_name_by_id(course_id: str) -> str:
    names = {
        'cs_cpp': 'Introduction to Programming (C++)',
        'cs_ds': 'Data Structures',
        'cs_db': 'Introduction to Databases',
        'cs_java1': 'Object-Oriented Programming 1',
        'cs_networks': 'Computer Networks',
        'cys_cys_principles': 'Cyber Security Principles',
        'aids_prog': 'Introduction to Programming',
        'aids_oop': 'Object Oriented Programming (Java 1)',
        'aids_ds': 'Data Structures',
        'aids_db': 'Introduction to Database Systems',
        'aids_fund_ds': 'Fundamentals of Data Science',
        'aids_fund_ai': 'Fundamentals of Artificial Intelligence',
        'aids_ml': 'Machine Learning',
        'aids_dl': 'Neural Networks & Deep Learning',
    }
    return names.get(course_id, course_id.replace("_", " ").title())

@router.post("/edupulse/exams/{student_id}", response_model=dict)
def edupulse_add_exam(student_id: str, exam: ExamCreate):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    new_exam = {
        "id": int(os.urandom(4).hex(), 16) % 10000000,
        "courseId": exam.courseId,
        "courseName": get_course_name_by_id(exam.courseId),
        "date": exam.date,
        "time": exam.time,
        "location": exam.location
    }
    
    if "examEvents" not in data[student_id]:
        data[student_id]["examEvents"] = []
        
    data[student_id]["examEvents"].append(new_exam)
    save_edupulse_data(data)
    return {"message": "Exam added to calendar", "exam": new_exam}

@router.delete("/edupulse/exams/{student_id}/{exam_id}", response_model=dict)
def edupulse_delete_exam(student_id: str, exam_id: int):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if "examEvents" not in data[student_id]:
        raise HTTPException(status_code=404, detail="No exams found")
        
    original_len = len(data[student_id]["examEvents"])
    data[student_id]["examEvents"] = [e for e in data[student_id]["examEvents"] if e["id"] != exam_id]
    
    if len(data[student_id]["examEvents"]) == original_len:
        raise HTTPException(status_code=404, detail="Exam event not found")
        
    save_edupulse_data(data)
    return {"message": "Exam deleted successfully"}

@router.get("/edupulse/gpa/{student_id}", response_model=dict)
def edupulse_get_gpa_calculator(student_id: str):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return {
        "gpaPrev": data[student_id].get("gpaPrev", data[student_id]["profile"]["gpa"]),
        "hoursPrev": data[student_id].get("hoursPrev", data[student_id]["profile"]["completedHours"]),
        "gpaCourses": data[student_id].get("gpaCourses", [])
    }

@router.post("/edupulse/gpa/{student_id}", response_model=dict)
def edupulse_save_gpa_calculator(student_id: str, req: GpaSaveRequest):
    data = load_edupulse_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    data[student_id]["gpaPrev"] = req.gpaPrev
    data[student_id]["hoursPrev"] = req.hoursPrev
    data[student_id]["gpaCourses"] = [item.dict() for item in req.gpaCourses]
    save_edupulse_data(data)
    
    return {"message": "GPA calculator data saved successfully"}

@root_router.get("/")
def read_root():
    logging.info("Root endpoint accessed via API.")
    return {"message": "Welcome to Student Intelligence API. Go to /docs for Swagger!"}

@root_router.get("/dashboard")
def show_dashboard():
    # Resolves and serves the frontend React dashboard
    routes_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(routes_dir, "../.."))
    
    frontend_path = os.path.join(project_root, "frontend", "features.html")
    if not os.path.exists(frontend_path):
        fallback_path = os.path.join(os.path.dirname(project_root), "edupulse", "features.html")
        if os.path.exists(fallback_path):
            return FileResponse(fallback_path)
        legacy_path = os.path.join(os.path.dirname(project_root), "edupulse", "index.html")
        if os.path.exists(legacy_path):
            return FileResponse(legacy_path)
        return {"error": "features.html not found. Please place features.html in project_root/frontend/"}
    return FileResponse(frontend_path)
