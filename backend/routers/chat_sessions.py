"""
Router for managing chat sessions (conversations).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from loguru import logger
import uuid

from ..database import get_session
from ..models import ChatSession
from ..response_models import ChatSessionResponse, CreateChatSessionRequest, UpdateChatSessionRequest

router = APIRouter(tags=["chat_sessions"])


@router.get("/api/chat/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(session: Session = Depends(get_session)):
    """
    List all chat sessions, ordered by most recently updated first.
    """
    try:
        statement = select(ChatSession).order_by(ChatSession.updated_at.desc())
        sessions = session.exec(statement).all()
        return sessions
    except Exception as e:
        logger.error(f"Failed to list chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")


@router.post("/api/chat/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    request: CreateChatSessionRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new chat session.
    """
    try:
        # Generate a new UUID for the session
        session_id = str(uuid.uuid4())
        
        # Use provided title or default
        title = request.title if request.title else "New Chat"
        
        new_session = ChatSession(
            id=session_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_session)
        session.commit()
        session.refresh(new_session)
        
        logger.info(f"Created new chat session: {session_id}")
        return new_session
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create chat session")


@router.get("/api/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str, session: Session = Depends(get_session)):
    """
    Get details of a specific chat session.
    """
    try:
        chat_session = session.get(ChatSession, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail=f"Chat session '{session_id}' not found")
        return chat_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat session")


@router.delete("/api/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, session: Session = Depends(get_session)):
    """
    Delete a chat session.
    Note: This only deletes the session metadata. 
    The actual chat messages are stored in LangGraph's memory store.
    """
    try:
        chat_session = session.get(ChatSession, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail=f"Chat session '{session_id}' not found")
        
        session.delete(chat_session)
        session.commit()
        
        logger.info(f"Deleted chat session: {session_id}")
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat session {session_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


@router.patch("/api/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: str,
    request: UpdateChatSessionRequest,
    session: Session = Depends(get_session)
):
    """
    Update a chat session's title.
    """
    try:
        chat_session = session.get(ChatSession, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail=f"Chat session '{session_id}' not found")
        
        if request.title is not None:
            chat_session.title = request.title
            chat_session.updated_at = datetime.utcnow()
        
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        
        logger.info(f"Updated chat session {session_id}: title='{request.title}'")
        return chat_session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update chat session {session_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update chat session")
