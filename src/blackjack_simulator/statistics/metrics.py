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

    def merge(self, other: "RunningVariance") -> None:
        if other.count == 0:
            return
        if self.count == 0:
            self.count = other.count
            self.mean = other.mean
            self._m2 = other._m2
            return

        total_count = self.count + other.count
        delta = other.mean - self.mean
        self._m2 += other._m2 + (
            delta * delta * Decimal(self.count) * Decimal(other.count)
        ) / Decimal(total_count)
        self.mean += delta * Decimal(other.count) / Decimal(total_count)
        self.count = total_count

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
