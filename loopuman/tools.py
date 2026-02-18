"""
Framework integrations for Loopuman.
Drop-in tools for LangChain, CrewAI, and other agent frameworks.
"""

from loopuman.client import Loopuman, LoopumanError


# ── Standalone function (works everywhere) ─────────────────

def ask_human(
    question: str,
    category: str = "other",
    budget_vae: int = 50,
    estimated_seconds: int = 120,
    api_key: str = None,
) -> str:
    """
    Route a question to a real human. Returns their answer.
    
    Works without any framework. Just call it.
    
    Args:
        question: What the human should do (be specific)
        category: writing, research, data, survey, image, local, translation, audio, other
        budget_vae: Cost in VAE (100 VAE = $1.00 USD). Minimum 10.
        estimated_seconds: Expected time for worker to complete (required — enforces $6/hr min rate)
        api_key: Optional, reads LOOPUMAN_API_KEY from env if not set
    """
    client = Loopuman(api_key=api_key)
    return client.ask(question, category=category, budget_vae=budget_vae, estimated_seconds=estimated_seconds)


# ── LangChain Tool ─────────────────────────────────────────

def langchain_tool(api_key: str = None):
    """
    Create a LangChain-compatible tool for human tasks.
    
    Usage:
        from loopuman.tools import langchain_tool
        tools = [langchain_tool()]
        agent = initialize_agent(tools=tools, llm=llm)
    """
    try:
        from langchain.tools import tool as lc_tool
    except ImportError:
        try:
            from langchain_core.tools import tool as lc_tool
        except ImportError:
            raise ImportError("Install langchain: pip install langchain-core")

    client = Loopuman(api_key=api_key)

    @lc_tool
    def loopuman_human_task(task_description: str) -> str:
        """Route a task to a real human when AI cannot complete it.
        
        Use this tool when you encounter:
        - CAPTCHAs or bot detection
        - Phone calls or SMS verification needed
        - Physical world actions (visit location, take photo)
        - Subjective judgment (content moderation, design feedback)
        - App testing on real devices
        - Translation review by native speakers
        - Data labeling or RLHF evaluation
        - Any task requiring a real person
        
        Input: A clear, specific description of what the human should do.
        Output: The human's response (typically within 5-15 minutes).
        Cost: $0.10-$2.00 depending on complexity.
        """
        try:
            return client.ask(task_description, budget_vae=50, estimated_seconds=120)
        except LoopumanError as e:
            return f"Human task failed: {e}"

    return loopuman_human_task


# ── CrewAI Tool ────────────────────────────────────────────

def crewai_tool(api_key: str = None):
    """
    Create a CrewAI-compatible tool for human tasks.
    
    Usage:
        from loopuman.tools import crewai_tool
        from crewai import Agent
        agent = Agent(tools=[crewai_tool()], ...)
    """
    try:
        from crewai.tools import tool as crew_tool
    except ImportError:
        raise ImportError("Install crewai: pip install crewai")

    client = Loopuman(api_key=api_key)

    @crew_tool("Human Task")
    def loopuman_human_task(task_description: str) -> str:
        """Route a task to a real human when AI cannot complete it.
        Use for CAPTCHAs, phone calls, physical actions, subjective judgment,
        content moderation, translation review, data labeling, or RLHF evaluation.
        Provide a clear, specific description. Human responds in 5-15 minutes.
        Cost: $0.10-$2.00 per task."""
        try:
            return client.ask(task_description, budget_vae=50, estimated_seconds=120)
        except LoopumanError as e:
            return f"Human task failed: {e}"

    return loopuman_human_task


# ── AutoGen Tool ───────────────────────────────────────────

def autogen_function_map(api_key: str = None) -> dict:
    """
    Create an AutoGen-compatible function map.
    
    Usage:
        from loopuman.tools import autogen_function_map
        assistant = autogen.AssistantAgent(
            "assistant",
            function_map=autogen_function_map()
        )
    """
    client = Loopuman(api_key=api_key)

    def ask_human_worker(task_description: str, category: str = "other", budget_vae: int = 50, estimated_seconds: int = 120) -> str:
        """Route a task to a real human worker."""
        try:
            return client.ask(task_description, category=category, budget_vae=budget_vae, estimated_seconds=estimated_seconds)
        except LoopumanError as e:
            return f"Human task failed: {e}"

    return {"ask_human_worker": ask_human_worker}


# ── OpenAI Function Calling Schema ────────────────────────

OPENAI_FUNCTION_SCHEMA = {
    "name": "ask_human_worker",
    "description": (
        "Route a task to a real human when AI cannot complete it. "
        "Use for CAPTCHAs, phone calls, SMS verification, physical world actions, "
        "subjective judgment, content moderation, translation review, data labeling, "
        "RLHF evaluation, or any task requiring a real person. "
        "Human typically responds within 5-15 minutes. Cost: $0.10-$2.00."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "task_description": {
                "type": "string",
                "description": "Clear, specific description of what the human should do",
            },
            "category": {
                "type": "string",
                "enum": [
                    "writing", "research", "data", "survey", "image",
                    "local", "translation", "audio", "other",
                ],
                "description": "Task category for worker matching",
            },
            "budget_vae": {
                "type": "integer",
                "description": "Budget in VAE (100 VAE = $1.00 USD). Minimum 10.",
                "default": 50,
            },
            "estimated_seconds": {
                "type": "integer",
                "description": "Expected time in seconds for worker to complete. Platform enforces $6/hr minimum rate.",
                "default": 120,
            },
        },
        "required": ["task_description", "estimated_seconds"],
    },
}
