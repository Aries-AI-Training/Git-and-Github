from fastapi import FastAPI

app = FastAPI()

students_db = {
    1: {"name": "Layan", "major": "AI & Data Science", "gpa": 3.2},
    2: {"name": "Lugain", "major": "Computer Information system", "gpa": 3.2}
}

@app.get("/")
def home():
    return {"message": "Welcome to Student API!"}

@app.get("/student/{student_id}")
def get_student(student_id: int):
    if student_id in students_db:
        return students_db[student_id]
    
    return {"error": "Student not found"}