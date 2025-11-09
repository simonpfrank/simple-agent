"""
Calculator tool for basic math operations.

Provides simple arithmetic operations for agents.
"""

import logging
from smolagents import tool

logger = logging.getLogger(__name__)


@tool
def add(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    logger.debug(f"[TOOL] add(a={a}, b={b})")
    result = a + b
    logger.debug(f"[TOOL] add() = {result}")
    return result


@tool
def subtract(a: float, b: float) -> float:
    """
    Subtract b from a.

    Args:
        a: Number to subtract from
        b: Number to subtract

    Returns:
        The difference a - b
    """
    logger.debug(f"[TOOL] subtract(a={a}, b={b})")
    result = a - b
    logger.debug(f"[TOOL] subtract() = {result}")
    return result


@tool
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        The product of a and b
    """
    logger.debug(f"[TOOL] multiply(a={a}, b={b})")
    result = a * b
    logger.debug(f"[TOOL] multiply() = {result}")
    return result


@tool
def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        The quotient a / b

    Raises:
        ValueError: If b is zero
    """
    logger.debug(f"[TOOL] divide(a={a}, b={b})")
    if b == 0:
        logger.error("[TOOL] divide() - Cannot divide by zero")
        raise ValueError("Cannot divide by zero")
    result = a / b
    logger.debug(f"[TOOL] divide() = {result}")
    return result
