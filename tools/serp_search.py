"""SerpAPI tool for web searching using the SerpAPI service."""

import re
from typing import Optional, Dict, Any, List, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator
from serpapi import GoogleSearch

from utils.validators import validate_search_query
from utils.error_handlers import handle_tool_error, ToolError
from utils.formatters import format_list_response
from config.api_keys import get_serpapi_key

def test_serpapi_connection():
    """Test SerpAPI connection with current API key."""
    api_key = get_serpapi_key()
    if not api_key:
        print("Error: No SerpAPI key found in environment variables")
        return False
    
    print(f"Found API key: {api_key[:8]}... (length: {len(api_key)})")
    print(f"Key format valid: {bool(re.match(r'^[A-Za-z0-9]{32,}$', api_key))}")
    
    try:
        # Test search with simple query
        params = {
            "q": "test query",
            "num": 1,
            "api_key": api_key,
            "engine": "google"
        }
        print(f"\nMaking test request with params: {params}")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"API Error: {results['error']}")
            return False
            
        print("SerpAPI connection test successful!")
        print(f"Response keys: {list(results.keys())}")
        return True
        
    except Exception as e:
        print(f"Error testing SerpAPI connection: {str(e)}")
        return False

class SerpAPIInput(BaseModel):
    """Input schema for SerpAPI tool."""
    query: str = Field(
        ...,
        description="Search query in format: 'search_term' or 'search_term|num_results|language|country'. "
                  "Example: 'python programming' or 'python programming|5|en|us'"
    )

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate search query."""
        parts = v.split("|")
        if len(parts) > 4:
            raise ValueError("Invalid query format. Use: 'search_term' or 'search_term|num_results|language|country'")
        
        # Validate search term
        search_term = parts[0].strip()
        validate_search_query(search_term)
        
        # Validate num_results if provided
        if len(parts) > 1:
            try:
                num_results = int(parts[1])
                if not (1 <= num_results <= 10):
                    raise ValueError("Number of results must be between 1 and 10")
            except ValueError:
                raise ValueError("Invalid number of results")
        
        # Validate language if provided
        if len(parts) > 2 and (len(parts[2]) != 2):
            raise ValueError("Language code must be 2 characters (e.g., 'en')")
            
        # Validate country if provided
        if len(parts) > 3 and (len(parts[3]) != 2):
            raise ValueError("Country code must be 2 characters (e.g., 'us')")
            
        return v

class SerpAPITool(BaseTool):
    """Tool for performing web searches using SerpAPI."""
    
    name: str = Field(default="web_search")
    description: str = Field(
        default="Search the web using format: 'search_term' or 'search_term|num_results|language|country'. "
               "Example: 'python programming' or 'python programming|5|en|us'"
    )
    args_schema: Type[BaseModel] = SerpAPIInput
    api_key: Optional[str] = Field(
        default_factory=get_serpapi_key,
        description="SerpAPI key for authentication"
    )
    
    def __init__(self) -> None:
        """Initialize the SerpAPI tool."""
        super().__init__()
        if not self.api_key:
            raise ValueError("SerpAPI key not found in environment variables")
        print(f"SerpAPI Tool initialized with key: {self.api_key[:8]}...")
    
    @handle_tool_error
    def _run(self, query: str) -> str:
        """Execute the search query."""
        # Parse query parts
        parts = query.split("|")
        search_term = parts[0].strip()
        num_results = int(parts[1]) if len(parts) > 1 else 5
        language = parts[2] if len(parts) > 2 else "en"
        country = parts[3] if len(parts) > 3 else "us"
        
        # Prepare search parameters
        params = {
            "q": search_term,
            "num": num_results,
            "hl": language,
            "gl": country,
            "api_key": self.api_key,
            "engine": "google"
        }
        
        print(f"\nExecuting search with params: {params}")
        
        try:
            # Execute search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                error_msg = f"SerpAPI Error: {results['error']}"
                print(error_msg)
                return error_msg
                
            organic_results = results.get("organic_results", [])
            if not organic_results:
                no_results_msg = f"No results found for '{search_term}'"
                print(no_results_msg)
                return no_results_msg
            
            # Format results
            formatted_results = []
            for i, result in enumerate(organic_results[:num_results], 1):
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No description")
                formatted_results.append(f"{i}. {title}\nURL: {link}\n{snippet}\n")
            
            response = "\n".join(formatted_results)
            print(f"\nFound {len(formatted_results)} results")
            return response
            
        except Exception as e:
            error_msg = f"Error performing search: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def _arun(self, query: str) -> str:
        """Execute the search query asynchronously."""
        return self._run(query)


# Example usage
if __name__ == "__main__":
    # First test the API connection
    if test_serpapi_connection():
        search_tool = SerpAPITool()
        
        # Test cases
        test_queries = [
            "python programming",  # Basic search
            "machine learning|3",  # With num_results
            "paris tourism|5|fr|fr",  # Full parameters
        ]
        
        for query in test_queries:
            print(f"\nSearching for: {query}")
            try:
                result = search_tool.run(query)
                print(f"Result:\n{result}")
            except Exception as e:
                print(f"Error: {str(e)}")
    else:
        print("Skipping search tests due to API connection failure")