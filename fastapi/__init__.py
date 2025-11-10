"""
Minimal FastAPI stub used for local tooling tests.

This is NOT a full FastAPI implementation; replace with the real dependency
when network/package installation is available.
"""

from __future__ import annotations

from typing import Callable, List, Tuple


class FastAPI:
    def __init__(self) -> None:
        self.routes: List[Tuple[str, Callable]] = []

    def get(self, path: str) -> Callable[[Callable], Callable]:
        def decorator(func: Callable) -> Callable:
            self.routes.append((path, func))
            return func

        return decorator


__all__ = ["FastAPI"]
