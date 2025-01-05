"""Message handling for the agent system."""

from datetime import datetime
from typing import Optional, Dict, Any, List, Type
from pydantic import BaseModel, Field, validator
from langchain_core.messages import (
    SystemMessage as LangChainSystemMessage,
    HumanMessage as LangChainHumanMessage,
    AIMessage as LangChainAIMessage
)

from utils.formatters import format_chat_message

class MessageMetadata(BaseModel):
    """Schema for message metadata."""
    source: Optional[str] = Field(
        default=None,
        description="Source of the message"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Tool calls made during message processing"
    )
    tokens: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        description="Token usage information"
    )
    extra: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

class Message(BaseModel):
    """Base message class for all message types."""
    
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(
        ...,
        description="Content of the message",
        min_length=1
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Message timestamp"
    )
    metadata: Optional[MessageMetadata] = Field(
        default_factory=MessageMetadata,
        description="Message metadata"
    )

    @validator("content")
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata.dict() if self.metadata else None
        }
    
    def format(self) -> str:
        """Format message for display."""
        return format_chat_message(self)

class UserMessage(Message):
    """Message from the user."""
    role: str = "user"
    
    def to_langchain_message(self) -> LangChainHumanMessage:
        """Convert to LangChain HumanMessage."""
        return LangChainHumanMessage(content=self.content)

class AssistantMessage(Message):
    """Message from the assistant."""
    role: str = "assistant"
    
    def to_langchain_message(self) -> LangChainAIMessage:
        """Convert to LangChain AIMessage."""
        return LangChainAIMessage(content=self.content)

class SystemMessage(Message):
    """System message for setting context or behavior."""
    role: str = "system"
    
    def to_langchain_message(self) -> LangChainSystemMessage:
        """Convert to LangChain SystemMessage."""
        return LangChainSystemMessage(content=self.content)

class ErrorMessage(Message):
    """Error message for handling errors in conversation."""
    role: str = "error"
    error_type: str = Field(
        ...,
        description="Type of error that occurred"
    )
    traceback: Optional[str] = Field(
        default=None,
        description="Error traceback if available"
    )
    
    def to_langchain_message(self) -> LangChainSystemMessage:
        """Convert to LangChain SystemMessage."""
        content = f"Error: {self.error_type}\n{self.content}"
        if self.traceback:
            content += f"\n\nTraceback:\n{self.traceback}"
        return LangChainSystemMessage(content=content)

class MessageHistory:
    """Manages conversation message history."""
    
    def __init__(self, max_messages: Optional[int] = None) -> None:
        """Initialize message history."""
        self.max_messages = max_messages
        self.messages: List[Message] = []
    
    def add_message(self, message: Message) -> None:
        """Add a message to history."""
        self.messages.append(message)
        if self.max_messages and len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in history as dictionaries."""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """Clear message history."""
        self.messages.clear()


# Example usage
if __name__ == "__main__":
    # Create message history
    history = MessageHistory(max_messages=5)
    
    # Add different types of messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Hello!"),
        AssistantMessage(content="Hi! How can I help you?"),
        ErrorMessage(
            content="Division by zero",
            error_type="ZeroDivisionError",
            traceback="Traceback: ..."
        )
    ]
    
    # Test message handling
    for msg in messages:
        print(f"\nAdding message: {msg.role}")
        history.add_message(msg)
        print(f"Message content: {msg.content}")
        print(f"Formatted: {msg.format()}")
    
    # Print all messages
    print("\nAll messages:")
    for msg_dict in history.get_messages():
        print(f"{msg_dict['role']}: {msg_dict['content']}")