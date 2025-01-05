"""Python REPL tool for executing Python code."""

import sys
import ast
import math
import numpy as np
import pandas as pd
from scipy import stats
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Type, Dict, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, validator, PrivateAttr

from utils.validators import validate_python_code
from utils.error_handlers import handle_tool_error, ToolError
from utils.formatters import format_code_snippet

class PythonREPLInput(BaseModel):
    """Input schema for Python REPL tool."""
    query: str = Field(
        ...,
        description="Python code to execute. Can include multiple statements."
    )

    @validator("query")
    def validate_code(cls, v: str) -> str:
        """Validate Python code for basic syntax."""
        try:
            # Remove markdown code block formatting if present
            if v.startswith("```") and v.endswith("```"):
                # Extract code between backticks
                lines = v.split("\n")
                # Remove first and last lines (backticks)
                code_lines = lines[1:-1]
                # Remove language identifier if present
                if code_lines and code_lines[0].lower() in ["python", "py"]:
                    code_lines = code_lines[1:]
                v = "\n".join(code_lines)
            
            # Replace escaped newlines with actual newlines
            code = v.replace('\\n', '\n')
            ast.parse(code)
            return code
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {str(e)}")
        except Exception as e:
            raise ValueError(f"Code validation failed: {str(e)}")

class PythonREPLTool(BaseTool):
    """Tool for executing Python code in a REPL environment."""
    
    name: str = Field(default="python_repl")
    description: str = Field(
        default="A Python REPL for executing code. Supports:\n"
                "1. Basic Python operations\n"
                "2. Math functions (sin, cos, sqrt, etc.)\n"
                "3. Data analysis (mean, median, std, etc.)\n"
                "4. Multiple statements and variable persistence"
    )
    args_schema: Type[BaseModel] = PythonREPLInput

    _globals: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, **kwargs):
        """Initialize the Python REPL tool."""
        super().__init__(**kwargs)
        self._globals = {
            'math': math,
            'np': np,
            'pd': pd,
            'stats': stats,
            'pi': math.pi,
            'e': math.e,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'exp': math.exp,
            'sqrt': math.sqrt,
            'mean': np.mean,
            'median': np.median,
            'std': np.std,
            'min': np.min,
            'max': np.max,
            'sum': np.sum,
            'abs': abs,
            '__builtins__': __builtins__
        }

    def _run(self, query: str) -> str:
        """Execute Python code and return the output."""
        try:
            # Validate code
            validate_python_code(query)
            
            # Capture stdout and stderr
            stdout = StringIO()
            stderr = StringIO()
            
            with redirect_stdout(stdout), redirect_stderr(stderr):
                # Execute in current globals dict
                exec(query, self._globals, self._globals)
                
                # Get output
                output = stdout.getvalue() or stderr.getvalue()
                
            return output.strip() if output.strip() else "Code executed successfully."
            
        except Exception as e:
            return handle_tool_error(e)

    async def _arun(self, query: str) -> str:
        """Run the Python REPL asynchronously."""
        return self._run(query)
