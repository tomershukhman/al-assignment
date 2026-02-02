"""
Chat router for conversational math tutoring with the LangGraph agent.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
import json
from loguru import logger

from ..services.agent_service import process_chat_message, format_conversation_for_storage, retrieve_chat_history
from ..response_models import ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(..., description="User's text message"),
    image: Optional[UploadFile] = File(None, description="Optional image upload"),
    thread_id: Optional[str] = Form(None, description="Session ID for stateful conversation"),
    # conversation_history is deprecated but kept for backward compatibility/logging if needed, 
    # though we won't use it for agent state anymore.
    conversation_history: Optional[str] = Form(None, description="Deprecated: History is now managed on server")
):
    """
    Send a message to the math tutoring agent.
    
    The agent can:
    - Extract problems from uploaded images
    - Discuss math concepts and problems
    - Analyze submitted solutions with detailed feedback
    
    Args:
        message: The user's text message
        image: Optional image file (problem or solution)
        thread_id: UUID for the conversation session (optional, returned in response)
        
    Returns:
        ChatResponse with agent's response, any tool results, updated conversation, and thread_id
    """
    logger.info(f"Chat request received: {message[:50]}... (Thread: {thread_id})")
    
    try:
        # Process image if uploaded
        image_data = None
        image_media_type = None
        
        if image:
            # Validate image
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file must be an image"
                )
            
            image_data = await image.read()
            image_media_type = image.content_type
            logger.info(f"Image uploaded: {len(image_data)} bytes, type: {image_media_type}")
        
        # Process through agent with thread_id
        result = await process_chat_message(
            message=message,
            image_data=image_data,
            image_media_type=image_media_type,
            thread_id=thread_id
        )
        
        # Format conversation for response
        formatted_conversation = format_conversation_for_storage(result.get("conversation", []))
        new_thread_id = result.get("thread_id")
        
        # --- FIX START: Handle Structured Content ---
        # The agent might return a list of content blocks (text + tool_use)
        # We need to ensure 'final_response_text' is strictly a string for Pydantic.
        
        raw_response = result["response"]
        final_response_text = ""

        if isinstance(raw_response, str):
            final_response_text = raw_response
        elif isinstance(raw_response, list):
            # Concatenate all text parts from the list of blocks
            text_parts = []
            for block in raw_response:
                # Handle dictionary blocks like {'type': 'text', 'text': '...'}
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                # Handle raw string blocks
                elif isinstance(block, str):
                    text_parts.append(block)
            final_response_text = "\n".join(text_parts)
        # --- FIX END ---

        logger.success("Chat request processed successfully")
        
        return ChatResponse(
            response=final_response_text,  # Use the cleaned string
            tool_results=result.get("tool_results", []),
            conversation=formatted_conversation,
            thread_id=new_thread_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your message: {str(e)}"
        )


@router.get("/api/chat/history/{thread_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(thread_id: str):
    """
    Retrieve the full chat history for a given thread session.
    """
    try:
        if not thread_id:
            return []
            
        history = await retrieve_chat_history(thread_id)
        return history
    except Exception as e:
        logger.error(f"Failed to retrieve history for {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

