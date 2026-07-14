def average_score(student: dict) -> float:
    """
    Calculate the average of Previous Score and Exam Score.
    """

    previous_score = float(student["Previous_Scores"])
    exam_score = float(student["Exam_Score"])

    return (previous_score + exam_score) / 2


def attendance_rate(student: dict) -> float:
    """
    Return the student's attendance percentage.
    """

    return float(student["Attendance"])


def study_efficiency(student: dict) -> float:
    """
    Calculate exam score per study hour.
    """

    hours = float(student["Hours_Studied"])
    exam_score = float(student["Exam_Score"])

    if hours == 0:
        return 0.0

    return exam_score / hours