from functools import wraps
from threading import Lock


def singleton(cls):
    """
    Decorator that turns a class into a singleton.
    Ensures that only one instance of the class is ever created.
    """

    instances = {}
    lock = Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance