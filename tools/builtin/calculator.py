"""
Calculator tool for basic math operations.

Provides simple arithmetic operations for agents.
"""

from smolagents import tool


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
    return a + b


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
    return a - b


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
    return a * b


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
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
