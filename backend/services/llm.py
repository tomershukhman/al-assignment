import json
import base64
from anthropic import AsyncAnthropic
from ..config import settings
from loguru import logger

def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

async def analyze_submission(image_bytes: bytes, media_type: str, question: str, correct_answer: str) -> dict:
    """
    Sends the image bytes and problem context to Claude to get pedagogical feedback.
    Claude performs both OCR and analysis in a single step.
    """
    logger.info(f"Starting LLM analysis on image of size {len(image_bytes)} bytes")

    system_prompt = (
        "You are a helpful math tutor. You will be provided with an image of student work. "
        "Your goal is to:\n"
        "1. Read the handwritten math and text from the image.\n"
        "2. Analyze the student's work steps to identify errors in reasoning.\n"
        "3. Provide structured feedback.\n"
        "4. Assess your confidence in reading the handwriting.\n\n"
        "Your feedback should be encouraging and address the student directly (e.g., 'You did this...'). "
        "Do not refer to 'the student' in the third person."
    )

    image_base64 = encode_image(image_bytes)

    user_message_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_base64
            }
        },
        {
            "type": "text",
            "text": f"""
Analyze the student submission in the image for the problem: "{question}".
The correct answer is: "{correct_answer}".

Return a JSON object with:
- is_relevant: boolean (true if the submission appears to be an attempt to solve the given problem, false if it is unrelated content like a grocery list, drawing, or different problem)
- is_correct: boolean (false if is_relevant is false)
- confidence: number (0.0 to 1.0, indicating how confident you are that you correctly read the text and math in the image. Low confidence suggests illegible handwriting or poor image quality.)
- extracted_text: string (The text and math you read from the image. Use LaTeX for math expressions.)
- analysis: string (brief explanation of their method, addressing the student correctly as 'You'. If not relevant, explain why.)
- feedback: list of steps, where each step has:
    - step: description of the step (addressing the student correctly as 'You')
    - status: 'correct' or 'incorrect'
    - comment: optional string (brief specific comment explaining exactly what was wrong or right in this step, e.g. "Sign error here", "Good job isolating x").
"""
        }
    ]

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    logger.debug("Sending multimodal request to Anthropic API via SDK")

    try:
        message = await client.beta.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2000,
            betas=["structured-outputs-2025-11-13"],
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message_content}
            ],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "is_relevant": {"type": "boolean"},
                        "is_correct": {"type": "boolean"},
                        "confidence": {"type": "number"},
                        "extracted_text": {"type": "string"},
                        "analysis": {"type": "string"},
                        "feedback": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "string"},
                                    "status": {"type": "string", "enum": ["correct", "incorrect"]},
                                    "comment": {"type": "string"}
                                },
                                "required": ["step", "status"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["is_relevant", "is_correct", "confidence", "extracted_text", "analysis", "feedback"],
                    "additionalProperties": False
                }
            }
        )
        
        logger.info("Received response from Anthropic")

        # Extract text content from the response
        content_text = message.content[0].text
        
        result = json.loads(content_text)
        logger.success("Successfully parsed LLM feedback")
        logger.info(f"text confidence: {result['confidence']}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response JSON: {e}")
        if 'content_text' in locals():
            logger.debug(f"Raw response text: {content_text}")
            
        return {
            "is_relevant": False,
            "is_correct": False,
            "confidence": 0.0,
            "extracted_text": "",
            "analysis": "Error parsing AI response",
            "feedback": [
                {"step": "Error processing feedback", "status": "incorrect"}
            ]
        }
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        raise e
