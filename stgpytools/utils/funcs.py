from __future__ import annotations

from functools import update_wrapper
from types import FunctionType
from typing import Sequence

from ..types import F

__all__ = [
    'copy_func',
    'erase_module'
]


def copy_func(f: F) -> FunctionType:
    """Try copying a function."""

    try:
        g = FunctionType(
            f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__
        )
        g = update_wrapper(g, f)  # type: ignore
        g.__kwdefaults__ = f.__kwdefaults__
        return g
    except BaseException:  # for builtins
        return f  # type: ignore


def erase_module(func: F, modules: Sequence[str] | None = None) -> F:
    """Delete the __module__ of the function."""

    if hasattr(func, '__module__') and (True if modules is None else (func.__module__ in modules)):
        func.__module__ = None  # type: ignore

    return func
