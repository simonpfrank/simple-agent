"""
Logging filters for sensitive data masking and log verbosity control.

This module provides logging filters to:
1. Mask sensitive data (JWT tokens, API keys) in log messages
2. Control verbosity of third-party libraries (LiteLLM, OpenAI, etc.)
"""

import logging
import re
from typing import List, Tuple


class AzureIdentityFilter(logging.Filter):
    """
    Filter to suppress noisy Azure identity credential attempts.
    
    Azure DefaultAzureCredential tries multiple auth methods sequentially,
    logging failures for each unavailable method. These are expected and noisy.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Suppress Azure credential failure logs.
        
        Args:
            record: Log record to filter
            
        Returns:
            False to suppress, True to allow
        """
        # Suppress CredentialUnavailableError tracebacks (expected failures during auth chain)
        if record.exc_info:
            exc_type = record.exc_info[0]
            if exc_type and exc_type.__name__ == 'CredentialUnavailableError':
                return False  # Suppress this log
        
        # Suppress specific noisy messages
        noisy_patterns = [
            'failed: Failed to invoke PowerShell',
            'CredentialUnavailableError',
            'Enable debug logging for additional information',
        ]
        
        msg = str(record.msg)
        if any(pattern in msg for pattern in noisy_patterns):
            return False  # Suppress
        
        return True  # Allow other logs


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that masks sensitive data in log records.
    
    Prevents credential leakage by redacting:
    - Azure AD JWT tokens
    - API keys
    - Authentication tokens
    
    Usage:
        logger = logging.getLogger('my_logger')
        logger.addFilter(SensitiveDataFilter())
    """
    
    # Patterns to detect and redact (pattern, replacement)
    SENSITIVE_PATTERNS: List[Tuple[str, str]] = [
        # Azure AD tokens in extra_body dict
        (r"azure_ad_token['\"]:\s*['\"]eyJ[^'\"]+['\"]", "azure_ad_token': '***REDACTED***'"),
        # Azure AD tokens in plain text (ey****sg format in logs)
        (r"azure_ad_token['\"]:\s*['\"]?ey[A-Za-z0-9_\.\-]{10,}['\"]?", "azure_ad_token': 'ey****REDACTED'"),
        # Any JWT token (starts with eyJ, 100+ chars) - more aggressive
        (r"eyJ[A-Za-z0-9_\.\-]{100,}", "ey****REDACTED"),
        # Shorter JWT patterns (catch abbreviated logs)
        (r"ey[A-Za-z0-9_\.\-]{50,}", "ey****REDACTED"),
        # API keys in various formats
        (r"api_key['\"]:\s*['\"][^'\"]{20,}['\"]", "api_key': '***REDACTED***'"),
        # Bearer tokens
        (r"Bearer\s+[A-Za-z0-9_\-]{20,}", "Bearer ***REDACTED***"),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record by masking sensitive data.
        
        Args:
            record: Log record to filter
            
        Returns:
            True (always allow record through after masking)
        """
        # Mask sensitive data in message
        if hasattr(record, 'msg') and record.msg:
            msg = str(record.msg)
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                msg = re.sub(pattern, replacement, msg)
            record.msg = msg
        
        # Also check args tuple (used in formatted messages)
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, tuple):
                cleaned_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        for pattern, replacement in self.SENSITIVE_PATTERNS:
                            arg = re.sub(pattern, replacement, arg)
                    cleaned_args.append(arg)
                record.args = tuple(cleaned_args)
        
        return True


def configure_logging_filters():
    """
    Configure logging filters for the application.
    
    - Applies SensitiveDataFilter to all loggers
    - Reduces verbosity of third-party libraries (LiteLLM, OpenAI, etc.)
    - Respects the root logger's level (set by config or --debug flag)
    - Should be called once at application startup
    """
    # Apply sensitive data filter to root logger (affects all loggers)
    root_logger = logging.getLogger()
    root_logger.addFilter(SensitiveDataFilter())
    
    # Get root logger's level to respect user's debug setting
    root_level = root_logger.getEffectiveLevel()
    
    # Only suppress third-party libraries if we're NOT in DEBUG mode
    if root_level > logging.DEBUG:
        # Reduce verbosity of third-party libraries
        # These generate massive logs with HTTP headers, requests, etc.
        verbose_loggers = [
            'LiteLLM',
            'litellm',
            'openai',
            'httpcore',
            'httpx',
            'urllib3',
            'azure.identity',  # Suppress verbose Azure AD credential attempts
            'azure.core',      # Suppress Azure SDK HTTP logging
        ]
        
        for logger_name in verbose_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)  # Only show warnings and errors
            logger.addFilter(SensitiveDataFilter())
    
    # Always remove console handlers from third-party loggers to prevent console spam
    # They should only log to our file handler
    for logger_name in ['LiteLLM', 'litellm', 'openai', 'httpcore', 'httpx', 'urllib3', 'azure.identity', 'azure.core']:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.addFilter(SensitiveDataFilter())
        
        # Apply AzureIdentityFilter to azure.identity logger to suppress credential attempt noise
        if logger_name == 'azure.identity':
            lib_logger.addFilter(AzureIdentityFilter())
        
        # Remove any console/stream handlers to prevent duplicate console output
        lib_logger.handlers = [h for h in lib_logger.handlers if not isinstance(h, logging.StreamHandler)]
        lib_logger.propagate = True  # Let messages propagate to root (which goes to file only)
    
    # Don't override simple_agent logger level - let it inherit from root
    # This respects --debug flag and config settings


def mask_sensitive_string(text: str) -> str:
    """
    Utility function to mask sensitive data in a string.
    
    Useful for one-off masking without using the filter.
    
    Args:
        text: String potentially containing sensitive data
        
    Returns:
        String with sensitive data masked
    """
    for pattern, replacement in SensitiveDataFilter.SENSITIVE_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text
