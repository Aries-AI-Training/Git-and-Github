from data import students
import numpy as np
import matplotlib.pyplot as plt

def average_quiz_score(student):
    return sum(student["quiz_scores"]) / len(student["quiz_scores"])


def lesson_completion(student):
     return (student["watched_lessons"] / student["total_lessons"]) * 100

from data import students

def average_quiz_score(student):
    return sum(student["quiz_scores"]) / len(student["quiz_scores"])


def lesson_completion(student):
    return (student["watched_lessons"] / student["total_lessons"]) * 100


def student_risk_level(student):
    average = average_quiz_score(student)

    if average < 60 or student["attendance_rate"] < 60 or student["days_inactive"] > 7:
        return "High Risk"

    elif average < 75 or student["attendance_rate"] < 75 or 4 <= student["days_inactive"] <= 7:
        return "Medium Risk"

    else:
        return "Low Risk"
    

for student in students:
      print(student["name"])
      print("Average Quiz:", average_quiz_score(student))
      print("Lesson Completion:", lesson_completion(student))
      print("Risk Level:", student_risk_level(student))
      print("----------------")
best_student = None
highest_score = 0
 
print("\nHigh Risk Students:")

for student in students:
    if student_risk_level(student) == "High Risk":
        print(student["name"])

for student in students:
    average = average_quiz_score(student)

    if average > highest_score:
        highest_score = average
        best_student = student["name"]

print("Best Performing Student:", best_student)

total_attendance = 0

for student in students:
    total_attendance += student["attendance_rate"]

average_attendance = total_attendance / len(students)

print("Average Attendance Rate:", average_attendance)

total_quiz = 0

for student in students:
    total_quiz += average_quiz_score(student)

overall_average = total_quiz / len(students)

print("Overall Average Quiz Score:", overall_average)

high = 0
medium = 0
low = 0

for student in students:
    risk = student_risk_level(student)

    if risk == "High Risk":
        high += 1
    elif risk == "Medium Risk":
        medium += 1
    else:
        low += 1

print("\nRisk Level Summary")
print("High Risk:", high)
print("Medium Risk:", medium)
print("Low Risk:", low)

feature_matrix = []

for student in students:
    feature_matrix.append([
        student["study_hours"],
        student["attendance_rate"],
        average_quiz_score(student),
        lesson_completion(student),
        student["days_inactive"]
    ])


feature_matrix = np.array(feature_matrix)

print("\nFeature Matrix")
print(feature_matrix)

print("\nFirst Three Students:")
print(feature_matrix[:3])

print("\nAttendance Column:")
print(feature_matrix[:, 1])

print("\nQuiz Score Column:")
print(feature_matrix[:, 2])

print("\nPerformance Columns:")
print(feature_matrix[:, 1:4])
student_names = []
quiz_averages = []

for student in students:
    student_names.append(student["name"])
    quiz_averages.append(average_quiz_score(student))


plt.figure(figsize=(8,5))

plt.bar(student_names, quiz_averages)

plt.title("Average Quiz Score per Student")
plt.xlabel("Students")
plt.ylabel("Average Quiz Score")

plt.savefig("charts/average_quiz_score.png")

plt.show()