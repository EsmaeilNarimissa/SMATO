"""Tool initialization and management."""

from typing import List
from langchain_core.tools import BaseTool

from .calculator import CalculatorTool
from .python_repl import PythonREPLTool
from .serp_search import SerpAPITool
from .url import URLTool
from .wikipedia import WikipediaTool
from .data_analysis import DataAnalysisTool

def get_all_tools() -> List[BaseTool]:
    """Get all available tools."""
    return [
        CalculatorTool(),
        PythonREPLTool(),
        SerpAPITool(),
        URLTool(),
        WikipediaTool(),
        DataAnalysisTool(),
    ]

__all__ = [
    "CalculatorTool",
    "PythonREPLTool",
    "SerpAPITool",
    "URLTool",
    "WikipediaTool",
    "DataAnalysisTool",
    "get_all_tools",
]