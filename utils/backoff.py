from __future__ import annotations

import random


class Backoff:
    def __init__(self, base: float = 1.0, factor: float = 2.0, maximum: float = 60.0) -> None:
        self._base = base
        self._factor = factor
        self._maximum = maximum
        self._current = base

    def next_delay(self) -> float:
        delay = min(self._current, self._maximum)
        self._current = min(self._current * self._factor, self._maximum)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter

    def reset(self) -> None:
        self._current = self._base
