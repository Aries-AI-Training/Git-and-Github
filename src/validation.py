MIN_SCORE = 0.0
MAX_SCORE = 100.0
MIN_HOURS = 0
MIN_ATTENDANCE = 0.0
MAX_ATTENDANCE = 100.0

valid_motivation_levels = {"Low", "Medium", "High"}  

required_fields = [
    "Hours_Studied",
    "Attendance",
    "Sleep_Hours",
    "Previous_Scores",
    "Exam_Score",
    "Motivation_Level"
]

def validate_student(student: dict) -> tuple[bool, str]:
    try:

        for field in required_fields:
            if not student[field].strip():
                return False, f"{field} is missing"
#type casting  
        hours = int(student["Hours_Studied"])
        attendance = float(student["Attendance"])
        sleep = int(student["Sleep_Hours"])
        previous_score = float(student["Previous_Scores"])
        exam_score = float(student["Exam_Score"])
        motivation = student["Motivation_Level"].strip()

        if hours <= MIN_HOURS:
            return False, f"Hours studied must be greater than {MIN_HOURS}"

        if attendance < MIN_ATTENDANCE or attendance > MAX_ATTENDANCE:
            return False, f"Attendance must be between {MIN_ATTENDANCE} and {MAX_ATTENDANCE}"

        if sleep <= MIN_HOURS:  
            return False, f"Sleep hours must be greater than {MIN_HOURS}"

        if previous_score < MIN_SCORE or previous_score > MAX_SCORE:
            return False, f"Previous score must be between {MIN_SCORE} and {MAX_SCORE}"

        if exam_score < MIN_SCORE or exam_score > MAX_SCORE:
            return False, f"Exam score must be between {MIN_SCORE} and {MAX_SCORE}"

        if motivation not in valid_motivation_levels:
            return False, "Invalid motivation level"

        return True, "Valid"

    except (ValueError, KeyError):
        return False, "Invalid student record"