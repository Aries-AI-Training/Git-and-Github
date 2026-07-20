from pydantic import BaseModel, Field, model_validator
from typing import List

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)
    study_hours: float = Field(..., ge=0)
    attendance_rate: float = Field(..., ge=0, le=100)
    quiz_scores: List[float] = Field(...)
    projects_submitted: int = Field(..., ge=0)
    watched_lessons: int = Field(..., ge=0)
    total_lessons: int = Field(..., gt=0)
    days_inactive: int = Field(..., ge=0)
    support_messages: int = Field(..., ge=0)
    Previous_Scores: float = Field(..., ge=0, le=100)
    Exam_Score: float = Field(..., ge=0, le=100)
    Attendance: float = Field(..., ge=0, le=100)
    Hours_Studied: float = Field(..., ge=0)
#Pydantic model validators to ensure data integrity and constraints
    @model_validator(mode='after')
    def check_lessons(self) -> 'StudentCreate':
        if self.watched_lessons > self.total_lessons:
            raise ValueError('Watched lessons cannot exceed total lessons')
        
        for score in self.quiz_scores:
            if not (0 <= score <= 100):
                raise ValueError('Quiz scores must be between 0 and 100')
                
        return self