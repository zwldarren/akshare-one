from .base import InfoDataProvider
from .eastmoney import EastmoneyInfo


class InfoDataFactory:
    """
    Factory class for creating info data providers
    """

    _providers = {
        "eastmoney": EastmoneyInfo,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> InfoDataProvider:  # type: ignore
        """
        Get a info data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'eastmoney')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            InfoDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown info data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new info data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class  # type: ignore
