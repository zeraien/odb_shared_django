from .exceptions import LockfileExistsException
from .file_lock import Lockfile
from .redis_lock import RedisLock
from .cache_lock import CacheLock
from .monitor import Monitor

def lockfile_wait(name, raise_if_already_locked=True, timeout=60):
    # Bare decorator: @lockfile_wait -- although the first argument is called
    # `name_or_func`, it's actually the function being decorated.
    name_or_func = name
    if callable(name_or_func):
        data = [name_or_func.__module__,name_or_func.__name__]
        return Monitor(name=".".join(data),
                       raise_if_already_locked=raise_if_already_locked,
                       data=data,
                       timeout=timeout)(name_or_func)
    # Decorator: @lockfile_wait(...) or context manager: with lockfile_wait(...): ...
    else:
        return Monitor(name=name_or_func,
                       raise_if_already_locked=raise_if_already_locked,
                       data=[name_or_func],
                       timeout=timeout)

