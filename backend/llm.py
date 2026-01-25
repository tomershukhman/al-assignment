import json
from anthropic import AsyncAnthropic
from .config import settings
from loguru import logger

CLAUDE_MODEL = "claude-sonnet-4-20250514"  # As specified in DESIGN.md

async def analyze_submission(ocr_text: str, question: str, correct_answer: str) -> dict:
    """
    Sends the OCR text and problem context to Claude to get pedagogical feedback
    using the Anthropic SDK.
    """
    logger.info("Starting LLM analysis")

    system_prompt = (
        "You are a helpful math tutor. You analyze student work steps, "
        "identify errors in reasoning, and provide encouraging feedback. "
        "Do not just give the answer."
    )

    user_message = f"""
Analyze the following student submission for the problem: "{question}".
The correct answer is: "{correct_answer}".
The student's handwritten work was interpreted as:
"{ocr_text}"

Return a JSON object with:
- is_correct: boolean
- analysis: string (brief explanation of their method)
- feedback: string (constructive feedback for the student)
"""

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    logger.debug("Sending request to Anthropic API via SDK")

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        logger.info("Received response from Anthropic")

        # Extract text content from the response
        content_text = message.content[0].text
        
        # Clean up code blocks if present (Claude often wraps JSON in ```json ... ```)
        cleaned_text = content_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
            
        result = json.loads(cleaned_text.strip())
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
            "feedback": "We encountered an error processing the feedback. Please try again."
        }
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        raise e
