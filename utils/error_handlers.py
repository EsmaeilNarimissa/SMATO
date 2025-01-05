"""Error handling utilities for the agent system."""

import functools
import logging
import traceback
from typing import Any, Callable, TypeVar, cast, Optional, Dict, Type
from datetime import datetime
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type variable for generic function type
F = TypeVar('F', bound=Callable[..., Any])

class ErrorContext(BaseModel):
    """Context information for errors."""
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the error occurred"
    )
    function_name: Optional[str] = Field(
        default=None,
        description="Name of the function where error occurred"
    )
    args: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Arguments passed to the function"
    )
    traceback: Optional[str] = Field(
        default=None,
        description="Error traceback"
    )
    additional_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context information"
    )

class BaseError(Exception):
    """Base exception class with enhanced error handling."""
    
    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None
    ):
        """Initialize error with context."""
        super().__init__(message)
        self.context = context or ErrorContext()
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "context": self.context.dict() if self.context else None,
            "cause": str(self.cause) if self.cause else None
        }
    
    def log(self, level: int = logging.ERROR) -> None:
        """Log error with context."""
        error_dict = self.to_dict()
        logger.log(level, f"Error occurred: {error_dict}")

# For backward compatibility
AgentError = BaseError

class ToolError(BaseError):
    """Exception class for tool-related errors."""
    pass

class CalculatorError(ToolError):
    """Exception class for calculator-related errors."""
    pass

class APIError(BaseError):
    """Exception class for API-related errors."""
    pass

class ValidationError(BaseError):
    """Exception class for validation errors."""
    pass

class ConfigurationError(BaseError):
    """Exception class for configuration errors."""
    pass

class AuthenticationError(BaseError):
    """Exception class for authentication errors."""
    pass

def create_error_context(
    func: Callable,
    args: tuple,
    kwargs: dict,
    error: Exception
) -> ErrorContext:
    """Create error context from function call information."""
    return ErrorContext(
        function_name=func.__name__,
        args={
            "args": args,
            "kwargs": kwargs
        },
        traceback=traceback.format_exc(),
        additional_info={
            "error_type": type(error).__name__,
            "module": func.__module__
        }
    )

def handle_errors(
    error_class: Type[BaseError] = BaseError,
    log_level: int = logging.ERROR,
    reraise: bool = True
) -> Callable[[F], F]:
    """Decorator factory for handling errors with specific error class."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # If it's already our error type, just log and re-raise
                if isinstance(e, BaseError):
                    e.log(log_level)
                    if reraise:
                        raise
                    return None
                
                # Create error context
                context = create_error_context(func, args, kwargs, e)
                
                # Create specific error instance
                error = error_class(
                    message=str(e),
                    context=context,
                    cause=e
                )
                
                # Log error
                error.log(log_level)
                
                if reraise:
                    raise error from e
                return None
                
        return cast(F, wrapper)
    return decorator

# Specific error handlers
handle_tool_error = handle_errors(ToolError)
handle_api_error = handle_errors(APIError)
handle_validation_error = handle_errors(ValidationError)
handle_config_error = handle_errors(ConfigurationError)
handle_auth_error = handle_errors(AuthenticationError)

def get_error_message(error: Exception) -> str:
    """Get formatted error message based on error type."""
    if isinstance(error, BaseError):
        error_dict = error.to_dict()
        return (
            f"{error_dict['error_type']}: {error_dict['message']}\n"
            f"Context: {error_dict['context']}\n"
            f"Cause: {error_dict['cause']}"
        )
    return f"{type(error).__name__}: {str(error)}"


# Example usage
if __name__ == "__main__":
    # Test tool error handling
    @handle_tool_error
    def test_calculator(x: int, y: int) -> float:
        """Test function that simulates calculator operations."""
        if y == 0:
            raise CalculatorError("Division by zero")
        return x / y
    
    # Test error handling
    print("\nTesting calculator error handling:")
    try:
        result = test_calculator(10, 0)
    except Exception as e:
        print(get_error_message(e))