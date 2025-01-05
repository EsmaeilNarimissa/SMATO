"""Validation utilities for the agent system."""

import re
import ast
from typing import Any, List, Optional, Tuple, Dict, Union
from urllib.parse import urlparse
from pydantic import BaseModel, Field, validator

class ValidationResult(BaseModel):
    """Result of a validation check."""
    is_valid: bool = Field(..., description="Whether the validation passed")
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if validation failed"
    )
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional validation details"
    )

class URLValidator(BaseModel):
    """URL validation configuration."""
    url: str = Field(..., description="URL to validate")
    check_accessibility: bool = Field(
        default=False,
        description="Whether to check if URL is accessible"
    )
    allowed_schemes: List[str] = Field(
        default=["http", "https"],
        description="Allowed URL schemes"
    )

    def validate(self) -> ValidationResult:
        """Validate URL."""
        try:
            result = urlparse(self.url)
            
            if not all([result.scheme, result.netloc]):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid URL format"
                )
            
            if result.scheme not in self.allowed_schemes:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid scheme. Allowed: {', '.join(self.allowed_schemes)}"
                )
            
            return ValidationResult(
                is_valid=True,
                details={"parsed_url": result._asdict()}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=str(e)
            )

class CodeValidator(BaseModel):
    """Python code validation configuration."""
    code: str = Field(..., description="Code to validate")
    mode: str = Field(
        default="exec",
        description="Compilation mode"
    )
    check_syntax_only: bool = Field(
        default=True,
        description="Only check syntax without executing"
    )

    def validate(self) -> ValidationResult:
        """Validate Python code."""
        try:
            if self.check_syntax_only:
                ast.parse(self.code)
            else:
                compile(self.code, '<string>', self.mode)
            
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=str(e)
            )

class MathValidator(BaseModel):
    """Mathematical expression validation configuration."""
    expression: str = Field(..., description="Expression to validate")
    allowed_operators: List[str] = Field(
        default=["+", "-", "*", "/", "^", "**", "(", ")", ","],
        description="Allowed mathematical operators"
    )
    allowed_functions: List[str] = Field(
        default=["abs", "round", "pow", "sqrt", "compound", "simple"],
        description="Allowed mathematical functions"
    )

    def validate(self) -> ValidationResult:
        """Validate mathematical expression."""
        # Remove whitespace
        cleaned = self.expression.replace(" ", "")
        
        # Extract function calls
        function_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\('
        functions_used = re.findall(function_pattern, cleaned)
        
        # Validate functions
        invalid_functions = [f for f in functions_used if f not in self.allowed_functions]
        if invalid_functions:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid functions: {', '.join(invalid_functions)}",
                details={"invalid_functions": invalid_functions}
            )
        
        # Create set of valid characters
        valid_chars = set('0123456789.,_ ' + ''.join(self.allowed_operators) + 
                         ''.join([c for f in self.allowed_functions for c in f]))
        
        # Check for invalid characters
        invalid_chars = set(cleaned) - valid_chars
        if invalid_chars:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid characters: {', '.join(invalid_chars)}",
                details={"invalid_chars": list(invalid_chars)}
            )
        
        # Check for balanced parentheses
        if cleaned.count('(') != cleaned.count(')'):
            return ValidationResult(
                is_valid=False,
                error_message="Unbalanced parentheses",
                details={"open_count": cleaned.count('('), "close_count": cleaned.count(')')}
            )
        
        # All validations passed
        return ValidationResult(is_valid=True)

class APIKeyValidator(BaseModel):
    """API key validation configuration."""
    api_key: str = Field(..., description="API key to validate")
    provider: str = Field(..., description="API provider")
    
    @validator("provider")
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        valid_providers = {"openai", "serpapi", "github"}
        if v.lower() not in valid_providers:
            raise ValueError(f"Unsupported provider. Valid providers: {', '.join(valid_providers)}")
        return v.lower()

    def validate(self) -> ValidationResult:
        """Validate API key format."""
        patterns = {
            "openai": r"^sk-[A-Za-z0-9]{32,}$",
            "serpapi": r"^[A-Za-z0-9]{32,}$",
            "github": r"^gh[ps]_[A-Za-z0-9]{36,}$"
        }
        
        pattern = patterns.get(self.provider)
        if not pattern:
            return ValidationResult(
                is_valid=False,
                error_message=f"No validation pattern for provider: {self.provider}"
            )
        
        if not re.match(pattern, self.api_key):
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid {self.provider} API key format"
            )
        
        return ValidationResult(is_valid=True)

