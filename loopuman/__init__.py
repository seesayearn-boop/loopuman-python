"""
Loopuman — The Human Layer for AI
Route tasks to real verified humans worldwide. One API call → result in minutes.

Usage:
    from loopuman import Loopuman
    
    client = Loopuman()  # reads LOOPUMAN_API_KEY from env
    result = client.ask("Is the cafe at 123 Main St open right now?")
    print(result)
"""

from loopuman.client import Loopuman, Task, TaskStatus, LoopumanError, InsufficientBalanceError
from loopuman.tools import langchain_tool, crewai_tool

__version__ = "0.1.0"
__all__ = ["Loopuman", "Task", "TaskStatus", "LoopumanError", "InsufficientBalanceError", "langchain_tool", "crewai_tool"]
