"""Provider registry.

A provider declares itself where it is defined::

    @provider("historical", "sina")
    class SinaHistorical(HistoricalDataProvider):
        ...

:mod:`akshare_one.modules` imports every domain package, and each domain
package imports its providers, so importing :mod:`akshare_one` populates this
registry before any public function runs. Nothing else builds a registry.

The registry is keyed by ``(domain, capability, source)``. ``capability``
exists because one domain can expose more than one provider interface: the
futures domain has separate historical and realtime providers.
"""

from __future__ import annotations

from typing import Any, TypeVar

_T = TypeVar("_T")

#: Capability used by domains that expose a single provider interface.
DEFAULT_CAPABILITY = "default"

_REGISTRY: dict[tuple[str, str, str], type[Any]] = {}


class UnknownProviderError(ValueError):
    """Raised when no provider is registered for a domain/source (or capability)."""


def provider(
    domain: str,
    source: str,
    capability: str = DEFAULT_CAPABILITY,
) -> Any:
    """Register a provider class for ``(domain, capability, source)``.

    Args:
        domain: Data domain, e.g. ``"historical"``.
        source: Upstream source name, e.g. ``"sina"``. Case-insensitive.
        capability: Which of the domain's provider interfaces this class
            implements; defaults to :data:`DEFAULT_CAPABILITY`.

    Returns:
        The class decorator.

    Raises:
        ValueError: If a *different* class is already registered under the same
            key, which would otherwise silently shadow a provider.
    """

    def register(cls: type[_T]) -> type[_T]:
        key = (domain, capability, source.lower())
        existing = _REGISTRY.get(key)
        if existing is not None and existing is not cls:
            raise ValueError(
                f"{existing.__name__} is already registered as "
                f"{domain}/{capability}/{source}; refusing to replace it with {cls.__name__}"
            )
        _REGISTRY[key] = cls
        return cls

    return register


def registered_sources(domain: str, capability: str = DEFAULT_CAPABILITY) -> tuple[str, ...]:
    """Sources registered for a domain and capability, sorted."""
    return tuple(
        sorted(source for (d, cap, source) in _REGISTRY if d == domain and cap == capability)
    )


def resolve(
    domain: str,
    source: str,
    capability: str = DEFAULT_CAPABILITY,
    **kwargs: Any,
) -> Any:
    """Instantiate the provider registered for a source.

    Args:
        domain: Data domain, e.g. ``"historical"``.
        source: Upstream source name, e.g. ``"sina"``. Case-insensitive.
        capability: Which of the domain's provider interfaces to resolve.
        **kwargs: Passed to the provider's constructor.

    Returns:
        A provider instance for that source.

    Raises:
        UnknownProviderError: If the domain/capability has no provider for the
            requested source. The message lists the registered ones.
    """
    provider_class = _REGISTRY.get((domain, capability, source.lower()))
    if provider_class is None:
        known = ", ".join(registered_sources(domain, capability)) or "none"
        raise UnknownProviderError(
            f"Unknown {domain} provider: {source!r} (known sources: {known})"
        )
    return provider_class(**kwargs)
