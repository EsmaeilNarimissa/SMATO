"""API key management for the agent's tools."""

import os
import re
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class APIKeyConfig(BaseModel):
    """Configuration for API keys.
    
    Attributes:
        openai_api_key: Required OpenAI API key
        serpapi_api_key: Optional SerpAPI key for web search functionality
    """
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    serpapi_api_key: Optional[str] = Field(
        default=None,
        description="SerpAPI key (optional)"
    )

    @validator("openai_api_key")
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key format."""
        if not v:
            raise ValueError("OpenAI API key is required")
        # Updated pattern to accept project-specific keys
        if not re.match(r"^sk-(?:proj-)?[A-Za-z0-9_-]{32,}$", v):
            raise ValueError("Invalid OpenAI API key format")
        return v

    @validator("serpapi_api_key")
    def validate_serpapi_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate SerpAPI key format if provided."""
        if v is not None and not re.match(r"^[A-Za-z0-9]{32,}$", v):
            raise ValueError("Invalid SerpAPI key format")
        return v

    @classmethod
    def from_env(cls) -> "APIKeyConfig":
        """Create config from environment variables."""
        config = cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            serpapi_api_key=os.getenv("SERPAPI_API_KEY")
        )
        
        # Log warning if SerpAPI key is missing
        if config.serpapi_api_key is None:
            logger.warning("SerpAPI key not configured. Web search functionality will be limited.")
            
        return config

    def to_dict(self, mask: bool = True) -> Dict[str, Any]:
        """Convert config to dictionary, optionally masking key values.
        
        Args:
            mask: If True, mask key values for security
            
        Returns:
            Dictionary of configuration values
        """
        data = self.dict()
        if mask:
            for key in data:
                if data[key]:
                    data[key] = f"{data[key][:8]}...{data[key][-4:]}"
        return data


class APIKeyManager:
    """Manager for API keys.
    
    Handles:
    - API key validation
    - Key retrieval
    - Status reporting
    - Error logging
    """
    
    def __init__(self) -> None:
        """Initialize API key manager."""
        try:
            self.config = APIKeyConfig.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize API key manager: {e}")
            raise
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key.
        
        Returns:
            OpenAI API key
            
        Raises:
            ValueError: If key is not configured
        """
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return self.config.openai_api_key
    
    def get_serpapi_key(self) -> Optional[str]:
        """Get SerpAPI key with warning if not configured.
        
        Returns:
            SerpAPI key if configured, None otherwise
        """
        if self.config.serpapi_api_key is None:
            logger.warning("SerpAPI key not configured. Web search functionality will be limited.")
        return self.config.serpapi_api_key
    
    def validate_api_keys(self) -> bool:
        """Validate all API keys.
        
        Returns:
            True if all required keys are valid
        """
        try:
            # Validate OpenAI key
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required")
            
            # SerpAPI key is optional but validate if present
            if self.config.serpapi_api_key:
                self.config.validate_serpapi_key(self.config.serpapi_api_key)
            
            return True
            
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of all API keys.
        
        Returns:
            Dictionary with key status
        """
        return {
            "openai": bool(self.config.openai_api_key),
            "serpapi": bool(self.config.serpapi_api_key)
        }


# Create global API key manager instance
api_keys = APIKeyManager()

def get_openai_api_key() -> str:
    """Convenience function to get OpenAI API key."""
    return api_keys.get_openai_api_key()

def get_serpapi_key() -> Optional[str]:
    """Convenience function to get SerpAPI key."""
    return api_keys.get_serpapi_key()

def validate_api_keys() -> bool:
    """Convenience function to validate API keys."""
    return api_keys.validate_api_keys()


# Example usage
if __name__ == "__main__":
    # Test API key validation
    try:
        if api_keys.validate_api_keys():
            print("API keys validated successfully")
            print("Status:", api_keys.get_status())
            print("Keys:", api_keys.config.to_dict(mask=True))
    except Exception as e:
        print(f"Error validating API keys: {e}")