from .base import HistoricalDataProvider
from .eastmoney import EastMoneyHistorical
from .eastmoney_direct import EastMoneyDirectHistorical
from .sina import SinaHistorical


class HistoricalDataFactory:
    """
    Factory class for creating historical data providers
    """

    _providers = {
        "eastmoney": EastMoneyHistorical,
        "eastmoney_direct": EastMoneyDirectHistorical,
        "sina": SinaHistorical,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> HistoricalDataProvider:
        """
        Get a historical data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'eastmoney')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            HistoricalDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown historical data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a new historical data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
