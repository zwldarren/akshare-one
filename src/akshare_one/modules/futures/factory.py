from typing import Any

from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider
from .sina import SinaFuturesHistorical, SinaFuturesRealtime


class FuturesDataFactory:
    """Factory class for creating futures data providers"""

    _historical_providers: dict[str, type[HistoricalFuturesDataProvider]] = {
        "sina": SinaFuturesHistorical,
    }

    _realtime_providers: dict[str, type[RealtimeFuturesDataProvider]] = {
        "sina": SinaFuturesRealtime,
    }

    @classmethod
    def get_historical_provider(
        cls, provider_name: str, **kwargs: Any
    ) -> HistoricalFuturesDataProvider:
        """Get a historical futures data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'sina')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            HistoricalFuturesDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._historical_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown historical futures data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def get_realtime_provider(
        cls, provider_name: str, **kwargs: Any
    ) -> RealtimeFuturesDataProvider:
        """Get a realtime futures data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'sina')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            RealtimeFuturesDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._realtime_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown realtime futures data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_historical_provider(
        cls, name: str, provider_class: type[HistoricalFuturesDataProvider]
    ) -> None:
        """Register a new historical futures data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._historical_providers[name.lower()] = provider_class

    @classmethod
    def register_realtime_provider(
        cls, name: str, provider_class: type[RealtimeFuturesDataProvider]
    ) -> None:
        """Register a new realtime futures data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._realtime_providers[name.lower()] = provider_class
