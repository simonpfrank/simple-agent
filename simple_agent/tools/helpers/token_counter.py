"""Token counter utility for estimating text token usage."""
import tiktoken


def estimate_tokens(text: str) -> int:
    """
    Count the number of tokens in text using OpenAI's tiktoken tokenizer.

    Uses the cl100k_base encoding which is used by GPT-3.5 and GPT-4.

    Args:
        text: The text to count tokens for.

    Returns:
        Number of tokens.
    """
    if not text:
        return 0

    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        # Fallback if tiktoken fails
        return 0
