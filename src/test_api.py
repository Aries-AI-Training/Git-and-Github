import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_flow():
    # Test root and dashboard endpoints relocated to root_router in routes.py
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Welcome" in res_root.json()["message"]

    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200

    # 1. Login
    payload = {
        "studentId": "2134567",
        "fullName": "Layan Alkhawaldeh",
        "major": "AIDS",
        "gpa": "3.45",
        "completedHours": 72
    }
    response = client.post("/students/edupulse/login", json=payload)
    print("Login status:", response.status_code)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["profile"]["fullName"] == "Layan Alkhawaldeh"

    # 2. Get profile
    res_profile = client.get("/students/edupulse/profile/2134567")
    assert res_profile.status_code == 200

    # 3. Add task
    task_payload = {
        "title": "Solve Data Structures Quiz",
        "category": "Academic",
        "priority": "High"
    }
    res_task = client.post("/students/edupulse/tasks/2134567", json=task_payload)
    assert res_task.status_code == 200
    task_data = res_task.json()
    assert "task" in task_data
    task_id = task_data["task"]["id"]

    # 4. Toggle task
    res_toggle = client.put(f"/students/edupulse/tasks/2134567/{task_id}")
    assert res_toggle.status_code == 200
    assert res_toggle.json()["task"]["completed"] is True

    # 5. Delete task
    res_del = client.delete(f"/students/edupulse/tasks/2134567/{task_id}")
    assert res_del.status_code == 200

    # 6. Semester setup
    setup_payload = {
        "start": "2026-02-15",
        "firstExam": "2026-03-25",
        "secondExam": "2026-05-10",
        "selectedCourseIds": ["aids_ds", "aids_oop"]
    }
    res_setup = client.post("/students/edupulse/semester-setup/2134567", json=setup_payload)
    assert res_setup.status_code == 200

    # 7. Chapter toggle
    chapter_payload = {
        "courseId": "aids_ds",
        "chapterNum": 1
    }
    res_chapter = client.post("/students/edupulse/chapters/2134567", json=chapter_payload)
    assert res_chapter.status_code == 200

    # 8. Reset chapters
    res_reset = client.delete("/students/edupulse/chapters/2134567/aids_ds")
    assert res_reset.status_code == 200

    # 9. Add Exam
    exam_payload = {
        "courseId": "aids_ds",
        "date": "2026-03-25",
        "time": "10:00",
        "location": "IT Hall 102"
    }
    res_exam = client.post("/students/edupulse/exams/2134567", json=exam_payload)
    assert res_exam.status_code == 200
    exam_id = res_exam.json()["exam"]["id"]

    # 10. Delete Exam
    res_delexam = client.delete(f"/students/edupulse/exams/2134567/{exam_id}")
    assert res_delexam.status_code == 200

    # 11. GPA Calculator GET
    res_gpa_get = client.get("/students/edupulse/gpa/2134567")
    assert res_gpa_get.status_code == 200
    
    # 12. GPA Calculator POST
    gpa_payload = {
        "gpaPrev": "2.95",
        "hoursPrev": 85,
        "gpaCourses": [
            {
                "id": "1",
                "name": "Course 1",
                "credits": 3,
                "grade": "A-",
                "isRepeat": False,
                "prevGrade": ""
            }
        ]
    }
    res_gpa_post = client.post("/students/edupulse/gpa/2134567", json=gpa_payload)
    assert res_gpa_post.status_code == 200

    print("All backend tests completed successfully!")

if __name__ == "__main__":
    test_flow()
