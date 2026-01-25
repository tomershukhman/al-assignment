import json
import httpx
from .config import settings
from loguru import logger

MATHPIX_API_URL = "https://api.mathpix.com/v3/text"

async def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Sends image bytes to Mathpix API and returns the result dictionary.
    Includes text, latex_styled, confidence, etc.
    """
    logger.info(f"Starting OCR extraction. Image size: {len(image_bytes)} bytes")
    
    options = {
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True,
        "formats": ["text", "latex_styled"],
        "data_options": {
            "include_asciimath": True
        }
    }
    
    headers = {
        "app_id": settings.MATHPIX_APP_ID,
        "app_key": settings.MATHPIX_APP_KEY
    }
    
    data = {
        "options_json": json.dumps(options)
    }
    
    files = {"file": image_bytes}
    
    logger.debug(f"Sending request to Mathpix API at {MATHPIX_API_URL}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            MATHPIX_API_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=30.0
        )
    
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"Mathpix API failed with status {e.response.status_code}: {e.response.text}")
        raise e
        
    result = response.json()
    logger.info(f"Mathpix API response confidence: {result.get('confidence', 'N/A')}")
    logger.success(f"OCR extraction successful. Text: {result.get('text', '')[:100]}")
    return result
