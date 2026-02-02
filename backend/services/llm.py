import base64
from google import genai
from google.genai import types
from ..config import settings
from ..response_models import SubmissionAnalysis, ProblemExtraction
from loguru import logger

# Initialize the Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_submission(image_bytes: bytes, media_type: str, question: str, correct_answer: str) -> dict:
    """
    Sends the image bytes and problem context to Gemini to get pedagogical feedback.
    """
    logger.info(f"Starting LLM analysis on image of size {len(image_bytes)} bytes")

    system_prompt = (
        "You are a helpful math tutor. You will be provided with an image of student work. "
        "Your goal is to:\n"
        "1. Read the handwritten math and text from the image.\n"
        "2. Analyze the student's work steps to identify errors in reasoning.\n"
        "3. Provide structured feedback.\n"
        "4. Assess your confidence in reading the handwriting.\n"
        "5. IMPORTANT: For any math expressions in the extracted text, use LaTeX formatting (e.g., $x^2$).\n\n"
        "Your feedback should be encouraging and address the student directly (e.g., 'You did this...'). "
        "Do not refer to 'the student' in the third person."
    )

    prompt = f"""
    Analyze the student submission in the image for the problem: "{question}".
    The correct answer is: "{correct_answer}".
    """

    logger.debug("Sending multimodal request to Gemini API (New SDK)")

    try:
        # Create the image part
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=media_type
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=SubmissionAnalysis,
            )
        )
        
        logger.info("Received response from Gemini")
        
        # Use .parsed to get the Pydantic-validated object
        if response.parsed:
            result = response.parsed.model_dump()
            logger.success("Successfully parsed LLM feedback")
            logger.info(f"Raw Gemini response: {result}")
            logger.info(f"text confidence: {result['confidence']}")
            logger.info(f"Extracted text length: {len(result.get('extracted_text', ''))}")
            return result
        else:
            logger.error("Gemini response was not parsed as the expected schema")
            raise ValueError("Invalid response format from Gemini")

    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        # Return a fallback error response
        return {
            "is_relevant": False,
            "is_correct": False,
            "confidence": 0.0,
            "extracted_text": "",
            "analysis": f"Message: {str(e)}",
            "feedback": [
                {"step": "Error processing feedback", "status": "incorrect", "comment": str(e)}
            ]
        }


async def extract_problem_info(image_bytes: bytes, media_type: str) -> dict:
    """
    Sends the image bytes to Gemini to extract the problem text and correct answer.
    """
    logger.info(f"Starting LLM problem extraction on image of size {len(image_bytes)} bytes")

    system_prompt = (
        "You are a helpful math teacher assistant. You will be provided with an image of a math problem. "
        "Your goal is to:\n"
        "1. Read the handwritten or printed math problem from the image.\n"
        "2. Solve the problem to find the correct answer.\n"
        "3. Identify the math topic.\n"
        "4. IMPORTANT: Return the question text using LaTeX for all math expressions (e.g., $3x^2 - 27 = 0$).\n"
    )

    prompt = "Extract the math problem from the image."

    logger.debug("Sending multimodal request to Gemini API for problem extraction (New SDK)")

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=media_type
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ProblemExtraction,
            )
        )
        
        if response.parsed:
            result = response.parsed.model_dump()
            logger.success(f"Successfully extracted problem info. Topic: {result.get('topic')}")
            logger.info(f"Raw Gemini problem extraction response: {result}")
            logger.info(f"Extracted Question: {result.get('question')}")
            return result
        else:
            logger.error("Gemini problem extraction response was not parsed correctly")
            raise ValueError("Invalid problem extraction format")

    except Exception as e:
        logger.error(f"LLM extraction call failed: {str(e)}")
        raise e
