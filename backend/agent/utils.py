
import tempfile
import base64
import os
from loguru import logger
from typing import Optional, Tuple

def save_temp_image(image_data: bytes, media_type: str) -> str:
    """Save raw image bytes to a temporary file and return the path."""
    try:
        suffix = ".png" if "png" in media_type else ".jpg"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(image_data)
        temp_file.flush()
        temp_file.close()
        logger.info(f"Saved temp image to: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Failed to save temp image: {e}")
        raise e

def create_image_message_content(message_text: str, image_data: bytes, media_type: str, image_path: str) -> list:
    """Create the multimodal message content block for LangChain."""
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    return [
        {"type": "text", "text": message_text},
        {
            "type": "image_url", 
            "image_url": {"url": f"data:{media_type};base64,{image_b64}"}
        },
        # System breadcrumb for file path persistence
        {
            "type": "text", 
            "text": f"\n[SYSTEM: Image saved at {image_path}]"
        }
    ]
