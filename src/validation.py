def validate_student(student: dict) -> tuple[bool, str]:
    try:
        if not student["name"].strip():
            return False, "Name is empty"

        age = int(student["age"])
        attendance = float(student["attendance_rate"])

        quiz_scores = [
            float(student["quiz1"]),
            float(student["quiz2"]),
            float(student["quiz3"])
        ]

        watched = int(student["watched_lessons"])
        total = int(student["total_lessons"])
        days = int(student["days_inactive"])

        if age <= 0:
            return False, "Invalid age"

        if attendance < 0 or attendance > 100:
            return False, "Attendance must be between 0 and 100"

        for score in quiz_scores:
            if score < 0 or score > 100:
                return False, "Quiz score must be between 0 and 100"

        if total <= 0:
            return False, "Total lessons must be greater than zero"

        if watched > total:
            return False, "Watched lessons cannot exceed total lessons"

        if days < 0:
            return False, "Days inactive cannot be negative"

        return True, "Valid"

    except ValueError:
        return False, "Invalid numeric value"