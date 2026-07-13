from metrics import average_quiz_score


def student_risk_level(student: dict) -> str:
    average = average_quiz_score(student)

    if (
        average < 60
        or student["attendance_rate"] < 60
        or student["days_inactive"] > 7
    ):
        return "High Risk"

    elif (
        average < 75
        or student["attendance_rate"] < 75
        or 4 <= student["days_inactive"] <= 7
    ):
        return "Medium Risk"

    else:
        return "Low Risk"