import inspect
import functools


def patchtest_result(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        subject, result, reason = func(*args, **kwargs)
        if result == "PASS":
            return f"{result}: {func.__name__} on {subject}"
        else:
            return f"{result}: {func.__name__} on {subject} ({reason})"

    return wrapper
