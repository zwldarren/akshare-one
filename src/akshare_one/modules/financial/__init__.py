"""Financial data domain. Importing it registers its providers."""

from .eastmoney_direct import EastMoneyDirectFinancialReport
from .sina import SinaFinancialReport

__all__ = ["EastMoneyDirectFinancialReport", "SinaFinancialReport"]
