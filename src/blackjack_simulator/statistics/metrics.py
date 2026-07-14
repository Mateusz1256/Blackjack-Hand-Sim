"""Streaming metric helpers."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class RunningVariance:
    count: int = 0
    mean: Decimal = Decimal("0")
    _m2: Decimal = Decimal("0")

    def add(self, value: Decimal) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / Decimal(self.count)
        delta_after = value - self.mean
        self._m2 += delta * delta_after

    @property
    def sample_variance(self) -> Decimal:
        if self.count < 2:
            return Decimal("0")

        return self._m2 / Decimal(self.count - 1)

    @property
    def population_variance(self) -> Decimal:
        if self.count == 0:
            return Decimal("0")

        return self._m2 / Decimal(self.count)
