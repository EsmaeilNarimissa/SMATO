"""Formatting utilities for the agent system."""

import json
import html
import textwrap
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from bs4 import BeautifulSoup

class FormattingConfig(BaseModel):
    """Configuration for formatting options."""
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum length for truncated text"
    )
    indent_size: int = Field(
        default=2,
        description="Number of spaces for indentation",
        ge=0,
        le=8
    )
    truncation_marker: str = Field(
        default="...",
        description="Marker to show text truncation"
    )
    datetime_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Format for datetime strings"
    )
    code_block_marker: str = Field(
        default="```",
        description="Marker for code blocks"
    )

class ContentFormatter:
    """Formatter for various content types."""
    
    def __init__(self, config: Optional[FormattingConfig] = None):
        """Initialize formatter with configuration."""
        self.config = config or FormattingConfig()
    
    def format_json(
        self,
        data: Union[Dict[str, Any], List[Any]],
        pretty: bool = True
    ) -> str:
        """Format JSON data."""
        try:
            if pretty:
                return json.dumps(
                    data,
                    indent=self.config.indent_size,
                    ensure_ascii=False
                )
            return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            return f"Error formatting JSON: {str(e)}"
    
    def format_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ) -> str:
        """Format error messages with optional context."""
        parts = [f"Error: {str(error)}"]
        
        if context:
            context_str = ", ".join(
                f"{k}: {v}" for k, v in sorted(context.items())
            )
            parts.append(f"Context: {context_str}")
        
        if include_traceback and hasattr(error, "__traceback__"):
            import traceback
            tb = traceback.format_exception(
                type(error),
                error,
                error.__traceback__
            )
            parts.append("Traceback:")
            parts.extend(tb)
        
        return "\n".join(parts)
    
    def format_chat_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Format chat messages with metadata."""
        message = {
            "role": role,
            "content": content,
            "timestamp": (timestamp or datetime.now()).strftime(
                self.config.datetime_format
            )
        }
        
        if metadata:
            message["metadata"] = metadata
        
        return message
    
    def format_list(
        self,
        items: List[Any],
        max_items: Optional[int] = None,
        bullet: str = "-"
    ) -> str:
        """Format list with customizable bullets and truncation."""
        if not items:
            return "No items"
        
        # Apply truncation if needed
        if max_items and len(items) > max_items:
            visible_items = items[:max_items]
            remaining = len(items) - max_items
            formatted = [f"{bullet} {item}" for item in visible_items]
            formatted.append(f"... and {remaining} more items")
        else:
            formatted = [f"{bullet} {item}" for item in items]
        
        return "\n".join(formatted)
    
    def format_code(
        self,
        code: str,
        language: str = "python",
        line_numbers: bool = False
    ) -> str:
        """Format code with optional line numbers."""
        # Clean and normalize line endings
        code = code.strip().replace('\r\n', '\n')
        
        # Add line numbers if requested
        if line_numbers:
            lines = code.split('\n')
            max_num_width = len(str(len(lines)))
            numbered_lines = [
                f"{i+1:>{max_num_width}} | {line}"
                for i, line in enumerate(lines)
            ]
            code = '\n'.join(numbered_lines)
        
        # Wrap in code block
        return (
            f"{self.config.code_block_marker}{language}\n"
            f"{code}\n"
            f"{self.config.code_block_marker}"
        )
    
    def format_url_content(
        self,
        content: str,
        clean_html: bool = True,
        preserve_links: bool = False
    ) -> str:
        """Format URL content with HTML cleaning options."""
        if not content:
            return ""
        
        if clean_html:
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
                element.decompose()
            
            if preserve_links:
                # Convert links to markdown format
                for a in soup.find_all('a', href=True):
                    a.replace_with(f"[{a.get_text()}]({a['href']})")
            
            # Get text content
            content = soup.get_text()
        
        # Clean up whitespace
        content = ' '.join(content.split())
        
        # Apply length limit if configured
        if self.config.max_length and len(content) > self.config.max_length:
            content = content[:self.config.max_length] + self.config.truncation_marker
        
        return content
    
    def format_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        align: Optional[List[str]] = None
    ) -> str:
        """Format data as a markdown table."""
        if not headers or not rows:
            return "Empty table"
        
        # Validate and normalize alignment
        valid_aligns = {'left': ':--', 'right': '--:', 'center': ':-:'}
        if align is None:
            align = ['left'] * len(headers)
        else:
            align = [a.lower() if a.lower() in valid_aligns else 'left' for a in align]
        
        # Convert all values to strings and find column widths
        str_rows = [[str(cell) for cell in row] for row in rows]
        widths = [
            max(
                len(str(header)),
                max(len(str(row[i])) for row in str_rows)
            )
            for i, header in enumerate(headers)
        ]
        
        # Format headers
        header_row = '|' + '|'.join(
            f" {header:<{width}} " for header, width in zip(headers, widths)
        ) + '|'
        
        # Format alignment row
        align_row = '|' + '|'.join(
            f" {valid_aligns[a]:<{width}} " for a, width in zip(align, widths)
        ) + '|'
        
        # Format data rows
        data_rows = []
        for row in str_rows:
            formatted_row = '|' + '|'.join(
                f" {cell:<{width}} " for cell, width in zip(row, widths)
            ) + '|'
            data_rows.append(formatted_row)
        
        # Combine all parts
        return '\n'.join([header_row, align_row] + data_rows)


# Create global formatter instance
formatter = ContentFormatter()

# Convenience functions for backward compatibility
def format_tool_response(tool_name: str, response: Any) -> str:
    """Format tool response."""
    if isinstance(response, (dict, list)):
        return formatter.format_json(response)
    return str(response)

def format_error_message(
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Format error message."""
    return formatter.format_error(error, context)

