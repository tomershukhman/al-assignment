import httpx
import asyncio
import os
import argparse
import json

async def process_image(client, url, image_path):
    print(f"\n--- Processing: {image_path} ---")
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    try:
        with open(image_path, "rb") as f:
            filename = os.path.basename(image_path)
            files = {"file": (filename, f, "image/png")}
            response = await client.post(url, files=files, timeout=60.0)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Confidence: {data.get('confidence')}")
                print(f"Text: {data.get('text')}")
            else:
                print("Error response:")
                print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Test OCR API")
    parser.add_argument("--file", help="Path to a specific image file to test")
    args = parser.parse_args()

    url = "http://127.0.0.1:8000/ocr"
    
    async with httpx.AsyncClient() as client:
        if args.file:
            await process_image(client, url, args.file)
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
                await process_image(client, url, image_path)

if __name__ == "__main__":
    asyncio.run(main())
