"""News data domain. Importing it registers its providers."""

from .eastmoney import EastMoneyNews

__all__ = ["EastMoneyNews"]
