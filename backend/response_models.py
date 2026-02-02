from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any


class ProblemInfo(BaseModel):
    id: str
    topic_id: str
    question: str
    correct_answer: str


class SubmissionWithProblem(BaseModel):
    id: int
    problem_id: str
    image_path: str
    ocr_text: str
    ocr_confidence: float
    student_result: str
    is_correct: bool
    feedback_json: str
    created_at: datetime
    problem: ProblemInfo
    
    class Config:
        from_attributes = True


class ProblemExtraction(BaseModel):
    topic: str
    question: str
    correct_answer: str


class FeedbackStep(BaseModel):
    step: str
    status: Literal["correct", "incorrect"]
    comment: Optional[str] = None


class SubmissionAnalysis(BaseModel):
    is_relevant: bool
    is_correct: bool
    confidence: float
    extracted_text: str
    analysis: str
    feedback: List[FeedbackStep]


class ToolResult(BaseModel):
    """Result from a tool execution"""
    name: str
    result: Any  # Can be dict, str, etc.


class ChatResponse(BaseModel):
    """Response from the chat agent"""
    response: str
    tool_results: List[Dict[str, Any]] = []
    conversation: List[Dict[str, Any]] = []
    thread_id: Optional[str] = None
