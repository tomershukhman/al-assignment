"""
Agent tools for problem extraction and submission analysis.
These tools now work with FILE PATHS instead of raw Base64 data to prevent LLM freezes.
"""

import os
import json
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from pydantic import BaseModel, Field
from loguru import logger

# Import your existing service functions
from ..services.llm import extract_problem_info, analyze_submission, extract_text_from_image

# --- Input Schemas ---

class ExtractProblemInput(BaseModel):
    """Input schema for problem extraction tool."""
    image_path: str = Field(description="The system file path to the uploaded image (e.g. '/tmp/image.png')")
    media_type: str = Field(description="MIME type of the image (e.g., 'image/jpeg', 'image/png')")

class ExtractTextInput(BaseModel):
    """Input schema for text extraction tool."""
    image_path: str = Field(description="The system file path to the uploaded image")
    media_type: str = Field(description="MIME type of the image")

class SubmitSolutionInput(BaseModel):
    """Input schema for solution submission tool."""
    image_path: str = Field(description="The system file path to the student's solution image")
    media_type: str = Field(description="MIME type of the image")
    question: str = Field(description="The problem question text")
    correct_answer: str = Field(description="The correct answer to the problem")

# --- Helper ---

# --- Helper ---

def _load_image_bytes(path: str) -> bytes:
    """Helper to safely load bytes from a file path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found at path: {path}")
    with open(path, "rb") as f:
        return f.read()

def _create_error_command(tool_call_id: str, tool_name: str, error: Exception) -> Command:
    """Helper to create a standardized error Command."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=str(error),
                    tool_call_id=tool_call_id,
                    name=tool_name,
                    status="error"
                )
            ]
        }
    )

# --- Tools ---


@tool(args_schema=ExtractProblemInput)
async def extract_problem_from_image(
    image_path: str,
    media_type: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Extract problem information from an uploaded image file.
    This tool identifies the math topic, extracts the question text, and determines the correct answer.
    """
    logger.info(f"Tool: extract_problem_from_image called with path: {image_path}")
    
    try:
        image_bytes = _load_image_bytes(image_path)
        result = await extract_problem_info(image_bytes, media_type)
        logger.success(f"Problem extracted: {result.get('topic', 'unknown topic')}")
        
        return Command(
            update={
                "current_problem": result,
                "messages": [
                    ToolMessage(
                        content=json.dumps(result),
                        tool_call_id=tool_call_id,
                        name="extract_problem_from_image"
                    )
                ]
            }
        )
    except Exception as e:
        logger.error(f"Problem extraction tool failed: {str(e)}")
        return _create_error_command(tool_call_id, "extract_problem_from_image", e)

@tool(args_schema=ExtractTextInput)
async def extract_text_from_problem_image(
    image_path: str,
    media_type: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Extract raw text from an image file without solving or analyzing it.
    """
    logger.info(f"Tool: extract_text_from_problem_image called with path: {image_path}")
    
    try:
        image_bytes = _load_image_bytes(image_path)
        result = await extract_text_from_image(image_bytes, media_type)
        logger.success(f"Text extracted: {len(result)} characters")
        
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call_id,
                        name="extract_text_from_problem_image"
                    )
                ]
            }
        )
    except Exception as e:
        logger.error(f"Text extraction tool failed: {str(e)}")
        return _create_error_command(tool_call_id, "extract_text_from_problem_image", e)

@tool(args_schema=SubmitSolutionInput)
async def submit_solution(
    image_path: str,
    media_type: str,
    question: str,
    correct_answer: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Analyze a student's submitted solution to a math problem from an image file.
    """
    logger.info(f"Tool: submit_solution called with path: {image_path}")
    
    try:
        image_bytes = _load_image_bytes(image_path)
        result = await analyze_submission(image_bytes, media_type, question, correct_answer)
        logger.success(f"Solution analyzed. Correct: {result.get('is_correct', False)}")
        
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=json.dumps(result),
                        tool_call_id=tool_call_id,
                        name="submit_solution"
                    )
                ]
            }
        )
    except Exception as e:
        logger.error(f"Solution submission tool failed: {str(e)}")
        return _create_error_command(tool_call_id, "submit_solution", e)

# List of all available tools
ALL_TOOLS = [
    extract_problem_from_image,
    extract_text_from_problem_image,
    submit_solution
]