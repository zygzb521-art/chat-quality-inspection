from typing import Type
from .base import BaseConnector

_registry: dict[str, Type[BaseConnector]] = {}


def register_connector(platform: str):
    """Decorator to register a connector class for a given platform code."""
    def wrapper(cls):
        if not issubclass(cls, BaseConnector):
            raise TypeError(f'{cls.__name__} must inherit from BaseConnector')
        _registry[platform] = cls
        return cls
    return wrapper


def get_connector(platform: str, config: dict) -> BaseConnector:
    """Factory: instantiate the registered connector for *platform* with *config*."""
    cls = _registry.get(platform)
    if cls is None:
        raise KeyError(f'No connector registered for platform "{platform}". '
                       f'Available: {list(_registry.keys())}')
    return cls(config)


def list_registered() -> list[str]:
    return list(_registry.keys())