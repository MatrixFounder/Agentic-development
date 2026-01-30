def calculate(price: float, rate: float) -> float:
    """
    Calculates total price.

    Args:
        price (float): Base price.
        rate (float): Tax rate.

    Returns:
        float: Total price.
    """
    return price * (1 + rate)
