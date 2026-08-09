from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Old Project Model (Keep intact)
class StudentCreate(BaseModel):
    name: str = Field(..., description="Student name")
    study_hours: float = Field(..., description="Weekly study hours", ge=0)
    attendance: float = Field(..., description="Attendance percentage (0-100)", ge=0, le=100)
    sleep_hours: float = Field(..., description="Average daily sleep hours", ge=0)
    previous_scores: float = Field(..., description="Previous exam scores (0-100)", ge=0, le=100)
    exam_score: float = Field(..., description="Current exam score (0-100)", ge=0, le=100)
    motivation_level: str = Field(..., description="Motivation level: Low, Medium, or High")

# New EduPulse AI Project Models
class StudentLogin(BaseModel):
    studentId: str
    fullName: str
    major: str
    gpa: str
    completedHours: int

class ProfileUpdate(BaseModel):
    fullName: str
    major: str
    gpa: str
    completedHours: int
    targetGpa: str

class SemesterSetup(BaseModel):
    start: str
    firstExam: str
    secondExam: str
    selectedCourseIds: List[str]

class TaskCreate(BaseModel):
    title: str
    category: str
    priority: str

class QuizScoreSubmit(BaseModel):
    weekIndex: int
    score: float

class EmergencyPlanRequest(BaseModel):
    reason: str
    availableHours: str

class ChapterToggle(BaseModel):
    courseId: str
    chapterNum: int

class ExamCreate(BaseModel):
    courseId: str
    date: str
    time: str
    location: str

class GpaCourseItem(BaseModel):
    id: str
    name: str
    credits: int
    grade: str
    isRepeat: bool
    prevGrade: str

class GpaSaveRequest(BaseModel):
    gpaPrev: str
    hoursPrev: int
    gpaCourses: List[GpaCourseItem]
