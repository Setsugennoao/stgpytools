from __future__ import annotations

from .base import CustomKeyError

__all__ = [
    'NotFoundEnumValue'
]


class NotFoundEnumValue(CustomKeyError):
    """Raised when you try to instantiate an Enum with unknown value"""
