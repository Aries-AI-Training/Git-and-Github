import numpy as np 
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


total_attendance = 0
total_quiz_scores = 0
best_student = None
highest_score = -1

risk_counts = {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0}

print("Student Details")
for student in students:
    avg_quiz = average_quiz_score(student)
    completion = lesson_completion(student)
    risk = student_risk_level(student)
    
    print(f"Name: {student['name']} | Avg Quiz: {avg_quiz:.2f} | Completion: {completion:.2f}% | Risk: {risk}")
    
    total_attendance += student["attendance_rate"]
    total_quiz_scores += avg_quiz
    
    risk_counts[risk] += 1
    
    #best student
    if avg_quiz > highest_score:
        highest_score = avg_quiz
        best_student = student["name"]

print("\n" + "="*40 + "\n")

#هون بحسب المعادلات 
num_students = len(students)
avg_academy_attendance = total_attendance / num_students
avg_academy_quiz = total_quiz_scores / num_students

print(f"🔹 Average Attendance across Academy: {avg_academy_attendance:.2f}%")
print(f"🔹 Average Quiz Score across Academy: {avg_academy_quiz:.2f}")
print(f"🔹 Best Performing Student: {best_student} (Score: {highest_score:.2f})")
print(f"🔹 Students per Risk Level: {risk_counts}")








matrix_data = []
for student in students:
    matrix_data.append([
        student["study_hours"],
        student["attendance_rate"],
        average_quiz_score(student),
        lesson_completion(student),
        student["days_inactive"]
    ])

ai_matrix = np.array(matrix_data)

# Slicing
print("1. First three students (Rows 0, 1, 2):\n", ai_matrix[:3])
print("\n2. Only the attendance column (Column index 1):\n", ai_matrix[:, 1])
print("\n3. Only the quiz score column (Column index 2):\n", ai_matrix[:, 2])
print("\n4. Performance columns (Attendance, Quiz, Completion - Columns 1, 2, 3):\n", ai_matrix[:, 1:4])

import os
import matplotlib.pyplot as plt

if not os.path.exists("charts"):
    os.makedirs("charts")

names = [s["name"] for s in students]
quiz_averages = [average_quiz_score(s) for s in students]

plt.figure(figsize=(8, 5))
plt.bar(names, quiz_averages, color='skyblue', edgecolor='black')
plt.title('Average Quiz Score per Student')
plt.xlabel('Students')
plt.ylabel('Average Score')
plt.axhline(y=60, color='red', linestyle='--', label='Passing Mark (60)') 
plt.legend()
plt.savefig('charts/quiz_scores.png') 
plt.close()


levels = list(risk_counts.keys())
counts = list(risk_counts.values())

plt.figure(figsize=(6, 4))
plt.bar(levels, counts, color=['salmon', 'orange', 'lightgreen'], edgecolor='black')
plt.title('Number of Students per Risk Level')
plt.xlabel('Risk Level')
plt.ylabel('Number of Students')
plt.savefig('charts/risk_levels.png') 
plt.close()

