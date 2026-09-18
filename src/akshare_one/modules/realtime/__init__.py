"""Realtime data domain. Importing it registers its providers."""

from .eastmoney import EastmoneyRealtime
from .eastmoney_direct import EastMoneyDirectRealtime
from .xueqiu import XueQiuRealtime

__all__ = [
    "EastMoneyDirectRealtime",
    "EastmoneyRealtime",
    "XueQiuRealtime",
]
