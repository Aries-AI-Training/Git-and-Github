import json
import os
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models.student import StudentCreate
from src.metrics import average_score, attendance_rate
from src.risk import student_risk_level

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../data/students.json")

def load_students_from_file():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_students_to_file(students_data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(students_data, f, indent=4, ensure_ascii=False)


router = APIRouter(
    prefix="/students",  
    tags=["Students Profile"]  
)

#فاضي "" لأنه بياخد الـ Prefix
@router.get("", response_model=List[dict])
def get_all_students():
    students = load_students_from_file()
    
    processed_students = []
    
    for student in students:
        avg_score = average_score(student)
        
        att_rate = attendance_rate(student)
        
        risk = student_risk_level(student)

        hours = float(student.get("study_hours", 0))
        lesson_completion = min(100.0, (hours / 20.0) * 100.0)
        
        processed_students.append({
            "name": student.get("name"),
            "average_quiz_score": round(avg_score, 2),
            "lesson_completion_percentage": round(lesson_completion, 2),
            "risk_level": risk
        })
        
    return processed_students
@router.get("/summary", response_model=dict)
def get_academy_summary():
    students = load_students_from_file()
    
    if not students:
        return {
            "total_students": 0,
            "average_attendance": 0.0,
            "average_quiz_score": 0.0,
            "best_performing_student": None,
            "highest_risk_student": None,
            "risk_distribution": {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0},
            "at_risk_actions": [],
            "inactive_alerts": []
        }
    
    total_students = len(students)
    total_attendance = 0.0
    total_quiz_scores_sum = 0.0
    
    best_student = None
    best_score = -1.0
    
    highest_risk_student = None
    highest_risk_value = -1 
    
    risk_distribution = {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0}
    at_risk_actions = []
    inactive_alerts = []  # ✨ ميزة إضافية للبزنس: مراقبة الطلاب الخاملين
    
    for student in students:
        avg_score = average_score(student)
        att_rate = attendance_rate(student)
        risk = student_risk_level(student)
        days_inactive = student.get("days_inactive", 0)
        
        total_attendance += att_rate
        total_quiz_scores_sum += avg_score
        
        if risk in risk_distribution:
            risk_distribution[risk] += 1
            
        if avg_score > best_score:
            best_score = avg_score
            best_student = student.get("name")
            
        risk_map = {"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}
        current_risk_weight = risk_map.get(risk, 0)
        
        if current_risk_weight > highest_risk_value:
            highest_risk_value = current_risk_weight
            highest_risk_student = student.get("name")
            
        # 🧠 حساب الأكشن والأسباب بناءً على القواعد للطلاب الـ At-Risk
        if risk in ["High Risk", "Medium Risk"]:
            reason = "مستوى علامات منخفض"
            action = "توفير مادة تعليمية إضافية وجلسة دعم مع المدرب."
            
            if att_rate < 75:
                reason = "نسبة حضور ضعيفة جداً"
                action = "التواصل مع الطالب فوراً لمراجعة مشكلة الحضور البارزة."
            elif days_inactive > 5:
                reason = "انقطاع وخمول عن المنصة لعدة أيام"
                action = "إرسال تذكير تلقائي وتعيين مكالمة متابعة هاتفية."
                
            at_risk_actions.append({
                "name": student.get("name"),
                "risk_level": risk,
                "reason": reason,
                "suggested_action": action
            })
            
        if days_inactive >= 7:
            inactive_alerts.append({
                "name": student.get("name"),
                "days_inactive": days_inactive,
                "message": f"الطالب منقطع عن الدراسة منذ {days_inactive} أيام!"
            })
            
    overall_attendance = total_attendance / total_students
    overall_quiz_score = total_quiz_scores_sum / total_students
    
    return {
        "total_students": total_students,
        "average_attendance": round(overall_attendance, 2),
        "average_quiz_score": round(overall_quiz_score, 2),
        "best_performing_student": best_student,
        "highest_risk_student": highest_risk_student,
        "risk_distribution": risk_distribution,
        "at_risk_actions": at_risk_actions,
        "inactive_alerts": inactive_alerts  # رح تظهر بالداشبورد كبونص قوي للبزنس!
    }

@router.get("/{student_name}", response_model=dict)
def get_student_by_name(student_name: str):
    students = load_students_from_file()
    
    #عشان ال cass sensitive 
    for student in students:
        if student.get("name", "").lower() == student_name.lower():
            
            avg_score = average_score(student)
            att_rate = attendance_rate(student)
            risk = student_risk_level(student)
            
            hours = float(student.get("study_hours", 0))
            lesson_completion = min(100.0, (hours / 20.0) * 100.0)
            
            return {
    "name": student.get("name"),
    "age": student.get("age"),
    "study_hours": student.get("study_hours"),
    "attendance_rate": student.get("attendance_rate"),
    "quiz_scores": student.get("quiz_scores"),
    "projects_submitted": student.get("projects_submitted"),
    "watched_lessons": student.get("watched_lessons"),
    "total_lessons": student.get("total_lessons"),
    "days_inactive": student.get("days_inactive"),
    "support_messages": student.get("support_messages"),
    "Previous_Scores": student.get("Previous_Scores"),
    "Exam_Score": student.get("Exam_Score"),
    "Attendance": student.get("Attendance"),
    "Hours_Studied": student.get("Hours_Studied"),

    "average_quiz_score": round(avg_score, 2),
    "lesson_completion_percentage": round(lesson_completion, 2),
    "risk_level": risk
}
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with name '{student_name}' was not found in our system."
    )



@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
def add_new_student(student_in: StudentCreate):

    students = load_students_from_file()
    
    for student in students:
        if student.get("name", "").lower() == student_in.name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with name '{student_in.name}' already exists."
            )
            
    new_student_data = student_in.model_dump()
    
    students.append(new_student_data)
    save_students_to_file(students)
    
    avg_score = average_score(new_student_data)
    risk = student_risk_level(new_student_data)
    
    hours = float(new_student_data.get("study_hours", 0))
    lesson_completion = min(100.0, (hours / 20.0) * 100.0)
    
    return {
        "message": "Student created successfully!",
        "student": {
            "name": new_student_data.get("name"),
            "age": new_student_data.get("age"),
            "average_quiz_score": round(avg_score, 2),
            "lesson_completion_percentage": round(lesson_completion, 2),
            "risk_level": risk,
            "status": "Saved"
        }
    }

