from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, Literal, TypeAlias, Union

from .builtins import F, SingleOrArr, SingleOrArrOpt
from .supports import SupportsString

__all__ = [
    'MissingT', 'MISSING',

    'FuncExceptT',

    'DataType',

    'StrArr', 'StrArrOpt',

    'PassthroughC'
]


class MissingTBase(Enum):
    MissingT = auto()


MissingT: TypeAlias = Literal[MissingTBase.MissingT]
MISSING = MissingTBase.MissingT

DataType = Union[str, bytes, bytearray, SupportsString]

FuncExceptT = str | Callable[..., Any] | tuple[Callable[..., Any] | str, str]
"""
This type is used in specific functions that can throw an exception.
```
def can_throw(..., *, func: FuncExceptT) -> None:
    ...
    if some_error:
        raise CustomValueError('Some error occurred!!', func)

def some_func() -> None:
    ...
    can_throw(..., func=some_func)
```
If an error occurs, this will print a clear error ->\n
``ValueError: (some_func) Some error occurred!!``
"""


StrArr = SingleOrArr[SupportsString]
StrArrOpt = SingleOrArrOpt[SupportsString]

PassthroughC = Callable[[F], F]
