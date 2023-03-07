def is_even(number: int) -> bool:
    return number % 2 == 0


def is_odd(number: int) -> bool:
    return number % 2 == 1


def format_percentage(percentage: float) -> str:
    return format(percentage * 100, '.3f')
