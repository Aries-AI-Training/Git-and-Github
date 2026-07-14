from metrics import average_score


def student_risk_level(student: dict) -> str:
    """
    Classify the student's risk level.
    """

    average = average_score(student)
    attendance = float(student["Attendance"])
    hours = float(student["Hours_Studied"])

    if average < 60 or attendance < 70 or hours < 5:
        return "High Risk"

    elif average < 75 or attendance < 85 or hours < 10:
        return "Medium Risk"

    else:
        return "Low Risk"