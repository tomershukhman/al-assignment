
import requests
import sys

API_URL = "http://127.0.0.1:8000/api"

def test_persistence():
    print("1. Sending message...")
    try:
        resp = requests.post(f"{API_URL}/chat", data={"message": "My lucky number is 777"})
        resp.raise_for_status()
        data = resp.json()
        thread_id = data.get("thread_id")
        print(f"Message sent. Thread ID: {thread_id}")
        
        if not thread_id:
            print("ERROR: No thread_id returned")
            sys.exit(1)
            
        print("2. Retrieving history...")
        history_resp = requests.get(f"{API_URL}/chat/history/{thread_id}")
        history_resp.raise_for_status()
        history = history_resp.json()
        print(f"History retrieved. Length: {len(history)}")
        
        # Verify content exists
        # History should have:
        # 1. User: "My lucky number is 777"
        # 2. Assistant: (response)
        
        found_message = False
        for msg in history:
            print(f"- {msg['role']}: {msg.get('content')}")
            if msg['role'] == 'user' and '777' in msg.get('content', ''):
                found_message = True
                
        if found_message:
            print("SUCCESS: User message found in history!")
        else:
            print("FAILURE: User message not found in history.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_persistence()
