from __future__ import annotations

from typing import Any, Callable, Concatenate, overload

from ..exceptions import CustomRuntimeError
from ..types import MISSING, KwargsT, MissingT, P, R, T

__all__ = [
    'iterate', 'fallback', 'kwargs_fallback'
]


def iterate(
    base: T, function: Callable[Concatenate[T | R, P], R],
    count: int, *args: P.args, **kwargs: P.kwargs
) -> T | R:
    """
    Execute a given function over the base value multiple times.

    Different from regular iteration functions is that you do not need to pass a partial object.
    This function accepts *args and **kwargs. These will be passed on to the given function.

    Examples:

    >>> iterate(5, lambda x: x * 2, 2)
        20

    :param base:        Base value, etc. to iterate over.
    :param function:    Function to iterate over the base.
    :param count:       Number of times to execute function.
    :param *args:       Positional arguments to pass to the given function.
    :param **kwargs:    Keyword arguments to pass to the given function.

    :return:            Value, etc. with the given function run over it
                        *n* amount of times based on the given count.
    """

    if count <= 0:
        return base

    result: T | R = base

    for _ in range(count):
        result = function(result, *args, **kwargs)

    return result


fallback_missing = object()


@overload
def fallback(value: T | None, fallback: T, /) -> T:
    ...


@overload
def fallback(value: T | None, fallback0: T | None, default: T, /) -> T:
    ...


@overload
def fallback(value: T | None, fallback0: T | None, fallback1: T | None, default: T, /) -> T:
    ...


@overload
def fallback(value: T | None, *fallbacks: T | None) -> T | MissingT:
    ...


@overload
def fallback(value: T | None, *fallbacks: T | None, default: T) -> T:
    ...


def fallback(value: T | None, *fallbacks: T | None, default: Any | T = fallback_missing) -> T | MissingT:
    """
    Utility function that returns a value or a fallback if the value is None.

    Example:

    .. code-block:: python

        >>> fallback(5, 6)
        5
        >>> fallback(None, 6)
        6

    :param value:               Input value to evaluate. Can be None.
    :param fallback_value:      Value to return if the input value is None.

    :return:                    Input value or fallback value if input value is None.
    """

    if value is not None:
        return value

    for fallback in fallbacks:
        if fallback is not None:
            return fallback

    if default is not fallback_missing:
        return default
    elif len(fallbacks) > 3:
        return MISSING

    raise CustomRuntimeError('You need to specify a default/fallback value!')


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback0: T | None, default: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], fallback0: T | None, fallback1: T | None,
    default: T
) -> T:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None
) -> T | MissingT:
    ...


@overload
def kwargs_fallback(
    input_value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None, default: T
) -> T:
    ...


def kwargs_fallback(  # type: ignore
    value: T | None, kwargs: tuple[KwargsT, str], *fallbacks: T | None, default: T = fallback_missing  # type: ignore
) -> T | MissingT:
    """Utility function to return a fallback value from kwargs if value was not found or is None."""

    return fallback(value, kwargs[0].get(kwargs[1], None), *fallbacks, default=default)
