"""Utility functions for the agent system."""

from .error_handlers import (
    handle_tool_error,
    handle_api_error,
    get_error_message,
    BaseError,  # Changed from AgentError
    ToolError,
    APIError,
    ValidationError,
    ConfigurationError,
    AuthenticationError,
)

from .formatters import (
    format_tool_response,
    format_error_message,
    format_chat_message,
    format_list_response,
    format_code_snippet,
    format_url_content,
)

from .validators import (
    validate_url,
    validate_python_code,
    validate_math_expression,
    validate_api_key,
    validate_search_query,
)

# Define all exports
__all__ = [
    # Error handlers
    'handle_tool_error',
    'handle_api_error',
    'get_error_message',
    'BaseError',  # Changed from AgentError
    'ToolError',
    'APIError',
    'ValidationError',
    'ConfigurationError',
    'AuthenticationError',
    
    # Formatters
    'format_tool_response',
    'format_error_message',
    'format_chat_message',
    'format_list_response',
    'format_code_snippet',
    'format_url_content',
    
    # Validators
    'validate_url',
    'validate_python_code',
    'validate_math_expression',
    'validate_api_key',
    'validate_search_query',
]