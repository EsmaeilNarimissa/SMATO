"""Memory management for the agent system."""

from typing import List, Dict, Any, Optional, Type
from langchain_core.memory import BaseMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage as LangChainSystemMessage
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

from config.settings import MemoryConfig
from .message import Message, MessageHistory, SystemMessage, UserMessage, AssistantMessage

class AgentMemory:
    """Memory management system for the agent."""
    
    def __init__(
        self,
        config: Optional[MemoryConfig] = None
    ) -> None:
        """Initialize the agent memory system."""
        self.config = config or MemoryConfig()
        
        # Initialize message history
        self.message_history = MessageHistory(
            max_messages=self.config.max_messages
        )
        
        # Initialize LangChain memory with updated imports
        self.langchain_memory = ConversationBufferMemory(
            memory_key=self.config.memory_key,
            return_messages=True,
            output_key="output"
        )
        
        # Add system message if provided
        if self.config.system_message:
            self.add_message(SystemMessage(content=self.config.system_message))
    
    def add_message(self, message: Message) -> None:
        """Add a message to both message histories."""
        # Add to our message history
        self.message_history.add_message(message)
        
        # Convert and add to LangChain memory
        if isinstance(message, UserMessage):
            self.langchain_memory.chat_memory.add_message(
                HumanMessage(content=message.content)
            )
        elif isinstance(message, AssistantMessage):
            self.langchain_memory.chat_memory.add_message(
                AIMessage(content=message.content)
            )
        elif isinstance(message, SystemMessage):
            self.langchain_memory.chat_memory.add_message(
                LangChainSystemMessage(content=message.content)
            )
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the history."""
        return self.message_history.get_messages()
    
    def clear(self) -> None:
        """Clear both message histories."""
        self.message_history.clear()
        self.langchain_memory.clear()
    
    def get_langchain_memory(self) -> BaseMemory:
        """Get LangChain memory object."""
        return self.langchain_memory