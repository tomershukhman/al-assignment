from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
from typing import Optional, List
from sqlmodel import Session, select
from .ocr import extract_text_from_image
from .llm import analyze_submission
from .database import get_session
from .models import Problem, Topic, Submission
import os
from pathlib import Path

app = FastAPI(title="Math Solving Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Math Solving Assistant Backend"}

@app.get("/api/topics")
def get_topics(session: Session = Depends(get_session)):
    """Get all available math topics"""
    statement = select(Topic)
    topics = session.exec(statement).all()
    return topics

@app.get("/api/topics/{topic_id}/problems")
def get_topic_problems(topic_id: str, session: Session = Depends(get_session)):
    """Get all problems for a specific topic"""
    # Verify topic exists
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    
    statement = select(Problem).where(Problem.topic_id == topic_id)
    problems = session.exec(statement).all()
    return problems

@app.get("/api/problems/{problem_id}")
def get_problem(problem_id: str, session: Session = Depends(get_session)):
    """Get details of a specific problem"""
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
    return problem

@app.get("/api/submissions")
def get_submissions(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """Get submission history, latest first"""
    statement = select(Submission).order_by(Submission.created_at.desc()).offset(offset).limit(limit)
    submissions = session.exec(statement).all()
    return submissions

@app.get("/api/submissions/{submission_id}")
def get_submission(submission_id: int, session: Session = Depends(get_session)):
    """Get details of a specific submission"""
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found")
    return submission


@app.post("/api/submissions")
async def process_submission(
    file: UploadFile = File(...),
    problem_id: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    correct_answer: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """
    Full processing pipeline:
    1. Receive Image
    2. OCR Processing
    3. LLM Feedback
    4. Return Feedback
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validation: We need question context either from DB (via problem_id) or direct input
    if not question or not correct_answer:
        # Implement DB lookup using problem_id if context not provided
        if not problem_id:
             raise HTTPException(status_code=400, detail="Must provide question and correct_answer (or problem_id)")
        
        # Fetch problem from database
        statement = select(Problem).where(Problem.id == problem_id)
        problem = session.exec(statement).first()
        
        if not problem:
            raise HTTPException(status_code=404, detail=f"Problem with id '{problem_id}' not found")
        
        # Use problem data from DB
        question = problem.question
        correct_answer = problem.correct_answer
    
    try:
        # 1. Read and Process Image (OCR)
        content = await file.read()
        ocr_result = await extract_text_from_image(content)
        
        extracted_text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0) # Mathpix might return this differently, checking docs or response is needed
        
        if not extracted_text:
             raise HTTPException(status_code=400, detail="Could not extract text from image")

        # 2. LLM Analysis
        # Use provided context or fetched from DB
        feedback = await analyze_submission(extracted_text, question, correct_answer)
        
        # 3. Return Logic (No saving for this specific pass as per request)
        return {
            "ocr_text": extracted_text,
            "feedback": feedback
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)