from .base import InsiderDataProvider
from .xueqiu import XueQiuInsider


class InsiderDataFactory:
    """
    Factory class for creating insider data providers
    """

    _providers = {
        "xueqiu": XueQiuInsider,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> InsiderDataProvider:  # type: ignore
        """
        Get an insider data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'xueqiu')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            InsiderDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown insider data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new insider data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class  # type: ignore
