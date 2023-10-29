from __future__ import annotations

from itertools import chain, zip_longest
from typing import Iterable, overload

from ..exceptions import CustomIndexError
from ..types import T0, T

__all__ = [
    'ranges_product',

    'interleave_arr'
]


@overload
def ranges_product(range0: range | int, range1: range | int, /) -> Iterable[tuple[int, int]]:
    ...


@overload
def ranges_product(range0: range | int, range1: range | int, range2: range | int, /) -> Iterable[tuple[int, int, int]]:
    ...


def ranges_product(*_iterables: range | int) -> Iterable[tuple[int, ...]]:
    """
    Take two or three lengths/ranges and make a cartesian product of them.

    Useful for getting all coordinates of an image.
    For example ranges_product(1920, 1080) will give you [(0, 0), (0, 1), (0, 2), ..., (1919, 1078), (1919, 1079)].
    """

    n_iterables = len(_iterables)

    if n_iterables <= 1:
        raise CustomIndexError(f'Not enough ranges passed! ({n_iterables})', ranges_product)

    iterables = [range(x) if isinstance(x, int) else x for x in _iterables]

    if n_iterables == 2:
        first_it, second_it = iterables

        for xx in first_it:
            for yy in second_it:
                yield xx, yy
    elif n_iterables == 3:
        first_it, second_it, third_it = iterables

        for xx in first_it:
            for yy in second_it:
                for zz in third_it:
                    yield xx, yy, zz
    else:
        raise CustomIndexError(f'Too many ranges passed! ({n_iterables})', ranges_product)


def interleave_arr(arr0: Iterable[T], arr1: Iterable[T0], n: int = 2) -> Iterable[T | T0]:
    """
    Interleave two arrays of variable length.

    :param arr0:    First array to be interleaved.
    :param arr1:    Second array to be interleaved.
    :param n:       The number of elements from arr0 to include in the interleaved sequence
                    before including an element from arr1.

    :yield:         Elements from either arr0 or arr01.
    """
    if n == 1:
        yield from (x for x in chain.from_iterable(zip_longest(arr0, arr1)) if x is not None)

        return

    arr0_i, arr1_i = iter(arr0), iter(arr1)
    arr1_vals = arr0_vals = True

    while arr1_vals or arr0_vals:
        if arr0_vals:
            for _ in range(n):
                try:
                    yield next(arr0_i)
                except StopIteration:
                    arr0_vals = False

        if arr1_vals:
            try:
                yield next(arr1_i)
            except StopIteration:
                arr1_vals = False
