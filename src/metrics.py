def average_quiz_score(student: dict) -> float:
    scores = student.get("quiz_scores", [])
    return sum(scores) / len(scores) if scores else 0.0

def lesson_completion(student: dict) -> float:
    total = int(student.get("total_lessons", 1))
    watched = int(student.get("watched_lessons", 0))
    return (watched / total) * 100