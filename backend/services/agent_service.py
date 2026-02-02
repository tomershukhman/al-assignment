"""
Agent service for processing chat messages.
Handles file persistence and passes 'current_image_path' to the agent state.
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import json
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
        
        # Helper: Map tool_call_id to args from AIMessages
        tool_args_map = {}
        for msg in final_messages:
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
                for tool_call in msg.tool_calls:
                    if 'id' in tool_call:
                        tool_args_map[tool_call['id']] = tool_call.get('args', {})

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
                args = {}
                if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                    args = tool_args_map.get(msg.tool_call_id, {})
                
                result_content = msg.content
                # Try to parse JSON content if it's a string
                if isinstance(result_content, str):
                    try:
                        result_content = json.loads(result_content)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON

                tool_results.append({
                    "name": msg.name or "unknown",
                    "args": args,
                    "result": result_content
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


    return formatted_messages


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


async def retrieve_chat_history(thread_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve the full chat history for a thread, formatted for the frontend.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = await math_tutor_agent.aget_state(config)
    
    if not state_snapshot.values:
        logger.warning(f"No state found for thread {thread_id}")
        return []
    
    messages = state_snapshot.values.get("messages", [])
    return _group_messages_by_turn(messages)


def _group_messages_by_turn(messages: List[Any]) -> List[Dict[str, Any]]:
    """
    Group raw LangChain messages into User/Assistant turns for the frontend.
    Collapses ToolMessages into the associated Assistant message.
    """
    history = []
    
    # Track tool outputs to attach to the next AI message
    # Or, more accurately: 
    # AI (calls tool) -> Tool (result) -> AI (interprets result)
    # The frontend expects the "Assistant" message to contain the tool results.
    # We'll buffer tool results and attach them to the AI message that generated the calls (or the one following?)
    # Usually: User -> [AI -> Tool -> AI] (Assistant Turn)
    
    current_turn = None
    pending_tool_results = []
    
    msg_map = {msg.id: msg for msg in messages if hasattr(msg, 'id') and msg.id}
    
    for i, msg in enumerate(messages):
        # SKIP System messages
        if msg.type == 'system':
            continue
            
        if isinstance(msg, HumanMessage):
            # If we were building an assistant turn, push it
            if current_turn:
                if pending_tool_results:
                    current_turn["toolResults"] = pending_tool_results
                    pending_tool_results = []
                history.append(current_turn)
                current_turn = None
                
            # Create User turn
            # Extract image if present (multimodal content)
            image_url = None
            text_content = ""
            if isinstance(msg.content, list):
                for block in msg.content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            bg_text = block.get("text", "")
                            # Filter out system breadcrumbs
                            if not bg_text.strip().startswith("[SYSTEM:"):
                                text_content += bg_text
                        # elif block.get("type") == "image_url": ... (if we stored URLs)
                    else:
                        text_content += str(block)
            else:
                text_content = str(msg.content)

            history.append({
                "id": str(i) if not msg.id else msg.id,
                "role": "user",
                "content": text_content,
                # "imageUrl": ... (Need a way to recover this if we want full fidelity, 
                # but 'current_image_path' is transient in state.
                # For now, just show text)
            })
            
        elif isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                # Flatten text content
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = "\n".join(text_parts)
            
            # If this AI message HAS tool_calls, it's an intermediate step.
            # But we might want to show it if it has text.
            # If it has NO text but ONLY tool_calls, it's just a "Thinking..." step effectively.
            # The Final Answer usually comes in a separate AIMessage after the ToolMessage.
            
            # If we don't have a current assistant turn, start one
            if not current_turn:
                current_turn = {
                    "id": str(i) if not msg.id else msg.id,
                    "role": "assistant",
                    "content": content or "", # Might be empty if just tool call
                    "toolResults": []
                }
            else:
                # We already have an assistant turn (maybe we are merging multiple AI chunks?)
                # Or this is the "Final Answer" after a tool call.
                # Let's simple append content if it exists
                if content:
                    current_turn["content"] += content
            
            # If this message initiated tool calls, we don't have results yet.
            # The results will come in the next messages (ToolMessage).
            
        elif isinstance(msg, ToolMessage):
             # This is a result using 'tool_call_id'
             # Find the call args from the previous AIMessage(s)
             # This is a bit tricky with linear scan.
             # We'll just extract the result and meaningful name.
             
             tool_name = msg.name or "tool"
             
             # Try to find args from the message that called it
             args = {}
             # Look back for the AIMessage with matching tool_call_id
             # (Simple lookback optimization: usually the message just before or a few back)
             found_call = False
             for prev_msg in reversed(messages[:i]):
                 if isinstance(prev_msg, AIMessage) and hasattr(prev_msg, 'tool_calls'):
                     for tc in prev_msg.tool_calls:
                         if tc.get('id') == msg.tool_call_id:
                             args = tc.get('args', {})
                             tool_name = tc.get('name', tool_name)
                             found_call = True
                             break
                 if found_call: 
                     break
             
             try:
                 result_data = json.loads(msg.content)
             except:
                 result_data = msg.content
                 
             pending_tool_results.append({
                 "name": tool_name,
                 "args": args,
                 "result": result_data
             })
             
             # Attach to current turn immediately if it exists
             if current_turn:
                 current_turn.setdefault("toolResults", []).extend(pending_tool_results)
                 pending_tool_results = []
                 
    # Append final turn if exists
    if current_turn:
        if pending_tool_results:
             current_turn.setdefault("toolResults", []).extend(pending_tool_results)
        history.append(current_turn)
        
    return history
