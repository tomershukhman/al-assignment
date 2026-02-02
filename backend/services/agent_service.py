"""
Agent service for processing chat messages.
Handles file persistence and passes 'current_image_path' to the agent state.
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import base64
import tempfile
import os
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from ..agent.graph import math_tutor_agent


from ..agent.utils import save_temp_image, create_image_message_content

import uuid

async def process_chat_message(
    message: str,
    image_data: Optional[bytes] = None,
    image_media_type: Optional[str] = None,
    thread_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a chat message through the agent with server-side memory.
    
    Args:
        message: The user's message text.
        image_data: Optional raw bytes of an uploaded image.
        image_media_type: Optional MIME type of the image.
        thread_id: Optional UUID for the conversation session. If None, a new one is generated.
        
    Returns:
        Dict containing response, tool_results, conversation (snapshot), and thread_id.
    """
    # Generate thread_id if new session
    if not thread_id:
        thread_id = str(uuid.uuid4())
        logger.info(f"Starting new conversation session: {thread_id}")
    else:
        logger.info(f"Continuing conversation session: {thread_id}")

    logger.info(f"Processing chat message: {message[:100]}...")
    
    # 1. Prepare Initial Messages
    # We only send the *new* message. History is managed by the graph's memory.
    input_messages = []
    
    # 2. Handle New Input (Text + Optional Image)
    current_image_path = None
    
    if image_data and image_media_type:
        try:
            # Save Image & Create Context
            current_image_path = save_temp_image(image_data, image_media_type)
            content_block = create_image_message_content(
                message, image_data, image_media_type, current_image_path
            )
            # Add new user message with multimodal content
            input_messages.append(HumanMessage(content=content_block))
            
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            input_messages.append(HumanMessage(content=message))
    else:
        # Add new text-only user message
        input_messages.append(HumanMessage(content=message))
    
    # 3. Invoke Agent with State & Thread Configuration
    logger.debug("Invoking agent...")
    try:
        # Prepare input payload. 
        # 'messages' key in state will be updated by LangGraph's reducer.
        input_payload = {"messages": input_messages}
        
        if current_image_path:
            input_payload["current_image_path"] = current_image_path

        # Invoke with configuration for thread-level persistence
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 10
        }

        result = await math_tutor_agent.ainvoke(input_payload, config=config)
        
        # 4. Extract Response & Tool Results from Final State
        final_messages = result.get("messages", [])
        assistant_response = None
        tool_results = []
        
        # Iterate backwards to find the last AI message
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                assistant_response = msg.content
                break
        
        if not assistant_response:
             # Fallback if no AI content found (rare)
            assistant_response = "I'm here to help! What would you like to know?"

        # Extract tool results from the conversation
        # We look for ToolMessages
        for msg in final_messages:
             if isinstance(msg, ToolMessage):
                tool_results.append({
                    "name": msg.name or "unknown",
                    "result": msg.content
                })

        logger.success(f"Agent responded. Tool results: {len(tool_results)}")
        
        return {
            "response": assistant_response,
            "tool_results": tool_results,
            "conversation": final_messages, # Full history for frontend display (sync)
            "thread_id": thread_id
        }
        
    except Exception as e:
        logger.error(f"Agent invocation failed: {str(e)}")
        raise e


def format_conversation_for_storage(messages: List[Any]) -> List[Dict[str, Any]]:
    """
    Format LangChain message objects into a JSON-serializable list of dictionaries.
    """
    formatted_messages = []
    for msg in messages:
        role = "unknown"
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        
        # Extract content
        content = msg.content
        
        # Build dict
        message_dict = {
            "role": role,
            "content": content,
        }
        
        # Add extra fields if available
        if hasattr(msg, "tool_call_id"):
            message_dict["tool_call_id"] = msg.tool_call_id
        if hasattr(msg, "name"):
            message_dict["name"] = msg.name
            
        formatted_messages.append(message_dict)
        
    return formatted_messages
