"""Main agent implementation for the system."""

import traceback
import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.callbacks.base import BaseCallbackHandler
from config import SYSTEM_MESSAGES, get_openai_api_key
from config.settings import MemoryConfig, settings
from .memory import AgentMemory
from tools import get_all_tools


class ToolError(Exception):
    """Custom error for tool execution failures."""
    pass


class AgentCallbackHandler(BaseCallbackHandler):
    """Callback handler for agent actions."""

    def __init__(self) -> None:
        """Initialize callback handler."""
        super().__init__()
        self.actions: List[Dict[str, Any]] = []

    def on_agent_action(self, action, **kwargs: Any) -> None:
        """Record agent actions."""
        self.actions.append({
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log
        })

    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Record agent finish."""
        self.actions.append({
            "output": finish.return_values["output"],
            "log": finish.log
        })


class Agent:
    """Main agent class that orchestrates the interaction."""

    def __init__(self, memory_config: Optional[MemoryConfig] = None, show_thinking: bool = True,
                 max_iterations: Optional[int] = None, temperature: Optional[float] = None,
                 model_name: Optional[str] = None) -> None:
        """Initialize the agent with configuration."""
        if memory_config is None:
            memory_config = MemoryConfig(
                max_messages=100,
                system_message=SYSTEM_MESSAGES["default"]
            )

        self.memory = AgentMemory(config=memory_config)

        # Initialize the LLM with tool binding
        self.llm = ChatOpenAI(
            temperature=temperature or settings.llm.temperature,
            model_name=model_name or settings.llm.model_name,
            api_key=get_openai_api_key()
        )

        # Format tools for binding
        raw_tools = get_all_tools()
        self.tools = [tool for tool in raw_tools]

        # Configure LLM to use tools
        self.llm = self.llm.bind(
            functions=[{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') else {"type": "object", "properties": {}}
            } for tool in self.tools]
        )

        def create_messages(x: str) -> List[BaseMessage]:
            return [
                SystemMessage(content=SYSTEM_MESSAGES["default"]),
                HumanMessage(content=x)
            ]

        self.chain = (
            RunnablePassthrough()
            | create_messages
            | self.llm
            | RunnableLambda(lambda x: {
                "content": x.content if hasattr(x, "content") else str(x),
                "function_call": x.additional_kwargs.get("function_call") if hasattr(x, "additional_kwargs") else None
            })
        )

    async def _handle_tool_calls(self, function_call):
        """Handle tool calls from the model."""
        try:
            tool_name = function_call["name"]
            tool_args = json.loads(function_call["arguments"])
            query = tool_args.get("query", "")

            # Get tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                return f"Tool {tool_name} not found"

            # Execute tool and return raw result
            result = await tool.arun(query)
            return result

        except Exception as e:
            return f"Error: {str(e)}"

    async def process_message(self, message: str) -> str:
        """Process a user message and return the response."""
        try:
            # Store the query for context
            self.last_query = message.lower()
            msg = message.strip()

            # Only catch EXPLICIT calculations
            is_calculation = False
            
            # Check if it starts with a function call
            function_starts = [
                "factorial(", "sin(", "cos(", "tan(", "sqrt(", "log(",
                "exp(", "abs(", "round(", "pow(", "floor(", "ceil("
            ]
            if any(msg.lower().startswith(f) for f in function_starts):
                is_calculation = True
                
            # Check if it contains operators with numbers
            operators = ["+", "-", "*", "/", "^"]
            has_numbers = any(c.isdigit() for c in msg)
            has_operators = any(op in msg for op in operators)
            if has_numbers and has_operators:
                is_calculation = True
                
            # Check if it's just a number with factorial
            if msg.replace(" ", "").replace("!", "").isdigit():
                is_calculation = True

            # If it's explicitly a calculation, use calculator directly
            if is_calculation:
                calculator = next((t for t in self.tools if t.name == "calculator"), None)
                if calculator:
                    return await calculator.arun(message)

            # Otherwise, let the LLM decide which tool to use
            response = await self.chain.ainvoke(message)

            # Handle function calls
            if response.get("function_call"):
                return await self._handle_tool_calls(response.get("function_call"))

            # Return direct response
            return response.get("content", str(response))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.memory.get_messages()

    def get_agent_actions(self) -> List[Dict[str, Any]]:
        """Get the list of actions taken by the agent."""
        return self.memory.callback_handler.actions

    def clear_history(self) -> None:
        """Clear conversation history and agent actions."""
        self.memory.clear()
        self.memory.callback_handler.actions.clear()

# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        """Test the agent with a simple interaction."""
        agent = Agent(show_thinking=True)
        response = await agent.process_message(
            "What is the weather like in Sydney today?"
        )
        print(f"Response: {response}")
        print("\nConversation history:")
        for message in agent.get_conversation_history():
            print(f"{message['role']}: {message['content']}")
        print("\nAgent actions:")
        for action in agent.get_agent_actions():
            print(action)

    asyncio.run(main())
