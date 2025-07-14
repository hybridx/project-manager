"""
Configuration management for the AI processor service.
Centralizes all configuration settings and environment variables.
"""

import os
from typing import Dict, Any
from .interfaces import ConfigurationManager


class AppConfigurationManager(ConfigurationManager):
    """Concrete implementation of configuration manager"""
    
    def __init__(self):
        self._ai_model = os.getenv("AI_MODEL", "llama3.2:3b")
        self._ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ai-pm")
        self._processing_timeout = int(os.getenv("PROCESSING_TIMEOUT", "300"))
        self._max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self._ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self._story_point_scale = [1, 2, 3, 5, 8, 13, 21]
        
    def get_ai_model(self) -> str:
        """Get the AI model to use"""
        return self._ai_model
    
    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL"""
        return self._ollama_base_url
    
    def get_mongodb_uri(self) -> str:
        """Get MongoDB connection URI"""
        return self._mongodb_uri
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration"""
        return {
            "timeout": self._processing_timeout,
            "max_retries": self._max_retries,
            "ai_temperature": self._ai_temperature,
            "story_point_scale": self._story_point_scale,
            "ai_model": self._ai_model,
        }
    
    def get_ai_temperature(self) -> float:
        """Get AI temperature setting"""
        return self._ai_temperature
    
    def get_processing_timeout(self) -> int:
        """Get processing timeout in seconds"""
        return self._processing_timeout
    
    def get_max_retries(self) -> int:
        """Get maximum number of retries"""
        return self._max_retries
    
    def get_story_point_scale(self) -> list:
        """Get story point scale"""
        return self._story_point_scale.copy()


# Global configuration instance
config = AppConfigurationManager() 