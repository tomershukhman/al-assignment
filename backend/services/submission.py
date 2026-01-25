import uuid
import json
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select
from loguru import logger
from ..config import settings
from ..models import Submission, Problem
from .ocr import extract_text_from_image
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
            
        # 2. OCR Processing
        ocr_result = await extract_text_from_image(content)
        extracted_text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0.0)
        
        # 3. Confidence Check
        if not extracted_text or confidence < settings.OCR_CONFIDENCE_THRESHOLD:
             raise HTTPException(
                 status_code=400, 
                 detail="Could not read handwriting (low confidence). Please upload a new image."
             )

        # 4. LLM Analysis
        feedback = await analyze_submission(extracted_text, question, correct_answer)
        
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
        
        return {
            "ocr_text": extracted_text,
            "feedback": feedback,
            "imagePath": f"{settings.UPLOAD_URL_PREFIX}/{filename}"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
