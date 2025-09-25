from .base import RealtimeDataProvider
from .eastmoney import EastmoneyRealtime
from .eastmoney_direct import EastMoneyDirectRealtime
from .xueqiu import XueQiuRealtime


class RealtimeDataFactory:
    """
    Factory class for creating realtime data providers
    """

    _providers: dict[str, type["RealtimeDataProvider"]] = {
        "eastmoney": EastmoneyRealtime,
        "xueqiu": XueQiuRealtime,
        "eastmoney_direct": EastMoneyDirectRealtime,
    }

    @classmethod
    def get_provider(
        cls, provider_name: str, **kwargs: object
    ) -> "RealtimeDataProvider":
        """
        Get a realtime data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'eastmoney')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            RealtimeDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown realtime data provider: {provider_name}")

        # Extract symbol from kwargs if present
        symbol = kwargs.get("symbol", "")
        if symbol is None:
            symbol = ""
        elif not isinstance(symbol, str):
            raise ValueError("symbol must be a string")

        return provider_class(symbol=symbol)

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new realtime data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
