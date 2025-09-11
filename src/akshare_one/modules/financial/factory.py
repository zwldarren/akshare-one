from .base import FinancialDataProvider
from .eastmoney_direct import EastMoneyDirectFinancialReport
from .sina import SinaFinancialReport


class FinancialDataFactory:
    """
    Factory class for creating financial data providers
    """

    _providers = {
        "sina": SinaFinancialReport,
        "eastmoney_direct": EastMoneyDirectFinancialReport,
    }

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs) -> FinancialDataProvider:  # type: ignore
        """
        Get a financial data provider by name

        Args:
            provider_name: Name of the provider (e.g., 'sina')
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            FinancialDataProvider: An instance of the requested provider

        Raises:
            ValueError: If the requested provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown financial data provider: {provider_name}")

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new financial data provider

        Args:
            name: Name to associate with this provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class  # type: ignore
