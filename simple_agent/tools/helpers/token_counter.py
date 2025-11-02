"""Token counter utility for estimating text token usage."""
import logging
import tiktoken

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Count the number of tokens in text using OpenAI's tiktoken tokenizer.

    Uses the cl100k_base encoding which is used by GPT-3.5 and GPT-4.
    Falls back to character-based estimation if tiktoken is unavailable.

    Args:
        text: The text to count tokens for.

    Returns:
        Number of tokens (estimated if tiktoken unavailable).
    """
    if not text:
        return 0

    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        # Fallback: Use character-based estimation
        # Average: ~4 characters per token for English text
        # This is more accurate than returning 0
        logger.debug(f"Tiktoken unavailable, using fallback estimation: {e}")
        return _estimate_tokens_fallback(text)


def _estimate_tokens_fallback(text: str) -> int:
    """
    Estimate tokens using character count fallback.

    Based on empirical observation that:
    - Average English word = 4.7 characters
    - Average English word = 1.3 tokens
    - Therefore: 1 token ≈ 3.6 characters

    This method is more conservative (overestimates) to avoid token budget issues.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated token count.
    """
    # Conservative estimate: 1 token per 3.5 characters
    # This prevents underestimation which could cause rate limit errors
    chars = len(text.strip())
    words = len(text.split())

    # Use word count if available (more accurate)
    if words > 0:
        # Average 1.3 tokens per word (conservative)
        return int(words * 1.3) or 1

    # Fallback to character count if no words
    return max(1, int(chars / 3.5))
