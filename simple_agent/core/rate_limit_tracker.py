"""
Rate limit tracking for Azure OpenAI API responses.

This module provides a LiteLLM callback to capture rate limit information
from API response headers without cluttering logs with Azure SDK verbosity.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RateLimitTracker:
    """
    Tracks rate limit information from Azure OpenAI API responses.

    This is a singleton that stores the latest rate limit info
    and can be accessed by SimpleAgent instances.
    """

    _instance: Optional["RateLimitTracker"] = None
    _initialized: bool = False

    def __new__(cls) -> "RateLimitTracker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self.tpm_limit: Optional[int] = None
        self.rpm_limit: Optional[int] = None
        self.tpm_remaining: Optional[int] = None
        self.rpm_remaining: Optional[int] = None
        self.last_model: Optional[str] = None
        self._initialized = True
    
    def update_from_response(self, response_obj: Any, model: str = "unknown") -> None:
        """
        Update rate limits from LiteLLM response object.

        Args:
            response_obj: LiteLLM/OpenAI response object with headers
            model: Model name for logging
        """
        try:
            # Try to access headers from response
            headers = None
            
            # LiteLLM response may have different structures
            if hasattr(response_obj, 'headers'):
                headers = response_obj.headers
            elif hasattr(response_obj, '_response') and hasattr(response_obj._response, 'headers'):
                headers = response_obj._response.headers
            
            if headers:
                # Extract Azure rate limit headers
                updated = False
                
                if 'x-ratelimit-limit-tokens' in headers:
                    self.tpm_limit = int(headers['x-ratelimit-limit-tokens'])
                    updated = True
                if 'x-ratelimit-limit-requests' in headers:
                    self.rpm_limit = int(headers['x-ratelimit-limit-requests'])
                    updated = True
                if 'x-ratelimit-remaining-tokens' in headers:
                    self.tpm_remaining = int(headers['x-ratelimit-remaining-tokens'])
                    updated = True
                if 'x-ratelimit-remaining-requests' in headers:
                    self.rpm_remaining = int(headers['x-ratelimit-remaining-requests'])
                    updated = True
                
                if updated:
                    self.last_model = model
                    
                    # Log rate limits at INFO level (visible even when Azure SDK is suppressed)
                    logger.info(
                        f"[RATE LIMITS] Model: {model} - "
                        f"TPM: {self.tpm_remaining}/{self.tpm_limit}, "
                        f"RPM: {self.rpm_remaining}/{self.rpm_limit}"
                    )
                    
                    # Warn if approaching limits
                    if self.tpm_remaining is not None and self.tpm_limit is not None:
                        tpm_percent = (self.tpm_remaining / self.tpm_limit) * 100
                        if tpm_percent < 10:
                            logger.warning(
                                f"[RATE LIMITS] Low token quota remaining: {self.tpm_remaining}/{self.tpm_limit} ({tpm_percent:.1f}%)"
                            )
        
        except Exception as e:
            logger.debug(f"Failed to extract rate limits: {e}")
    
    def get_limits_str(self) -> str:
        """
        Get formatted rate limit string.
        
        Returns:
            Formatted string with current rate limits, or fallback message
        """
        if self.tpm_limit is not None:
            return (
                f"TPM: {self.tpm_remaining}/{self.tpm_limit}, "
                f"RPM: {self.rpm_remaining}/{self.rpm_limit}"
            )
        else:
            return "Limit details not available - enable debug logging to see full error"


# Global singleton instance
rate_limit_tracker = RateLimitTracker()
