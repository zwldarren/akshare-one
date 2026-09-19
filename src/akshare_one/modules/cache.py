"""Cache seam.

This module owns the policy: which namespaces exist, how long each lives, and
the ``AKSHARE_ONE_CACHE_ENABLED`` switch. Providers only declare what their
cache key must contain, via ``CACHE_PARAMS`` on the domain's base class::

    class HistoricalDataProvider(ABC):
        CACHE_PARAMS = ("symbol", "interval", "start_date", "end_date", "adjust")

    class SinaHistorical(HistoricalDataProvider):
        @cached("hist_data")
        def get_hist_data(self) -> pd.DataFrame:
            ...

A key is ``(method, declared parameter values, call arguments)``, so neither a
constructor parameter that changes the answer nor a call argument can be
dropped from the key by accident: whatever the provider declares in
``CACHE_PARAMS`` is read off the instance, and everything passed to the call is
included. The wrapper is built once, at import, and preserves the wrapped
method's name and docstring.
"""

from __future__ import annotations

import functools
import inspect
import os
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from cachetools import TTLCache

P = ParamSpec("P")
R = TypeVar("R")

#: ``namespace -> (maxsize, ttl seconds)``. The only place cache policy lives.
NAMESPACES: dict[str, tuple[int, int]] = {
    "hist_data": (1000, 3600),
    "realtime": (500, 60),
    "news": (500, 3600),
    "financial": (500, 86400),
    "info": (500, 86400),
    "insider": (500, 86400),
    "futures_hist": (1000, 3600),
    "futures_contracts": (10, 86400),
    "futures_varieties": (10, 86400),
    "futures_realtime": (500, 60),
    "options_chain": (1000, 3600),
    "options_realtime": (500, 60),
}

_CACHES: dict[str, TTLCache[Any, Any]] = {
    name: TTLCache(maxsize=maxsize, ttl=ttl) for name, (maxsize, ttl) in NAMESPACES.items()
}

_TRUTHY = ("1", "true", "yes", "on")


def enabled() -> bool:
    """Whether caching is on, per ``AKSHARE_ONE_CACHE_ENABLED`` (default on)."""
    return os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in _TRUTHY


def clear(namespace: str | None = None) -> None:
    """Drop every entry in one namespace, or in all of them."""
    if namespace is None:
        for cache in _CACHES.values():
            cache.clear()
        return
    _CACHES[namespace].clear()


def cached(namespace: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Cache calls to the decorated method or function.

    Args:
        namespace: An entry of :data:`NAMESPACES`, resolved at import time.

    Returns:
        The decorator.

    Raises:
        KeyError: If the namespace is not declared in :data:`NAMESPACES` — at
            import, not on first call.
    """
    if namespace not in _CACHES:
        raise KeyError(f"Unknown cache namespace {namespace!r}; declared: {sorted(_CACHES)}")

    cache = _CACHES[namespace]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        takes_receiver = next(iter(inspect.signature(func).parameters), None) == "self"
        func_qualname = getattr(func, "__qualname__", repr(func))

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not enabled():
                return func(*args, **kwargs)

            key = (
                func_qualname,
                _declared_params(args) if takes_receiver else (),
                args[1:] if takes_receiver else args,
                tuple(sorted(kwargs.items())),
            )
            try:
                return cache[key]
            except KeyError:
                value = func(*args, **kwargs)
                cache[key] = value
                return value

        return wrapper

    return decorator


def _declared_params(args: tuple[Any, ...]) -> tuple[Any, ...]:
    """Read the values of the receiver's ``CACHE_PARAMS``, if it declares any."""
    if not args:
        return ()
    declared = getattr(type(args[0]), "CACHE_PARAMS", None)
    if declared is None:
        return ()
    return tuple(getattr(args[0], name) for name in declared)
