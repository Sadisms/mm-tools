import time
from functools import wraps


def rate_limit(
    seconds: int = 20,
    paths_to_check: list[tuple] = None
):
    """
    Asynchronous decorator to limit the rate at which a function can be called.

    Args:
        seconds (int): The minimum number of seconds required between calls with the same key. Defaults to 20.
        paths_to_check (list[tuple], optional): List of paths (as tuples) to check against the event.body to uniquely identify requests.
            Each tuple corresponds to a path of keys to traverse inside event.body, and the value found is appended to the rate limit key.
            Defaults to [('context', 'value')].

    Returns:
        function: The decorated async function that will be rate limited.

    Example:
        @rate_limit(seconds=10, paths_to_check=[('context', 'user_id')])
        async def handler(self, event):
            pass

    Notes:
        - Assumes the function receives an event as the second positional argument, and that event.body is a dict.
        - The rate limiting key is generated from the function name and values extracted from event.body using each tuple in paths_to_check.
        - If a call is made before `seconds` have elapsed since the last call with the same key, the function will not be executed.
    """
    if paths_to_check is None:
        paths_to_check = [('context', 'value')]

    def decorator(func):
        last_called = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = func.__name__
            event = args[1]

            for check in paths_to_check:
                c = event.body
                for k in check:
                    c = c.get(k)

                key += str(c)

            if last_called.get(key):
                elapsed = time.time() - last_called[key]
                left_to_wait = seconds - elapsed
                if left_to_wait > 0:
                    return

            last_called[key] = time.time()
            return await func(*args, **kwargs)

        return wrapper

    return decorator
