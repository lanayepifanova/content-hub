"""
Minimal Click stub for offline development.
"""

from __future__ import annotations

from typing import Any, Callable


def command(*args: Any, **kwargs: Any) -> Callable:
    def decorator(func: Callable) -> Callable:
        return func

    return decorator


def option(*_args: Any, **_kwargs: Any) -> Callable:
    def decorator(func: Callable) -> Callable:
        return func

    return decorator


class Context:
    pass


__all__ = ["command", "option", "Context"]
