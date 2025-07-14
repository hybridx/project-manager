"""
Centralized error handling for the AI processor service.
Eliminates DRY violations and provides consistent error management.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from .interfaces import ErrorHandler


logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    
    def __init__(self, message: str, error_type: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)


class AIError(ProcessingError):
    """Custom exception for AI-related errors"""
    
    def __init__(self, message: str, model: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AI_ERROR", context)
        self.model = model


class DatabaseError(ProcessingError):
    """Custom exception for database-related errors"""
    
    def __init__(self, message: str, operation: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", context)
        self.operation = operation


class AppErrorHandler(ErrorHandler):
    """Concrete implementation of error handler"""
    
    def __init__(self):
        self.error_count = 0
        self.last_error_time = None
    
    async def handle_processing_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle processing errors with consistent logging and tracking"""
        self._update_error_stats()
        
        error_details = {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_count": self.error_count
        }
        
        logger.error(f"Processing error occurred: {error_details}")
        
        # Here you could add additional error handling logic like:
        # - Sending to error monitoring service
        # - Triggering alerts
        # - Saving to error database
        
        if isinstance(error, ProcessingError):
            await self._handle_custom_error(error, error_details)
    
    async def handle_ai_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle AI-related errors"""
        self._update_error_stats()
        
        error_details = {
            "error_type": "AI_ERROR",
            "message": str(error),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": context.get("model", "unknown"),
            "prompt_length": len(context.get("prompt", "")),
            "error_count": self.error_count
        }
        
        logger.error(f"AI error occurred: {error_details}")
        
        # Specific AI error handling
        if "timeout" in str(error).lower():
            logger.warning("AI request timed out - consider reducing prompt size or increasing timeout")
        elif "rate limit" in str(error).lower():
            logger.warning("AI rate limit exceeded - implementing backoff strategy")
    
    async def handle_database_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle database-related errors"""
        self._update_error_stats()
        
        error_details = {
            "error_type": "DATABASE_ERROR",
            "message": str(error),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": context.get("operation", "unknown"),
            "error_count": self.error_count
        }
        
        logger.error(f"Database error occurred: {error_details}")
        
        # Database-specific error handling
        if "connection" in str(error).lower():
            logger.warning("Database connection issue - check connection string and network")
        elif "timeout" in str(error).lower():
            logger.warning("Database timeout - consider optimizing query or increasing timeout")
    
    def _update_error_stats(self) -> None:
        """Update error statistics"""
        self.error_count += 1
        self.last_error_time = datetime.now(timezone.utc)
    
    async def _handle_custom_error(self, error: ProcessingError, error_details: Dict[str, Any]) -> None:
        """Handle custom processing errors"""
        logger.error(f"Custom error: {error.error_type} - {error_details}")
        
        # Add custom error handling logic here
        # For example, retry logic, fallback mechanisms, etc.
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None
        }
    
    def reset_error_stats(self) -> None:
        """Reset error statistics"""
        self.error_count = 0
        self.last_error_time = None


# Global error handler instance
error_handler = AppErrorHandler()


# Decorator for consistent error handling
def handle_errors(error_type: str = "processing"):
    """Decorator for consistent error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                if error_type == "ai":
                    await error_handler.handle_ai_error(e, context)
                elif error_type == "database":
                    await error_handler.handle_database_error(e, context)
                else:
                    await error_handler.handle_processing_error(e, context)
                
                raise
        return wrapper
    return decorator 