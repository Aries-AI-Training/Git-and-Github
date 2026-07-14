import logging
import os
import sys

# التأكد من مسار المجلدات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_students
from validation import validate_student
from metrics import average_score, attendance_rate
from risk import student_risk_level
from report_generator import save_processed_students, save_summary

# إنشاء مجلدات المشروع
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(project_root, "logs")
outputs_dir = os.path.join(project_root, "outputs")

os.makedirs(logs_dir, exist_ok=True)
os.makedirs(outputs_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(logs_dir, "application.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    logging.info("Application started")

    students = load_students()
    logging.info(f"{len(students)} student records loaded")

    processed_students = []
    valid_students = 0

    total_attendance = 0
    total_average_score = 0

    # تتبع أفضل وأسوأ طالب
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

        # توليد اسم افتراضي للطالب بما أنه لا يوجد أسماء في كاقل
        student_name = f"Student_{index}"

        avg_score = average_score(student)
        attendance = attendance_rate(student)
        
        # حساب تقريبي لإكمال الدروس بناءً على ساعات الدراسة (مثلاً بحد أقصى 20 ساعة = 100%)
        hours = float(student["Hours_Studied"])
        lesson_completion = min(100.0, (hours / 20.0) * 100.0)
        
        risk = student_risk_level(student)

        # المخرجات مطابقة تماماً للمفاتيح المطلوبة بالتاسك (Name, average_quiz_score, ...)
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

        # تتبع أفضل طالب
        if avg_score > best_average:
            best_average = avg_score
            best_student_name = student_name

        # تتبع أسوأ طالب (الأكثر عرضة للخطر)
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
    try:
        main()
    except Exception as error:
        logging.exception(f"Unexpected error: {error}")