import json


def save_processed_students(students: list, file_path: str) -> None:
    """
    Save processed student records to a JSON file.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=4)


def save_summary(summary: dict, file_path: str) -> None:
    """
    Save project summary to a JSON file.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)