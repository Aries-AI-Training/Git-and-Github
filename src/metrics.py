def average_score(student: dict) -> float:
    quiz_scores = student.get("quiz_scores", [])

    if not quiz_scores:
        return 0.0

    return sum(quiz_scores) / len(quiz_scores)


def attendance_rate(student: dict) -> float:
    attendance = student.get("attendance_rate", 0)

    if attendance <= 1:
        attendance *= 100

    return attendance


def study_efficiency(student: dict) -> float:
    hours = float(student.get("study_hours", 0))

    if hours == 0:
        return 0.0

    return average_score(student) / hours