def validate_student(student: dict) -> tuple[bool, str]:
    try:

        required_fields = [
            "Hours_Studied",
            "Attendance",
            "Sleep_Hours",
            "Previous_Scores",
            "Exam_Score",
            "Motivation_Level"
        ]

        for field in required_fields:
            if not student[field].strip():
                return False, f"{field} is missing"

        hours = int(student["Hours_Studied"])
        attendance = float(student["Attendance"])
        sleep = int(student["Sleep_Hours"])
        previous_score = float(student["Previous_Scores"])
        exam_score = float(student["Exam_Score"])
        motivation = student["Motivation_Level"].strip()

        if hours <= 0:
            return False, "Hours studied must be greater than zero"

        if attendance < 0 or attendance > 100:
            return False, "Attendance must be between 0 and 100"

        if sleep <= 0:
            return False, "Sleep hours must be greater than zero"

        if previous_score < 0 or previous_score > 100:
            return False, "Previous score must be between 0 and 100"

        if exam_score < 0 or exam_score > 100:
            return False, "Exam score must be between 0 and 100"

        if motivation not in ["Low", "Medium", "High"]:
            return False, "Invalid motivation level"

        return True, "Valid"

    except (ValueError, KeyError, AttributeError):
        return False, "Invalid student record"
