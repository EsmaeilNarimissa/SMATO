"""URL tool for fetching and processing web content."""

from typing import Optional, Type, Dict, Any
import aiohttp
import requests
from bs4 import BeautifulSoup
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, HttpUrl

from utils.validators import validate_url
from utils.formatters import format_url_content
from utils.error_handlers import handle_tool_error

class URLInput(BaseModel):
    """Input schema for URL tool."""
    query: str = Field(  # Changed from url to query for single input
        ...,
        description="The URL to fetch content from (must start with http:// or https://)"
    )

class URLTool(BaseTool):
    """Tool for fetching and processing content from URLs."""
    
    name: str = Field(default="url_fetch")
    description: str = Field(
        default="A tool for fetching and extracting text content from web URLs. "
               "Input should be a valid URL starting with http:// or https://."
    )
    args_schema: Type[BaseModel] = URLInput
    headers: Dict[str, str] = Field(
        default_factory=lambda: {
            'User-Agent': 'Mozilla/5.0 (compatible; LangChainAgent/1.0)'
        }
    )
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract meaningful text."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'head', 'header', 'footer', 'nav']):
            element.decompose()
        
        # Get text and clean it
        text = soup.get_text(separator=' ')
        return ' '.join(text.split())
    
    @handle_tool_error
    def _run(self, query: str) -> str:  # Changed from url to query
        """Run the URL tool."""
        # Validate URL
        validate_url(query)  # Using query instead of url
        
        try:
            # Make request with default timeout
            response = requests.get(
                query,  # Using query instead of url
                headers=self.headers,
                timeout=10  # Default timeout
            )
            response.raise_for_status()
            
            # Clean and format content
            cleaned_text = self._clean_html(response.text)
            return format_url_content(cleaned_text, max_length=1000)  # Default max_length
            
        except Exception as e:
            raise RuntimeError(f"Error fetching URL content: {str(e)}")
    
    async def _arun(self, query: str) -> str:  # Changed from url to query
        """Run the URL tool asynchronously."""
        # Validate URL
        validate_url(query)  # Using query instead of url
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(query, timeout=10) as response:  # Default timeout
                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status}: {response.reason}")
                    
                    html_content = await response.text()
                    cleaned_text = self._clean_html(html_content)
                    return format_url_content(cleaned_text, max_length=1000)  # Default max_length
                    
        except Exception as e:
            raise RuntimeError(f"Error fetching URL content: {str(e)}")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_url_tool():
        """Test the URL tool with a sample URL."""
        tool = URLTool()
        test_url = "https://example.com"
        
        try:
            # Test synchronous execution
            result = tool.run(test_url)
            print("\nSynchronous result:")
            print(result)
            
            # Test asynchronous execution
            result = await tool.arun(test_url)
            print("\nAsynchronous result:")
            print(result)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    asyncio.run(test_url_tool())