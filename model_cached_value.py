import hashlib
import pickle
from functools import wraps

from django.core.cache import cache

def _get_key(instance):
    return '%s_%s' % (instance._meta.model_name, instance.pk)

def cached_value(func):
    """
    returns the value of the decorated method, but checks the cache first.

    Cache is based on the Django model instance of the decorated method,
    it will respect method args and kwargs.

    To reset cache, call `reset_cache_for_instance`; reset should be called whenever changes
    to the underlying model or related children/parents are made.

    Use the provided `reset_cache_signal` function.
    :param func:
    :return:
    """
    @wraps(func)
    def inner_func(self, *args, **kwargs):
        key = _get_key(self)
        data = cache.get(key,dict())

        pickled_args = pickle.dumps(args)
        pickled_kwargs = pickle.dumps(kwargs)
        arg_hash = '%s%s' % (hashlib.md5(pickled_args).hexdigest(), hashlib.md5(pickled_kwargs).hexdigest())
        value_key = '%s_%s' % (func.__name__, arg_hash)

        value = data.get(value_key)
        if value is None:
            value = data[value_key] = func(self, *args, **kwargs)
            cache.set(key, data, 120)
        return value
    return inner_func

def reset_cache_for_instance(instance):
    cache.delete(_get_key(instance))

def reset_cache_signal(sender, instance, *args, **kwargs):
    """
    use this in post_save signals to reset the cache for the instance that sent the signal.
    This might not be enough if you also need to update some children or other related objects.
    In such cases, make your own signal and call `reset_cache_for_instance`
    """
    reset_cache_for_instance(instance)
