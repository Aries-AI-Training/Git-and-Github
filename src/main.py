import logging
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))  
project_root = os.path.dirname(current_dir)              

# Ensure folders are registered in sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Register 'src' as a module for compatibility
if "src" not in sys.modules:
    import types
    src_module = types.ModuleType("src")
    src_module.__path__ = [current_dir]
    sys.modules["src"] = src_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.routes import router as student_router, root_router

from data_loader import load_students
from validation import validate_student
from metrics import average_score, attendance_rate
from risk import student_risk_level
from report_generator import save_processed_students, save_summary

logs_dir = os.path.join(project_root, "logs")
outputs_dir = os.path.join(project_root, "outputs")

os.makedirs(logs_dir, exist_ok=True)
os.makedirs(outputs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "application.log"), encoding="utf-8"),
        logging.StreamHandler()#بيطبع اللوج لايف على الـ Terminal قدامي وانا شغالة.
    ]
)

app = FastAPI(
    title="Student Intelligence System API",
    description="REST API Upgrade with Backward Compatibility.",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(root_router)

def run_cli_mode():
    logging.info("Application started in CLI mode")

    students = load_students()
    logging.info(f"{len(students)} student records loaded")

    processed_students = []
    valid_students = 0

    total_attendance = 0
    total_average_score = 0

    best_average = -1
    best_student_name = None

    worst_average = 101
    highest_risk_student_name = None

    risk_counts = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}

    for index, student in enumerate(students, start=1):
        valid, message = validate_student(student)

        if not valid:
            logging.warning(f"Student #{index} skipped: {message}")
            continue

        student_name = student.get("name", f"Student_{index}")

        avg_score = average_score(student)
        attendance = attendance_rate(student)
        
        hours = float(student.get("Hours_Studied", 0))
        lesson_completion = min(100.0, (hours / 20.0) * 100.0)
        
        risk = student_risk_level(student)

        processed_students.append({
            "name": student_name,
            "average_quiz_score": round(avg_score, 2),
            "lesson_completion": round(lesson_completion, 2),
            "risk_level": risk
        })

        valid_students += 1
        total_attendance += attendance
        total_average_score += avg_score
        risk_counts[risk] += 1

        if avg_score > best_average:
            best_average = avg_score
            best_student_name = student_name

        if avg_score < worst_average:
            worst_average = avg_score
            highest_risk_student_name = student_name

    if valid_students == 0:
        logging.error("No valid student records found.")
        return

    summary = {
        "total_students": valid_students,
        "best_performing_student": best_student_name,
        "best_average_score": round(best_average, 2),
        "highest_risk_student": highest_risk_student_name,
        "worst_average_score": round(worst_average, 2),
        "average_attendance": round(total_attendance / valid_students, 2),
        "average_score": round(total_average_score / valid_students, 2),
        "students_per_risk_level": risk_counts
    }

    save_processed_students(processed_students, os.path.join(outputs_dir, "processed_students.json"))
    save_summary(summary, os.path.join(outputs_dir, "summary.json"))

    logging.info(f"{valid_students} valid students processed")
    logging.info("JSON reports created successfully")
    logging.info("Application finished successfully")


if __name__ == "__main__":
    # If run directly and no specific command arguments are passed, run CLI mode.
    # Otherwise, it can be run via uvicorn: uvicorn main:app --reload
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    else:
        try:
            run_cli_mode()
        except Exception as error:
            logging.exception(f"Unexpected error in CLI mode: {error}")
