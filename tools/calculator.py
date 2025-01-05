"""Calculator tool for performing mathematical operations."""

import math
from typing import Dict, Any, Type, Union, Optional
from pydantic import BaseModel, Field, validator
from langchain.tools import BaseTool
from utils.validators import validate_math_expression
from utils.error_handlers import handle_tool_error, ToolError


class CalculatorInput(BaseModel):
    """Input schema for Calculator tool."""
    query: str = Field(
        ...,
        description="The mathematical expression to evaluate (e.g., '2 + 2', 'pi * r^2')."
    )

    @validator('query')
    def validate_query(cls, v):
        """Validate that the expression is non-empty."""
        if not v or not v.strip():
            raise ValueError("Expression cannot be empty")
        return v.strip()


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = (
        "[CRITICAL] Mathematical calculator for SINGLE EXPRESSIONS ONLY. NO datasets or sequences.\n"
        "\nUSE THIS TOOL IF AND ONLY IF:\n"
        "1. Input is a SINGLE mathematical expression\n"
        "2. NO square brackets [] in the input\n"
        "3. NO data analysis or statistics needed\n"
        "4. NO web searches or text processing\n"
        "\nSupports:\n"
        "1. Basic arithmetic: +, -, *, /, ^ (power)\n"
        "2. Mathematical constants: pi, e\n"
        "3. Functions: abs, round, pow\n"
        "4. Financial calculations:\n"
        "   - compound(principal, rate, time)\n"
        "   - simple(principal, rate, time)\n"
        "\nExamples:\n"
        "✓ '2 + 2'\n"
        "✓ 'compound(1000, 5, 3)'\n"
        "✓ '23 * 36 - (4^7)'\n"
        "\nDO NOT USE FOR:\n"
        "✗ '[1, 2, 3]' -> Use data_analysis\n"
        "✗ 'mean of numbers' -> Use data_analysis\n"
        "✗ 'search web' -> Use serp_search\n"
        "✗ 'what is' -> Use wikipedia"
    )
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True

    def _run(self, query: str) -> str:
        """Run the calculator synchronously."""
        try:
            if not query.strip():
                raise ValueError("Expression cannot be empty")
            
            # Enhanced mathematical functions
            allowed_names = {
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
                'round': round,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'factorial': math.factorial,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'floor': math.floor,
                'ceil': math.ceil
            }
            
            # Clean input
            expression = query.strip()
            
            # Handle factorial function
            if "factorial" in expression or "!" in expression:
                try:
                    if "!" in expression:
                        num = int(expression.replace("!", ""))
                    elif expression.startswith("factorial("):
                        num = int(expression[10:-1])  # Extract number between factorial( and )
                    else:
                        # Try to evaluate as a normal expression
                        result = eval(expression, {"__builtins__": {}}, allowed_names)
                        return str(result)
                        
                    if num < 0:
                        return "Error: Factorial is not defined for negative numbers"
                    if num > 100:
                        return "Error: Factorial too large (max: 100)"
                    return str(math.factorial(num))
                except ValueError:
                    return "Error: Invalid input for factorial calculation"
            
            # Replace power operator
            expression = expression.replace('^', '**')
            
            # Safety check for large numbers
            if '**' in expression:
                base, exp = expression.split('**')
                if float(exp) > 1000:
                    return "Error: Exponent too large (max: 1000)"
                if float(base) > 1e100:
                    return "Error: Base number too large"
            
            # Evaluate with safety checks
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # Check result size
            if isinstance(result, (int, float)) and abs(result) > 1e100:
                return "Error: Result too large to display"
                
            return str(result)
            
        except ValueError as e:
            return f"Error: Invalid input - {str(e)}"
        except ZeroDivisionError:
            return "Error: Division by zero"
        except OverflowError:
            return "Error: Number too large to compute"
        except Exception as e:
            return f"Error: Invalid calculation - {str(e)}"

    # Override both run and arun to be direct
    def run(self, query: str) -> str:
        """Run calculator directly."""
        return self._run(query)

    async def arun(self, query: str) -> str:
        """Run calculator directly async."""
        return self._run(query)