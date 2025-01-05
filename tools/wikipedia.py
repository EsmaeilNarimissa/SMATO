"""Wikipedia tool for searching and retrieving Wikipedia content."""

from typing import List, Optional, Type, Dict, Any
import wikipedia
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator

from utils.validators import validate_search_query
from utils.error_handlers import handle_tool_error
from utils.formatters import format_list_response

class WikipediaInput(BaseModel):
    """Input schema for Wikipedia tool."""
    query: str = Field(
        ...,
        description="The search query for Wikipedia articles. Format: 'search_term' or 'search_term|num_results|language'. "
                  "Example: 'Albert Einstein' or 'Albert Einstein|3|en'"
    )

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate query format."""
        parts = v.split("|")
        if len(parts) > 3:
            raise ValueError("Invalid query format. Use: 'search_term' or 'search_term|num_results|language'")
        if len(parts) > 1:
            try:
                num_results = int(parts[1])
                if not (1 <= num_results <= 5):
                    raise ValueError("Number of results must be between 1 and 5")
            except ValueError:
                raise ValueError("Invalid number of results")
        if len(parts) > 2 and parts[2] not in wikipedia.languages():
            raise ValueError(f"Invalid language code: {parts[2]}")
        return v

class WikipediaTool(BaseTool):
    """Tool for searching and retrieving Wikipedia content."""
    
    name: str = Field(default="wikipedia")
    description: str = Field(
        default="Search Wikipedia articles. Use format: 'search_term' or 'search_term|num_results|language'. "
               "Example: 'Albert Einstein' or 'Albert Einstein|3|en'"
    )
    args_schema: Type[BaseModel] = WikipediaInput
    
    @handle_tool_error
    def _run(self, query: str) -> str:
        """Search Wikipedia and return results."""
        # Parse query parts
        parts = query.split("|")
        search_term = parts[0].strip()
        num_results = int(parts[1]) if len(parts) > 1 else 1
        language = parts[2] if len(parts) > 2 else "en"
        
        # Set language
        wikipedia.set_lang(language)
        
        try:
            # Search for pages
            search_results = wikipedia.search(search_term, results=num_results)
            if not search_results:
                return f"No Wikipedia articles found for '{search_term}'"
            
            # Get summaries
            results = []
            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    summary = page.summary.split('\n')[0]  # Get first paragraph
                    results.append(f"Title: {title}\nURL: {page.url}\nSummary: {summary}\n")
                except wikipedia.DisambiguationError as e:
                    options = e.options[:5]  # Limit options
                    results.append(f"'{title}' is ambiguous. Options: {', '.join(options)}\n")
                except wikipedia.PageError:
                    continue
            
            return "\n".join(results) if results else f"Could not retrieve content for '{search_term}'"
            
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Search Wikipedia asynchronously."""
        return self._run(query)


# Example usage
if __name__ == "__main__":
    wiki_tool = WikipediaTool()
    
    # Test cases
    test_queries = [
        "Python programming",  # Basic search
        "Einstein|3",  # Multiple results
        "Tokyo|2|ja",  # Japanese language
        "NonexistentArticle",  # No results
        "Python|1|invalid"  # Invalid language
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        result = wiki_tool.run(query)
        print(f"Result:\n{result}")