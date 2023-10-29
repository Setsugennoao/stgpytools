from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any, Callable, ParamSpec, Sequence, SupportsFloat, SupportsIndex, TypeAlias, TypeVar, Union
)

__all__ = [
    'T', 'T0', 'T1', 'T2', 'T_contra',

    'F', 'F0', 'F1', 'F2',

    'P', 'P0', 'P1', 'P2',
    'R', 'R0', 'R1', 'R2', 'R_contra',

    'Nb',

    'StrictRange', 'SoftRange', 'SoftRangeN', 'SoftRangesN',

    'Self',

    'SingleOrArr', 'SingleOrArrOpt',
    'SingleOrSeq', 'SingleOrSeqOpt',

    'SimpleByteData', 'SimpleByteDataArray',
    'ByteData',

    'KwargsT'
]

Nb = TypeVar('Nb', float, int)

T = TypeVar('T')
T0 = TypeVar('T0')
T1 = TypeVar('T1')
T2 = TypeVar('T2')

F = TypeVar('F', bound=Callable[..., Any])
F0 = TypeVar('F0', bound=Callable[..., Any])
F1 = TypeVar('F1', bound=Callable[..., Any])
F2 = TypeVar('F2', bound=Callable[..., Any])

P = ParamSpec('P')
P0 = ParamSpec('P0')
P1 = ParamSpec('P1')
P2 = ParamSpec('P2')

R = TypeVar('R')
R0 = TypeVar('R0')
R1 = TypeVar('R1')
R2 = TypeVar('R2')

T_contra = TypeVar('T_contra', contravariant=True)
R_contra = TypeVar('R_contra', contravariant=True)

Self = TypeVar('Self')

StrictRange: TypeAlias = tuple[int, int]
SoftRange: TypeAlias = int | StrictRange | Sequence[int]

SoftRangeN: TypeAlias = int | tuple[int | None, int | None] | None

if TYPE_CHECKING:
    SoftRangesN: TypeAlias = Sequence[SoftRangeN]
else:
    SoftRangesN: TypeAlias = list[SoftRangeN]

SingleOrArr = Union[T, list[T]]
SingleOrSeq = Union[T, Sequence[T]]
SingleOrArrOpt = Union[SingleOrArr[T], None]
SingleOrSeqOpt = Union[SingleOrSeq[T], None]

SimpleByteData: TypeAlias = str | bytes | bytearray
SimpleByteDataArray = Union[SimpleByteData, Sequence[SimpleByteData]]

ByteData: TypeAlias = SupportsFloat | SupportsIndex | SimpleByteData | memoryview

KwargsT = dict[str, Any]
