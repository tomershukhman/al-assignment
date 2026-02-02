from typing import Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import trim_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from loguru import logger

from ..config import settings
from .tools import ALL_TOOLS
from .prompts import MATH_TUTOR_SYSTEM_PROMPT, IMAGE_PATH_INSTRUCTION, PROBLEM_CONTEXT_TEMPLATE


class AgentState(MessagesState):
    """
    State for the math tutoring agent.
    """
    # Stores extracted problem details (topic, question, answer)
    current_problem: dict | None = None
    
    # Stores the local file path of the currently active image.
    current_image_path: str | None = None 


def create_agent():
    """
    Create and compile the LangGraph agent with memory and trimming.
    """
    logger.info("Creating math tutoring agent")
    
    # Initialize Memory
    # NOTE: In production, switch to SqliteSaver or PostgresSaver for persistence.
    checkpointer = InMemorySaver()

    # Initialize Gemini
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
    )
    
    # Bind tools
    model_with_tools = model.bind_tools(ALL_TOOLS)

    # Define Trimmer
    # Keeps the last ~10 messages related to strategy/context
    trimmer = trim_messages(
        max_tokens=20000,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )
    
    # Define the agent node
    def call_model(state: AgentState):
        messages = state["messages"]
        
        # 1. Base System Prompt
        system_content = MATH_TUTOR_SYSTEM_PROMPT

        # 2. Inject Path from State
        if state.get("current_image_path"):
            path = state["current_image_path"]
            system_content += IMAGE_PATH_INSTRUCTION.format(path=path)
        
        # 3. Add Problem Context if available
        # Note: current_problem is now updated automatically by the tool via Command (if tool was called)
        # OR persisted in state from previous turns.
        current_problem = state.get("current_problem")
        
        if current_problem:
            system_content += PROBLEM_CONTEXT_TEMPLATE.format(
                topic=current_problem.get('topic', 'unknown'),
                question=current_problem.get('question', 'N/A'),
                correct_answer=current_problem.get('correct_answer', 'N/A')
            )

        # Prepend the system message
        system_message = {"role": "system", "content": system_content}
        messages_with_system = [system_message] + messages
        
        # Trim messages before sending to model
        # We trim everything AFTER the system message we just constructed?
        # Actually, trim_messages usually takes the full list.
        # But our system message is dynamic.
        # Safe bet: Trim the conversation history (state["messages"]), then prepend system.
        trimmed_history = trimmer.invoke(messages)
        
        final_messages = [system_message] + trimmed_history
        
        logger.debug(f"Calling model with {len(final_messages)} messages (trimmed)")
        response = model_with_tools.invoke(final_messages)
        
        return {"messages": [response]}
    
    # Routing logic
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "__end__"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    workflow.add_edge("tools", "agent")
    
    agent = workflow.compile(checkpointer=checkpointer)
    logger.success("Agent compiled successfully with MemorySaver")
    return agent

math_tutor_agent = create_agent()