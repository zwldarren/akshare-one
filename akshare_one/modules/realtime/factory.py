from .eastmoney import EastmoneyRealtime
from .xueqiu import XueQiuRealtime
from .base import RealtimeDataProvider


class RealtimeDataFactory:
    """
    Factory class for creating realtime data providers
    """

    _providers = {
        "eastmoney": EastmoneyRealtime,
        "xueqiu": XueQiuRealtime,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> RealtimeDataProvider:
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

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a new realtime data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