@router.get("/{student_name}/risk", response_model=dict)
def get_student_risk(student_name: str):
    students = load_students_from_file()
    
    for student in students:
        if student.get("name", "").lower() == student_name.lower():
            avg_score = average_score(student)
            att_rate = attendance_rate(student)
            risk = student_risk_level(student)
            
            return {
                "name": student.get("name"),
                "risk_level": risk,
                "average_quiz_score": round(avg_score, 2),
                "attendance_rate": att_rate,
                "days_inactive": student.get("days_inactive", 0)
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with name '{student_name}' was not found."
    )




@router.delete("/{student_name}") 
def delete_student(student_name: str):
    students = load_students_from_file()
    
    student_to_delete = None
    for student in students:
        if student.get("name", "").lower() == student_name.lower():
            student_to_delete = student
            break
            
    if not student_to_delete:
        raise HTTPException(status_code=404, detail="Student not found!")
    
    students.remove(student_to_delete)
    
    save_students_to_file(students)
        
    return {"message": f"Student '{student_name}' has been deleted successfully!"}

@router.put("/{student_name}", response_model=dict)
def update_student(student_name: str, student_update: StudentCreate):
    students = load_students_from_file()
    
    student_index = -1
    for index, student in enumerate(students):
        if student.get("name", "").lower() == student_name.lower():
            student_index = index
            break
            
    if student_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Student with name '{student_name}' not found!"
        )
    
    updated_data = student_update.model_dump()
    
    students[student_index] = updated_data
    
    save_students_to_file(students)
    
    avg_score = average_score(updated_data)
    risk = student_risk_level(updated_data)
    
    return {
        "message": f"Student '{student_name}' updated successfully!",
        "student": {
            "name": updated_data.get("name"),
            "age": updated_data.get("age"),
            "average_quiz_score": round(avg_score, 2),
            "risk_level": risk,
            "status": "Updated"
        }
    }

@router.patch("/{student_name}", response_model=dict)
def patch_student(student_name: str, updates: dict): 

    students = load_students_from_file()
    
    student_to_update = None
    for student in students:
        if student.get("name", "").lower() == student_name.lower():
            student_to_update = student
            break
            
    if not student_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Student with name '{student_name}' not found!"
        )
    
    for key, value in updates.items():
        student_to_update[key] = value
        
    save_students_to_file(students)
    
    avg_score = average_score(student_to_update)
    risk = student_risk_level(student_to_update)
    
    return {
        "message": f"Student '{student_name}' updated partially!",
        "student": {
            "name": student_to_update.get("name"),
            "updated_fields": list(updates.keys()), 
            "average_quiz_score": round(avg_score, 2),
            "risk_level": risk
        }
    }