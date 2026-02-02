import requests
import json
import os
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.json import JSON
from rich.live import Live
from rich.table import Table

console = Console()

# API endpoint
API_URL = "http://localhost:8000/api/chat"

# Test images - Ensure these paths exist on your machine
PROBLEM_IMAGE = "example-imgs/problems/test/problem.png"
SOLUTION_IMAGE = "example-imgs/problems/test/correct_clean.png"


def send_message(message: str, image_path: str = None, conversation_history: list = None):
    """
    Send a message to the chat API.
    Handles file uploads and state persistence correctly.
    """
    if message:
        console.print(f"\n[bold blue]>>> User:[/bold blue] {message}")
    if image_path:
        console.print(f"[dim]📎 Attached: {image_path}[/dim]")
    
    # 1. Prepare Data Form
    data = {"message": message or ""}
    
    if conversation_history:
        data["conversation_history"] = json.dumps(conversation_history)
    
    # 2. Prepare Files
    files = {}
    file_obj = None
    
    try:
        if image_path:
            p = Path(image_path)
            if not p.exists():
                console.print(f"[red]Error: Image not found: {image_path}[/red]")
                return None
            
            file_obj = open(p, "rb")
            files["image"] = (p.name, file_obj, "image/png")

        # 3. Make Request
        response = requests.post(API_URL, data=data, files=files)
        response.raise_for_status()
        result = response.json()
        
        # 4. Display Response
        console.print(f"\n[bold green]<<< Agent:[/bold green]")
        response_text = result.get("response", "No response text")
        console.print(Panel(response_text, title="Response", border_style="green"))
        
        # 5. Display Tool Usage (Debug Info)
        if result.get("tool_results"):
            for tool_result in result["tool_results"]:
                tool_name = tool_result.get("name", "unknown")
                tool_output = tool_result.get("result", {})
                
                # Robustly parse tool_output if it appears to be a JSON string
                if isinstance(tool_output, str):
                    try:
                        # Sometimes tool output is double-encoded or just a string
                        parsed = json.loads(tool_output)
                        if isinstance(parsed, (dict, list)):
                            tool_output = parsed
                    except:
                        pass

                if tool_name == "extract_problem_from_image":
                    console.print(f"\n[bold yellow]🔍 Extracted Problem (LaTeX):[/bold yellow]")
                    if isinstance(tool_output, dict):
                        latex = tool_output.get("question", "N/A")
                        topic = tool_output.get("topic", "N/A")
                        console.print(f"[dim]Topic: {topic}[/dim]")
                        console.print(Panel(Syntax(latex, "latex", theme="monokai"), title="LaTeX Extraction"))
                    else:
                        console.print(f"[dim]Raw output: {tool_output}[/dim]")
                
                elif tool_name == "analyze_solution":
                    console.print(f"\n[bold yellow]📝 Solution Analysis:[/bold yellow]")
                    if isinstance(tool_output, dict):
                        is_correct = tool_output.get("is_correct", "Unknown")
                        feedback = tool_output.get("feedback", "No feedback")
                        status_color = "green" if is_correct is True else "red"
                        
                        console.print(f"[bold {status_color}]Correct: {is_correct}[/bold {status_color}]")
                        
                        # Handle list of feedback steps
                        if isinstance(feedback, list):
                            for step in feedback:
                                step_name = step.get("step", "Step")
                                step_status = step.get("status", "unknown")
                                comment = step.get("comment", "")
                                symbol = "✅" if step_status == "correct" else "❌"
                                console.print(f"  {symbol} [bold]{step_name}[/bold]: {comment}")
                        else:
                            console.print(Panel(str(feedback), title="Feedback", border_style=status_color))
                    else:
                        console.print(f"[dim]Raw output: {tool_output}[/dim]")

        return result
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Request failed: {e}[/red]")
        if hasattr(e, 'response') and e.response is not None:
            try:
                console.print(f"[red]Server Error Detail: {e.response.json()}[/red]")
            except:
                console.print(f"[red]Server Error Body: {e.response.text}[/red]")
        return None
        
    finally:
        if file_obj:
            file_obj.close()


def run_interactive(conversation=None):
    """Run an interactive chat session."""
    if conversation is None:
        conversation = []
        
    console.print(Panel("[bold green]Interactive Mode Started[/bold green]\nType 'exit' to quit.", border_style="green"))
    
    while True:
        try:
            user_input = console.input("\n[bold blue]You:[/bold blue] ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Simple check for image attachment
            image_path = None
            if user_input.startswith("/image "):
                parts = user_input.split(" ", 2)
                if len(parts) >= 2:
                    image_path = parts[1]
                    user_input = parts[2] if len(parts) > 2 else ""
            
            result = send_message(user_input, image_path, conversation)
            if result:
                conversation = result.get("conversation", [])
        except KeyboardInterrupt:
            break


def main():
    parser = argparse.ArgumentParser(description="Test Chat API")
    parser.add_argument("--interactive", action="store_true", help="Run interactive mode")
    args = parser.parse_args()

    if args.interactive:
        run_interactive()
        return

    console.print(Panel.fit(
        "[bold cyan]Chat API Scenario Simulation[/bold cyan]\n"
        "1. Agent starts\n2. User sends problem\n3. Agent extracts\n4. User sends solution",
        border_style="cyan"
    ))
    
    conversation = []
    
    # Step 0: Agent starts
    console.print("\n[bold magenta]Step 0: Agent starts (Initial Greeting)[/bold magenta]")
    result = send_message(
        message="Hello",  # Sending a simple greeting to trigger agent start
        conversation_history=conversation
    )
    if result:
        conversation = result.get("conversation", [])
    
    # Step 1: User sends problem
    console.print("\n[bold magenta]Step 1: User sends problem[/bold magenta]")
    result = send_message(
        message="Help me with this problem",
        image_path=PROBLEM_IMAGE,
        conversation_history=conversation
    )
    if result:
        conversation = result.get("conversation", [])
    
    # Step 2 & 3: User sends solution
    # (Step 2 is implicit in the Agent's response to Step 1, where it shows extraction)
    console.print("\n[bold magenta]Step 3: User sends solution[/bold magenta]")
    result = send_message(
        message="Here is my solution",
        image_path=SOLUTION_IMAGE,
        conversation_history=conversation
    )
    
    if result:
        console.print("\n" + "="*80)
        console.print(Panel.fit(
            "[bold green]✅ Scenario completed successfully![/bold green]",
            border_style="green"
        ))


if __name__ == "__main__":
    main()