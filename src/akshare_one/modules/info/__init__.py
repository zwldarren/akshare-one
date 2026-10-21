"""Info data domain. Importing it registers its providers."""

from .eastmoney import EastmoneyInfo
from .ths import ThsInfo

__all__ = ["EastmoneyInfo", "ThsInfo"]
