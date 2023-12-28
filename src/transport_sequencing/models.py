from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable


class Coords:
    def __init__(self, x: Decimal | float, y: Decimal | float) -> None:
        self.x = x if isinstance(x, Decimal) else Decimal(x)
        self.y = y if isinstance(y, Decimal) else Decimal(y)

    def __repr__(self) -> str:
        return f"{self.x:.6f}, {self.y:.6f}"

    def as_tuple(self) -> tuple[Decimal, Decimal]:
        return (self.x, self.y)


class Unit(str, Enum):
    MS = "m/s"
    KMH = "km/h"
    MPH = "mph"
    KG = "kg"
    TONS = "tons"
    LITER = "liter"
    GALLON = "gallons"


conversion_table: dict[
    tuple[Unit, Unit],
    tuple[Callable, float],
] = {
    (Unit.KMH, Unit.MS): (operator.truediv, 3.6),
    (Unit.KMH, Unit.MPH): (operator.truediv, 1.60934),
    (Unit.KMH, Unit.KMH): (operator.mul, 1),
    (Unit.MPH, Unit.KMH): (operator.mul, 1.60934),
    (Unit.MPH, Unit.MS): (operator.mul, 0.44704),
    (Unit.MPH, Unit.MPH): (operator.mul, 1),
    (Unit.MS, Unit.MPH): (operator.truediv, 0.44704),
    (Unit.MS, Unit.KMH): (operator.mul, 3.6),
    (Unit.MS, Unit.MS): (operator.mul, 1),
    (Unit.KG, Unit.TONS): (operator.truediv, 1000),
    (Unit.KG, Unit.KG): (operator.mul, 1),
    (Unit.TONS, Unit.KG): (operator.mul, 1000),
    (Unit.TONS, Unit.TONS): (operator.mul, 1),
    (Unit.GALLON, Unit.LITER): (operator.mul, 3.78541),
    (Unit.GALLON, Unit.GALLON): (operator.mul, 1),
    (Unit.LITER, Unit.GALLON): (operator.truediv, 3.78541),
    (Unit.LITER, Unit.LITER): (operator.mul, 1),
}


@dataclass
class Value(ABC):
    value: float
    unit: Unit

    @abstractmethod
    def convert_to(self, unit: Unit) -> tuple[Callable, float]:
        if not (self.unit, unit) in conversion_table:
            raise Exception(f"Cannot convert {self.unit} to {unit}")
        return conversion_table[(self.unit, unit)]

    def _have_same_unit(self, other) -> bool:
        return self.unit == other.unit

    def _assert_same_unit(self, other) -> None:
        if not self._have_same_unit(other):
            raise Exception("unit mismatch")

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"

    def __add__(self, other):
        self._assert_same_unit(other)
        return self.value + other.value

    def __sub__(self, other):
        self._assert_same_unit(other)
        return self.value - other.value

    def __gt__(self, other):
        self._assert_same_unit(other)
        return self.value > other.value

    def __ge__(self, other):
        self._assert_same_unit(other)
        return self.value >= other.value

    def __lt__(self, other):
        self._assert_same_unit(other)
        return self.value < other.value

    def __le__(self, other):
        self._assert_same_unit(other)
        return self.value <= other.value


_DEFAULT_SPEED_UNIT = Unit.KMH
_DEFAULT_PAYLOAD_UNIT = Unit.KG
_DEFAULT_FUEL_UNIT = Unit.LITER


@dataclass
class Speed(Value):
    value: float
    unit: Unit | None = None

    def __post_init__(self) -> None:
        if self.unit is None:
            self.unit = _DEFAULT_SPEED_UNIT

    def convert_to(self, unit: Unit) -> Speed:
        op, arg = super().convert_to(unit)
        return Speed(unit, op(self.value, arg))


@dataclass
class Payload(Value):
    value: float
    unit: Unit | None = None

    def __post_init__(self) -> None:
        if self.unit is None:
            self.unit = _DEFAULT_PAYLOAD_UNIT

    def convert_to(self, unit: Unit) -> Payload:
        op, arg = super().convert_to(unit)
        return Payload(unit, op(self.value, arg))


@dataclass
class Fuel(Value):
    value: float
    unit: Unit | None = None

    def __post_init__(self) -> None:
        if self.unit is None:
            self.unit = _DEFAULT_FUEL_UNIT

    def convert_to(self, unit: Unit) -> Fuel:
        op, arg = super().convert_to(unit)
        return Fuel(unit, op(self.value, arg))
