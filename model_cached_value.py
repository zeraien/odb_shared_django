from functools import wraps

from django.core.cache import cache

def _get_key(instance):
    return '%s_%s' % (instance._meta.model_name, instance.pk)

def cached_value(func):
    """
    returns the value of the decorated method, but checks the cache first.
    Cache is based on the Django model instance of the decorated method.
    To reset cache, call `reset_cache_for_instance`; reset should be called whenever changes
    to the underlying model or related children/parents are made.

    Use the provided `reset_cache_signal` function.
    :param func:
    :return:
    """
    @wraps(func)
    def inner_func(self, *args, **kwargs):
        value_key = func.__name__
        key = _get_key(self)
        data = cache.get(key,dict())
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
