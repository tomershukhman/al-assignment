from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Topic, Problem
from ..response_models import ProblemInfo

router = APIRouter(tags=["topics"])

@router.get("/api/topics")
def get_topics(session: Session = Depends(get_session)):
    """Get all available math topics"""
    statement = select(Topic)
    topics = session.exec(statement).all()
    return topics

@router.get("/api/topics/{topic_id}/problems")
def get_topic_problems(topic_id: str, session: Session = Depends(get_session)):
    """Get all problems for a specific topic"""
    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    
    statement = select(Problem).where(Problem.topic_id == topic_id)
    problems = session.exec(statement).all()
    return problems

@router.get("/api/problems/{problem_id}", response_model=ProblemInfo)
def get_problem(problem_id: str, session: Session = Depends(get_session)):
    """Get details of a specific problem"""
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
    return problem
