import json
import httpx
from .config import settings

MATHPIX_API_URL = "https://api.mathpix.com/v3/text"

async def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Sends image bytes to Mathpix API and returns the result dictionary.
    Includes text, latex_styled, confidence, etc.
    """
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
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            MATHPIX_API_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=30.0
        )
        
    response.raise_for_status()
    return response.json()
