import json
from anthropic import AsyncAnthropic
from ..config import settings
from loguru import logger

CLAUDE_MODEL = "claude-sonnet-4-5"  # As requested by user

async def analyze_submission(ocr_text: str, question: str, correct_answer: str) -> dict:
    """
    Sends the OCR text and problem context to Claude to get pedagogical feedback
    using the Anthropic SDK.
    """
    logger.info("Starting LLM analysis")

    system_prompt = (
        "You are a helpful math tutor. You analyze student work steps, "
        "identify errors in reasoning, and provide structured feedback. "
        "Your feedback should strictly follow a checklist format."
    )

    user_message = f"""
Analyze the following student submission for the problem: "{question}".
The correct answer is: "{correct_answer}".
The student's handwritten work was interpreted as:
"{ocr_text}"

Return a JSON object with:
- is_correct: boolean
- analysis: string (brief explanation of their method)
- feedback: list of steps, where each step has a description and a status (correct/incorrect)
"""

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    logger.debug("Sending request to Anthropic API via SDK")

    try:
        message = await client.beta.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            betas=["structured-outputs-2025-11-13"],
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "is_correct": {"type": "boolean"},
                        "analysis": {"type": "string"},
                        "feedback": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "string"},
                                    "status": {"type": "string", "enum": ["correct", "incorrect"]}
                                },
                                "required": ["step", "status"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["is_correct", "analysis", "feedback"],
                    "additionalProperties": False
                }
            }
        )
        
        logger.info("Received response from Anthropic")

        # Extract text content from the response
        content_text = message.content[0].text
        # logger.debug(f"Raw structured response: {content_text}")
        
        result = json.loads(content_text)
        logger.success("Successfully parsed LLM feedback")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response JSON: {e}")
        # Log the raw text to see what happened
        if 'content_text' in locals():
            logger.debug(f"Raw response text: {content_text}")
            
        return {
            "is_correct": False,
            "analysis": "Error parsing AI response",
            "feedback": [
                {"step": "Error processing feedback", "status": "incorrect"}
            ]
        }
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        raise e