class SearchQueryValidator(BaseModel):
    """Search query validation configuration."""
    query: str = Field(..., description="Query to validate")
    min_length: int = Field(
        default=3,
        description="Minimum query length",
        ge=1
    )
    max_length: int = Field(
        default=1000,
        description="Maximum query length",
        le=5000
    )
    disallowed_patterns: List[str] = Field(
        default=["^\\s*$", "^[\\W_]+$"],
        description="Regex patterns for invalid queries"
    )

    def validate(self) -> ValidationResult:
        """Validate search query."""
        # Check length
        if len(self.query) < self.min_length:
            return ValidationResult(
                is_valid=False,
                error_message=f"Query too short (minimum {self.min_length} characters)"
            )
        
        if len(self.query) > self.max_length:
            return ValidationResult(
                is_valid=False,
                error_message=f"Query too long (maximum {self.max_length} characters)"
            )
        
        # Check against disallowed patterns
        for pattern in self.disallowed_patterns:
            if re.match(pattern, self.query):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid query format"
                )
        
        return ValidationResult(is_valid=True)


# Convenience functions for backward compatibility
def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate URL format."""
    result = URLValidator(url=url).validate()
    return result.is_valid, result.error_message

def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
    """Validate Python code syntax."""
    result = CodeValidator(code=code).validate()
    return result.is_valid, result.error_message

def validate_math_expression(expression: str) -> ValidationResult:
    """Validate mathematical expression."""
    return MathValidator(expression=expression).validate()

def validate_api_key(api_key: str, provider: str) -> Tuple[bool, Optional[str]]:
    """Validate API key format."""
    result = APIKeyValidator(api_key=api_key, provider=provider).validate()
    return result.is_valid, result.error_message

def validate_search_query(
    query: str,
    min_length: int = 3
) -> Tuple[bool, Optional[str]]:
    """Validate search query."""
    result = SearchQueryValidator(
        query=query,
        min_length=min_length
    ).validate()
    return result.is_valid, result.error_message


# Example usage
if __name__ == "__main__":
    # Test URL validation
    urls = [
        "https://www.example.com",
        "not_a_url",
        "ftp://invalid.scheme"
    ]
    
    print("\nTesting URL validation:")
    for url in urls:
        result = URLValidator(url=url).validate()
        print(f"\nURL: {url}")
        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Error: {result.error_message}")
    
    # Test code validation
    code_samples = [
        "print('Hello, World!')",
        "if True print('Invalid')",
        "def func():\n    return 42"
    ]
    
    print("\nTesting code validation:")
    for code in code_samples:
        result = CodeValidator(code=code).validate()
        print(f"\nCode: {code}")
        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Error: {result.error_message}")
    
    # Test math validation
    expressions = [
        "2 + 2",
        "3 * (4 + 5",
        "1 + @ + 2"
    ]
    
    print("\nTesting math validation:")
    for expr in expressions:
        result = MathValidator(expression=expr).validate()
        print(f"\nExpression: {expr}")
        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Error: {result.error_message}")
            if result.details:
                print(f"Details: {result.details}")
    
    # Test API key validation
    api_keys = [
        ("sk-abcd1234", "openai"),
        ("invalid_key", "serpapi"),
        ("ghs_abcdef", "github")
    ]
    
    print("\nTesting API key validation:")
    for key, provider in api_keys:
        result = APIKeyValidator(api_key=key, provider=provider).validate()
        print(f"\nProvider: {provider}")
        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Error: {result.error_message}")
    
    # Test search query validation
    queries = [
        "artificial intelligence",
        "a",
        "   ",
        "!" * 1001
    ]
    
    print("\nTesting search query validation:")
    for query in queries:
        result = SearchQueryValidator(query=query).validate()
        print(f"\nQuery: {query}")
        print(f"Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"Error: {result.error_message}")