from metrics import average_score, attendance_rate


def student_risk_level(student: dict) -> str:

    average = average_score(student)
    attendance = attendance_rate(student)
    hours = float(student.get("study_hours", 0))

    if average < 60 or attendance < 70 or hours < 5:
        return "High Risk"

    elif average < 75 or attendance < 85 or hours < 10:
        return "Medium Risk"

    else:
        return "Low Risk"