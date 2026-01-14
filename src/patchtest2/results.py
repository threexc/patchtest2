import inspect
import functools
from typing import Tuple, Any


def patchtest_result(func):
    """Decorator that formats test results consistently.

    Test functions must return a tuple of (subject, result, reason) where:
    - subject: str - The patch subject line
    - result: str - One of 'PASS', 'FAIL', or 'SKIP'
    - reason: str or None - Description of the result
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Validate return value
        if not isinstance(result, tuple):
            raise ValueError(
                f"Test {func.__name__} must return a tuple, got {type(result).__name__}"
            )

        if len(result) != 3:
            raise ValueError(
                f"Test {func.__name__} must return (subject, result, reason), "
                f"got {len(result)} values: {result}"
            )

        subject, test_result, reason = result

        # Validate result is one of the expected values
        if test_result not in ("PASS", "FAIL", "SKIP"):
            raise ValueError(
                f"Test {func.__name__} returned invalid result '{test_result}'. "
                f"Must be one of: PASS, FAIL, SKIP"
            )

        # Format output
        if test_result == "PASS":
            return f"{test_result}: {func.__name__} on {subject}"
        else:
            return f"{test_result}: {func.__name__} on {subject} ({reason})"

    return wrapper
