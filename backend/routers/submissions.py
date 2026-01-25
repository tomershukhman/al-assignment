from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
from sqlalchemy.orm import selectinload
from ..database import get_session
from ..models import Submission
from ..response_models import SubmissionWithProblem
from ..services.submission import process_new_submission

router = APIRouter(tags=["submissions"])

@router.get("/api/submissions", response_model=List[SubmissionWithProblem])
def get_submissions(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    Get submission history, latest first, with problem details.
    Optimized to fetch related 'problem' data efficiently.
    """
    statement = (
        select(Submission)
        .options(selectinload(Submission.problem))
        .order_by(Submission.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    submissions = session.exec(statement).all()
    return submissions

@router.get("/api/submissions/{submission_id}", response_model=SubmissionWithProblem)
def get_submission(submission_id: int, session: Session = Depends(get_session)):
    """Get details of a specific submission"""
    statement = (
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.problem))
    )
    submission = session.exec(statement).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found")
    
    return submission

@router.post("/api/submissions")
async def process_submission(
    file: UploadFile = File(...),
    problem_id: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    correct_answer: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """
    Process a new student submission.
    Delegates logic to the submission service.
    """
    return await process_new_submission(
        file=file,
        problem_id=problem_id,
        question=question,
        correct_answer=correct_answer,
        session=session
    )
