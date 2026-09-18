"""Futures data domain. Importing it registers its providers."""

from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .sina import SinaFuturesHistorical, SinaFuturesRealtime

__all__ = [
    "HistoricalFuturesDataProvider",
    "RealtimeFuturesDataProvider",
    "SinaFuturesHistorical",
    "SinaFuturesRealtime",
]
