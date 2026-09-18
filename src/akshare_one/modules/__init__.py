"""Data domains.

Importing this package imports every domain package, and each domain imports
its providers, whose ``@provider`` decorators populate
:mod:`akshare_one.modules.registry`. Importing :mod:`akshare_one` therefore
registers every provider before any public function runs; there is no other
place that builds a registry.
"""

from . import (
    financial,
    futures,
    historical,
    info,
    insider,
    news,
    options,
    realtime,
    registry,
)

__all__ = [
    "financial",
    "futures",
    "historical",
    "info",
    "insider",
    "news",
    "options",
    "realtime",
    "registry",
]
