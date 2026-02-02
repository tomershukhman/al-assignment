from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from ..database import get_session
from ..models import Problem, Topic
from ..services import llm
from ..response_models import ProblemInfo
import uuid

router = APIRouter(tags=["problems"])

@router.post("/api/problems/extract", response_model=ProblemInfo)
async def extract_problem(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload an image of a math problem.
    The system will:
    1. Extract the problem text and correct answer using LLM.
    2. Identify or create a relevant Topic.
    3. Save the new Problem to the database.
    4. Return the created Problem.
    """
    
    # Read file content
    content = await file.read()
    
    # Extract info using LLM
    try:
        extraction = await llm.extract_problem_info(content, file.content_type or "image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract problem info: {str(e)}")
    
    # Find or create Topic
    # Simple logic: check if topic name exists (case-insensitiveish), else create.
    # We might want to normalize the topic name from the LLM.
    topic_name = extraction["topic"].strip()
    
    statement = select(Topic).where(Topic.name == topic_name)
    topic = session.exec(statement).first()
    
    if not topic:
        # Create new topic
        # Generate a simple ID from the name or random
        topic_id = topic_name.lower().replace(" ", "-")
        topic = Topic(
            id=topic_id, 
            name=topic_name, 
            description=f"Problems related to {topic_name}",
            grade_level=0 # Default, maybe LLM can guess this too later
        )
        session.add(topic)
        session.commit()
        session.refresh(topic)
        
    # Create Problem
    problem_id = str(uuid.uuid4())
    problem = Problem(
        id=problem_id,
        topic_id=topic.id,
        question=extraction["question"],
        correct_answer=extraction["correct_answer"]
    )
    
    session.add(problem)
    session.commit()
    session.refresh(problem)
    
    return problem
