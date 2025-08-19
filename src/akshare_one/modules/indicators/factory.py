from .base import BaseIndicatorCalculator
from .simple import SimpleIndicatorCalculator

_calculators = {
    "simple": SimpleIndicatorCalculator,
}
TALIB_AVAILABLE = False
try:
    from .talib import TalibIndicatorCalculator

    _calculators["talib"] = TalibIndicatorCalculator  # type: ignore
    TALIB_AVAILABLE = True
except ImportError:
    # talib is optional
    pass


class IndicatorFactory:
    """Factory for indicator calculators"""

    @classmethod
    def get_calculator(cls, calculator_type: str = "talib") -> BaseIndicatorCalculator:
        """Get indicator calculator instance

        If talib is not installed, it will fall back to the simple implementation.
        """
        if calculator_type == "talib" and not TALIB_AVAILABLE:
            calculator_type = "simple"

        calculator_class = _calculators.get(calculator_type)
        if not calculator_class:
            raise ValueError(f"Unsupported calculator type: {calculator_type}")
        return calculator_class()
