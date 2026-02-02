from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class ChatSession(SQLModel, table=True):
    """Represents a chat conversation session."""
    id: str = Field(primary_key=True)  # UUID, same as thread_id from LangGraph
    title: str  # Auto-generated from first message or user-edited
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Topic(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    description: str
    grade_level: int
    
    problems: List["Problem"] = Relationship(back_populates="topic")


class Problem(SQLModel, table=True):
    id: str = Field(primary_key=True)
    topic_id: str = Field(foreign_key="topic.id")
    question: str
    correct_answer: str
    
    topic: Topic = Relationship(back_populates="problems")
    submissions: List["Submission"] = Relationship(back_populates="problem")


class Submission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    problem_id: str = Field(foreign_key="problem.id")
    image_path: str
    ocr_text: str
    ocr_confidence: float
    student_result: str
    is_correct: bool
    feedback_json: str  # Storing JSON as string for SQLite simplicity
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    problem: Problem = Relationship(back_populates="submissions")
