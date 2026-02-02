
try:
    from backend.services.agent_service import format_conversation_for_storage
    print("Successfully imported format_conversation_for_storage")
except ImportError as e:
    print(f"Failed to import: {e}")
    exit(1)
except Exception as e:
    print(f"Other error: {e}")
    exit(1)