def format_chat_message(
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format chat message."""
    return formatter.format_chat_message(role, content, metadata)

def format_list_response(
    items: List[Any],
    max_items: Optional[int] = None
) -> str:
    """Format list response."""
    return formatter.format_list(items, max_items)

def format_code_snippet(
    code: str,
    language: str = "python"
) -> str:
    """Format code snippet."""
    return formatter.format_code(code, language)

def format_url_content(
    content: str,
    max_length: Optional[int] = None
) -> str:
    """Format URL content."""
    if max_length:
        formatter.config.max_length = max_length
    return formatter.format_url_content(content)


# Example usage
if __name__ == "__main__":
    # Create formatter with custom config
    custom_formatter = ContentFormatter(
        FormattingConfig(
            max_length=100,
            indent_size=4,
            truncation_marker="…"
        )
    )
    
    # Test JSON formatting
    data = {
        "name": "Test",
        "values": [1, 2, 3],
        "nested": {"key": "value"}
    }
    print("\nJSON Formatting:")
    print(custom_formatter.format_json(data))
    
    # Test error formatting
    try:
        raise ValueError("Test error")
    except Exception as e:
        print("\nError Formatting:")
        print(custom_formatter.format_error(
            e,
            context={"operation": "test"},
            include_traceback=True
        ))
    
    # Test list formatting
    items = ["apple", "banana", "cherry", "date", "elderberry"]
    print("\nList Formatting:")
    print(custom_formatter.format_list(items, max_items=3))
    
    # Test code formatting
    code = "def hello():\n    print('Hello, World!')"
    print("\nCode Formatting:")
    print(custom_formatter.format_code(code, line_numbers=True))
    
    # Test table formatting
    headers = ["Name", "Age", "City"]
    rows = [
        ["Alice", 25, "New York"],
        ["Bob", 30, "San Francisco"]
    ]
    print("\nTable Formatting:")
    print(custom_formatter.format_table(
        headers,
        rows,
        align=["left", "right", "center"]
    ))