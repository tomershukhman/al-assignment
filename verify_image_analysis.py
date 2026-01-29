import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow imports from backend
sys.path.append(os.getcwd())

from backend.services.llm import analyze_submission

# Path to the artifact image
IMAGE_PATH = "/Users/tomer.shukhman/.gemini/antigravity/brain/fd3cd933-f239-4d46-a942-67981811fc1c/simple_math_equation_1769716481728.png"

async def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        return

    print(f"Reading image from {IMAGE_PATH}...")
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print("Calling analyze_submission...")
    try:
        # The artifact image we checked is a JPEG
        result = await analyze_submission(
            image_bytes=image_bytes,
            media_type="image/jpeg",
            question="What is 2 + 2?",
            correct_answer="4"
        )
        
        print("\n--- Analysis Result ---")
        print(f"Is Relevant: {result.get('is_relevant')}")
        print(f"Is Correct: {result.get('is_correct')}")
        print(f"Extracted Text: {result.get('extracted_text')}")
        print(f"Analysis: {result.get('analysis')}")
        print("Feedback Steps:")
        for step in result.get('feedback', []):
            print(f"  - {step['step']} [{step['status']}]: {step.get('comment', '')}")
            
        # Basic assertions
        assert result['is_relevant'] is True
        assert result['is_correct'] is True
        assert "2" in result['extracted_text'] or "4" in result['extracted_text'] # Loose check
        print("\n✅ Verification Successful!")

    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
