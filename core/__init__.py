"""Core module for the agent system."""

from .message import (
    Message,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ErrorMessage,
    MessageHistory
)

from .memory import AgentMemory, MemoryConfig
from .agent import Agent, AgentCallbackHandler

__all__ = [
    # Message types
    'Message',
    'UserMessage',
    'AssistantMessage',
    'SystemMessage',
    'ErrorMessage',
    'MessageHistory',
    
    # Memory management
    'AgentMemory',
    'MemoryConfig',
    
    # Agent
    'Agent',
    'AgentCallbackHandler',
]

# Version information
__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "A pure Python implementation of an agent system using LangChain"