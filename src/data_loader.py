import csv
import os
import kagglehub

def load_students() -> list:
    path = kagglehub.dataset_download(
        "lainguyn123/student-performance-factors"
    )

    csv_path = os.path.join(path, "StudentPerformanceFactors.csv")

    students = []

    with open(csv_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            students.append(row)

    return students