import httpx
import asyncio
import os
import argparse
import json

async def process_image(client, url, image_path, problem_id=None):
    print(f"\n--- Processing: {image_path} ---")
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    try:
        with open(image_path, "rb") as f:
            filename = os.path.basename(image_path)
            files = {"file": (filename, f, "image/png")}
            data = {}
            if problem_id:
                data["problem_id"] = problem_id
            else:
                # Dummy context for testing if no problem_id
                data["question"] = "Solve for x: 2x + 5 = 15"
                data["correct_answer"] = "5"
            
            response = await client.post(url, files=files, data=data, timeout=60.0)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"OCR Text: {data.get('ocr_text')}")
                print(f"Feedback: {json.dumps(data.get('feedback'), indent=2)}")
            else:
                print("Error response:")
                print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Test OCR & LLM API")
    parser.add_argument("--file", default="example-imgs/correct_clean.png", help="Path to a specific image file to test")
    parser.add_argument("--problem_id", default="frac-add-002", help="Database ID of the problem")
    args = parser.parse_args()

    url = "http://127.0.0.1:8000/api/submissions"
    
    async with httpx.AsyncClient() as client:
        if args.file:
            await process_image(client, url, args.file, args.problem_id)
        else:
            example_dir = "example-imgs"
            if not os.path.exists(example_dir):
                print(f"Directory not found: {example_dir}")
                return

            # Process all png images
            for filename in os.listdir(example_dir):
                if not filename.lower().endswith(".png"):
                    continue
                
                image_path = os.path.join(example_dir, filename)
                await process_image(client, url, image_path, args.problem_id)

if __name__ == "__main__":
    asyncio.run(main())
