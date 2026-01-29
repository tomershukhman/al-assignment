import uuid
import json
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select
from loguru import logger
from ..config import settings
from ..models import Submission, Problem
from .llm import analyze_submission

async def process_new_submission(
    file: UploadFile,
    problem_id: str | None,
    question: str | None,
    correct_answer: str | None,
    session: Session
) -> dict:
    """
    Orchestrates the submission pipeline:
    1. Validation
    2. File Saving
    3. OCR
    4. LLM Analysis
    5. Database Persistence
    """
    
    # 0. Basic Validation
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Resolve problem context
    if not question or not correct_answer:
        if not problem_id:
             raise HTTPException(status_code=400, detail="Must provide question and correct_answer (or problem_id)")
        
        problem = session.get(Problem, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail=f"Problem with id '{problem_id}' not found")
        
        question = problem.question
        correct_answer = problem.correct_answer

    try:
        # 1. Save Image
        settings.UPLOADS_DIR.mkdir(exist_ok=True)
        
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = settings.UPLOADS_DIR / filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        # 2. LLM Analysis (includes "OCR")
        # We pass the image bytes directly to the LLM
        feedback = await analyze_submission(content, file.content_type, question, correct_answer)
        
        extracted_text = feedback.get("extracted_text", "")
        # Confidence is not explicitly returned by the LLM in the same way as Mathpix,
        # but we can assume high confidence if is_relevant is True.
        # We'll set a placeholder or use a check from the LLM result if we added one.
        # For now, let's assume if it returned a result, it works.
        confidence = feedback.get("confidence", 0.0)
        
        # 5. Save to DB
        submission = Submission(
            problem_id=problem_id,
            image_path=f"{settings.UPLOAD_URL_PREFIX}/{filename}",
            ocr_text=extracted_text,
            ocr_confidence=confidence,
            student_result="See Feedback",
            is_correct=feedback.get("is_correct", False),
            feedback_json=json.dumps(feedback)
        )
        
        session.add(submission)
        session.commit()
        session.refresh(submission)
        
        if confidence < settings.OCR_CONFIDENCE_THRESHOLD:
            raise HTTPException(
                status_code=400,
                detail="OCR confidence is too low. Please try again."
            )

        return {
            "ocr_text": extracted_text,
            "feedback": feedback,
            "imagePath": f"{settings.UPLOAD_URL_PREFIX}/{filename}"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while processing your submission. Please try again later."
        )
