import json


def save_processed_students(students: list, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=4)


def save_summary(summary: dict, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)