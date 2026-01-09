
import time
import random
from functools import wraps

def retry_with_backoff(retries=10, initial_delay=5.0, backoff_factor=1.5):
    """
    Decorator for retrying a function with exponential backoff.
    Designed to handle Gemini 429 Quota errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    msg = str(e).lower()
                    # Check for 429 or quota errors
                    if "429" in msg or "quota" in msg:
                        # Sometimes the error message contains the suggested delay
                        # But simple exponential backoff usually handles it.
                        # Gemini free tier often resets every minute.
                        print(f"  [Rate Limit] Retrying in {delay:.1f}s... ({i+1}/{retries})")
                        time.sleep(delay + random.uniform(0, 1.0))
                        delay *= backoff_factor
                    else:
                        raise e # Raise other errors immediately
            
            print(f"  [Error] Max retries reached for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator
