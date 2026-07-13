import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_students
from validation import validate_student
from metrics import average_quiz_score, lesson_completion
from risk import student_risk_level
from report_generator import save_processed_students, save_summary

os.makedirs("logs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    filename="logs/application.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    logging.info("Application started")
    
    students = load_students("data/students.csv")
    logging.info(f"Loaded {len(students)} records from CSV")

    processed_students = []
    total_attendance = 0
    total_quiz = 0
    
    best_student = ""
    best_score = -1
    
    high_risk_students = []

    risk_counts = {
        "Low Risk": 0,
        "Medium Risk": 0,
        "High Risk": 0
    }

    valid_students = 0

    for student in students:
        valid, message = validate_student(student)

        if not valid:
            student_name = student.get('name', '').strip() or "Unknown/Empty Name"
            logging.warning(f"Student '{student_name}' skipped: {message}")
            continue

        student["age"] = int(student["age"])
        student["study_hours"] = int(student["study_hours"])
        student["attendance_rate"] = float(student["attendance_rate"])

        student["quiz_scores"] = [
            float(student["quiz1"]),
            float(student["quiz2"]),
            float(student["quiz3"])
        ]

        student["projects_submitted"] = int(student["projects_submitted"])
        student["watched_lessons"] = int(student["watched_lessons"])
        student["total_lessons"] = int(student["total_lessons"])
        student["days_inactive"] = int(student["days_inactive"])
        student["support_messages"] = int(student["support_messages"])

        avg_quiz = average_quiz_score(student)
        completion = lesson_completion(student)
        risk = student_risk_level(student)

        processed_students.append({
            "name": student["name"],
            "average_quiz_score": round(avg_quiz, 2),
            "lesson_completion": round(completion, 2),
            "risk_level": risk
        })

        total_attendance += student["attendance_rate"]
        total_quiz += avg_quiz
        risk_counts[risk] += 1

        if avg_quiz > best_score:
            best_score = avg_quiz
            best_student = student["name"]

        if risk == "High Risk":
            high_risk_students.append(student["name"])

        valid_students += 1

    if valid_students == 0:
        logging.error("No valid students found to process.")
        return

    summary = {
        "best_student": best_student,
        "highest_risk_students": high_risk_students,  # صارت لستة احترافية تشمل الكل
        "average_attendance": round(total_attendance / valid_students, 2),
        "average_quiz_score": round(total_quiz / valid_students, 2),
        "students_per_risk_level": risk_counts
    }

    save_processed_students(processed_students, "outputs/processed_students.json")
    save_summary(summary, "outputs/summary.json")

    logging.info(f"{valid_students} valid students successfully processed")
    logging.info("Output JSON files created successfully")
    logging.info("Application finished smoothly")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception(f"Unexpected system crash: {error}")