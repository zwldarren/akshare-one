"""News data domain. Importing it registers its providers."""

from .eastmoney import EastMoneyNews
from .ths import ThsNews

__all__ = ["EastMoneyNews", "ThsNews"]
