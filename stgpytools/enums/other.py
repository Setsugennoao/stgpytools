from __future__ import annotations

from typing import TypeVar, overload

__all__ = [
    'Coordinate',
    'Position',
    'Size'
]


class Coordinate:
    """
    Positive set of (x, y) coordinates.

    :raises ValueError:     Negative values were passed.
    """

    x: int
    """Horizontal coordinate."""

    y: int
    """Vertical coordinate."""

    @overload
    def __init__(self: SelfCoord, other: tuple[int, int] | SelfCoord, /) -> None:
        ...

    @overload
    def __init__(self: SelfCoord, x: int, y: int, /) -> None:
        ...

    def __init__(self: SelfCoord, x_or_self: int | tuple[int, int] | SelfCoord, y: int | None = None, /) -> None:
        from ..exceptions import CustomValueError

        if isinstance(x_or_self, int):
            x = x_or_self
        else:
            x, y = x_or_self if isinstance(x_or_self, tuple) else (x_or_self.x, x_or_self.y)

        if y is None:
            raise CustomValueError("y coordinate must be defined!", self.__class__)

        if x < 0 or y < 0:
            raise CustomValueError("Values can't be negative!", self.__class__)

        self.x = x
        self.y = y


SelfCoord = TypeVar('SelfCoord', bound=Coordinate)


class Position(Coordinate):
    """Positive set of an (x,y) offset relative to the top left corner of an area."""


class Size(Coordinate):
    """Positive set of an (x,y), (horizontal,vertical), size of an area."""
