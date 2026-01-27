from typing import Any

from .base import OptionsDataProvider
from .sina import SinaOptionsProvider


class OptionsDataFactory:
    """Factory class for creating options data providers"""

    _providers: dict[str, type[OptionsDataProvider]] = {
        "sina": SinaOptionsProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs: Any) -> OptionsDataProvider:
        """Get an options data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'sina')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            OptionsDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown options data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type[OptionsDataProvider]) -> None:
        """Register a new options data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
