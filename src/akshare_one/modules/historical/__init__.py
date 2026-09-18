"""Historical data domain. Importing it registers its providers."""

from .eastmoney import EastMoneyHistorical
from .eastmoney_direct import EastMoneyDirectHistorical
from .sina import SinaHistorical

__all__ = ["EastMoneyHistorical", "EastMoneyDirectHistorical", "SinaHistorical"]
