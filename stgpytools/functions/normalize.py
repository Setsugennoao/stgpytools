from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Iterator, Sequence, overload

from ..types import F, SupportsString, T, SoftRange, SoftRangeN, SoftRangesN, StrictRange

__all__ = [
    'normalize_seq',
    'to_arr',
    'flatten',
    'normalize_list_to_ranges',
    'normalize_ranges_to_list',
    'normalize_range',
    'normalize_ranges',
    'invert_ranges',
    'norm_func_name', 'norm_display_name'
]


@overload
def normalize_seq(val: Sequence[T], length: int) -> list[T]:
    ...


@overload
def normalize_seq(val: T | Sequence[T], length: int) -> list[T]:
    ...


def normalize_seq(val: T | Sequence[T], length: int) -> list[T]:
    """
    Normalize a sequence of values.

    :param val:     Input value.
    :param length:  Amount of items in the output.
                    If original sequence length is less that this,
                    the last item will be repeated.

    :return:        List of normalized values with a set amount of items.
    """

    val = to_arr(val)

    val += [val[-1]] * (length - len(val))

    return val[:length]


_iterables_t = (list, tuple, range, zip, set, map, enumerate)


@overload
def to_arr(val: list[T], *, sub: bool = False) -> list[T]:
    ...


@overload
def to_arr(val: T | Sequence[T], *, sub: bool = False) -> list[T]:
    ...


def to_arr(val: T | Sequence[T], *, sub: bool = False) -> list[T]:
    """Normalize any value into an iterable."""

    if sub:
        return list(val) if any(isinstance(val, x) for x in _iterables_t) else [val]  # type: ignore

    return list(val) if type(val) in _iterables_t else [val]  # type: ignore


@overload
def flatten(items: T | Iterable[T | Iterable[T | Iterable[T]]]) -> Iterable[T]:
    ...


@overload
def flatten(items: T | Iterable[T | Iterable[T]]) -> Iterable[T]:  # type: ignore
    ...


@overload
def flatten(items: T | Iterable[T]) -> Iterable[T]:  # type: ignore
    ...


def flatten(items: Any) -> Any:
    """Flatten an array of values."""

    for val in items:
        if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
            for sub_x in flatten(val):
                yield sub_x
        else:
            yield val


def normalize_range(ranges: SoftRange, /) -> Iterable[int]:
    """
    Normalize ranges represented by a tuple to an iterable of frame numbers.

    :param ranges:      Ranges to normalize.

    :return:            List of positive frame ranges.
    """

    if isinstance(ranges, int):
        return [ranges]

    if isinstance(ranges, tuple):
        start, stop = ranges
        step = -1 if stop < start else 1

        return range(start, stop + step, step)

    return ranges


def normalize_list_to_ranges(flist: Iterable[int], min_length: int = 0) -> list[StrictRange]:
    flist2 = list[list[int]]()
    flist3 = list[int]()

    prev_n = -1

    for n in sorted(set(flist)):
        if prev_n + 1 != n:
            if flist3:
                flist2.append(flist3)
                flist3 = []
        flist3.append(n)
        prev_n = n

    if flist3:
        flist2.append(flist3)

    flist4 = [i for i in flist2 if len(i) > min_length]

    return list(zip(
        [i[0] for i in flist4],
        [i[-1] for j, i in enumerate(flist4)]
    ))


def normalize_ranges_to_list(ranges: Iterable[SoftRange]) -> list[int]:
    out = list[int]()

    for srange in ranges:
        out.extend(normalize_range(srange))

    return out


def normalize_ranges(ranges: SoftRangeN | SoftRangesN, end: int) -> list[StrictRange]:
    """
    Normalize ranges to a list of positive ranges.

    Frame ranges can include None and negative values.
    None will be converted to either 0 if it's the first value in a SoftRange, or the end if it's the second item.
    Negative values will be subtracted from the end.

    Examples:

    .. code-block:: python

        >>> normalize_ranges((None, None), end=1000)
        [(0, 999)]
        >>> normalize_ranges((24, -24), end=1000)
        [(24, 975)]
        >>> normalize_ranges([(24, 100), (80, 150)], end=1000)
        [(24, 150)]


    :param clip:        Input clip.
    :param franges:     Frame range or list of frame ranges.

    :return:            List of positive frame ranges.
    """

    ranges = ranges if isinstance(ranges, list) else [ranges]  # type:ignore

    out = []

    for r in ranges:
        if r is None:
            r = (None, None)

        if isinstance(r, tuple):
            start, endd = r
            if start is None:
                start = 0
            if endd is None:
                endd = end - 1
        else:
            start = r
            endd = r

        if start < 0:
            start = end - 1 + start

        if endd < 0:
            endd = end - 1 + endd

        out.append((start, endd))

    return normalize_list_to_ranges([
        x for start, endd in out for x in range(start, endd + 1)
    ])


def invert_ranges(ranges: SoftRangeN | SoftRangesN, enda: int, endb: int | None) -> list[StrictRange]:
    norm_ranges = normalize_ranges(ranges, enda if endb is None else endb)

    b_frames = {*normalize_ranges_to_list(norm_ranges)}

    return normalize_list_to_ranges({*range(enda)} - b_frames)


def norm_func_name(func_name: SupportsString | F) -> str:
    """Normalize a class, function, or other object to obtain its name"""

    if isinstance(func_name, str):
        return func_name.strip()

    if not isinstance(func_name, type) and not callable(func_name):
        return str(func_name).strip()

    func = func_name

    if hasattr(func_name, '__name__'):
        func_name = func.__name__
    elif hasattr(func_name, '__qualname__'):
        func_name = func.__qualname__

    if callable(func):
        if hasattr(func, '__self__'):
            func = func.__self__ if isinstance(func.__self__, type) else func.__self__.__class__
            func_name = f'{func.__name__}.{func_name}'

    return str(func_name).strip()


def norm_display_name(obj: object) -> str:
    """Get a fancy name from any object."""

    if isinstance(obj, Iterator):
        return ', '.join(norm_display_name(v) for v in obj).strip()

    if isinstance(obj, Fraction):
        return f'{obj.numerator}/{obj.denominator}'

    if isinstance(obj, dict):
        return '(' + ', '.join(f'{k}={v}' for k, v in obj.items()) + ')'

    return norm_func_name(obj)
