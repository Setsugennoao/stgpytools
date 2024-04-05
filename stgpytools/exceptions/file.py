from __future__ import annotations

from typing import Any

from ..types import FuncExceptT, SPath, SPathLike, SupportsString, FilePathType
from .base import CustomError, CustomPermissionError

__all__ = [
    'FileNotExistsError',
    'FileWasNotFoundError',
    'FilePermissionError',
    'FileTypeMismatchError',
    'FileIsADirectoryError'
]


class FileNotExistsError(CustomError, FileExistsError):
    """Raised when a file doesn't exists"""

    def __init__(
        self, func: FuncExceptT, file: SPathLike,
        message: SupportsString = "The file, '{file}', does not exist!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, SPath(file), **kwargs)


class FileWasNotFoundError(CustomError, FileNotFoundError):
    """Raised when a file wasn't found but the path is correct, e.g. parent directory exists"""

    def __init__(
        self, func: FuncExceptT, file: SPathLike,
        message: SupportsString = "Could not find the file, '{file}'!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, SPath(file), **kwargs)


class FilePermissionError(CustomPermissionError):
    """Raised when you try to access a file but haven't got permissions to do so"""

    def __init__(
        self, func: FuncExceptT, file: SPathLike,
        message: SupportsString = "Insufficient permissions to access the file, '{file}'!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, SPath(file), **kwargs)


class FileTypeMismatchError(CustomError, OSError):
    """Raised when you try to access a file with a FileType != AUTO and it's another file type"""

    def __init__(
        self, func: FuncExceptT, file: SPathLike,
        message: SupportsString = "The file type of '{file}' does not match the expected file type!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, SPath(file), **kwargs)


class FileIsADirectoryError(CustomError, IsADirectoryError):
    """Raised when you try to access a file but it's a directory instead"""

    def __init__(
        self, func: FuncExceptT, file: SPathLike,
        message: SupportsString = "The given path, '{file}', points to a directory!",
        **kwargs: Any
    ) -> None:
        super().__init__(message, func, SPath(file), **kwargs)
