from functools import wraps


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            return f"Encountered an error while processing request: {str(e)}.\n If the error is transient, please try again. Otherwise, please modify your query."
    return wrapper

