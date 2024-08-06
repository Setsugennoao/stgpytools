from __future__ import annotations

from os import PathLike, listdir, path
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Literal, TypeAlias, Union

__all__ = [
    'FilePathType', 'FileDescriptor',
    'FileOpener',

    'OpenTextModeUpdating',
    'OpenTextModeWriting',
    'OpenTextModeReading',

    'OpenBinaryModeUpdating',
    'OpenBinaryModeWriting',
    'OpenBinaryModeReading',

    'OpenTextMode',
    'OpenBinaryMode',

    'SPath', 'SPathLike'
]

FileDescriptor: TypeAlias = int

FilePathType: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]

FileOpener: TypeAlias = Callable[[str, int], int]

OpenTextModeUpdating: TypeAlias = Literal[
    'r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw',
    'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx',
]
OpenTextModeWriting: TypeAlias = Literal[
    'w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx'
]
OpenTextModeReading: TypeAlias = Literal[
    'r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr'
]

OpenBinaryModeUpdating: TypeAlias = Literal[
    'rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw',
    'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'
]
OpenBinaryModeWriting: TypeAlias = Literal[
    'wb', 'bw', 'ab', 'ba', 'xb', 'bx'
]
OpenBinaryModeReading: TypeAlias = Literal[
    'rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'
]

OpenTextMode: TypeAlias = OpenTextModeUpdating | OpenTextModeWriting | OpenTextModeReading
OpenBinaryMode: TypeAlias = OpenBinaryModeUpdating | OpenBinaryModeReading | OpenBinaryModeWriting


class SPath(Path):
    """Modified version of pathlib.Path"""
    _flavour = type(Path())._flavour  # type: ignore

    if TYPE_CHECKING:
        def __new__(cls, *args: SPathLike, **kwargs: Any) -> SPath:
            ...

    def format(self, *args: Any, **kwargs: Any) -> SPath:
        """Format the path with the given arguments."""

        return SPath(self.to_str().format(*args, **kwargs))

    def to_str(self) -> str:
        """Cast the path to a string."""

        return str(self)

    def get_folder(self) -> SPath:
        """Get the folder of the path."""

        folder_path = self.resolve()

        if folder_path.is_dir():
            return folder_path

        return SPath(path.dirname(folder_path))

    def mkdirp(self, mode: int = 0o777) -> None:
        """Make the dir path with its parents."""

        return self.get_folder().mkdir(mode, True, True)

    def rmdirs(self, missing_ok: bool = False, ignore_errors: bool = True) -> None:
        """Remove the dir path with its contents."""

        from shutil import rmtree

        try:
            return rmtree(str(self.get_folder()), ignore_errors)
        except FileNotFoundError:
            if not missing_ok:
                raise

    def read_lines(
        self, encoding: str | None = None, errors: str | None = None, keepends: bool = False
    ) -> list[str]:
        """Read the file and return its lines."""

        return super().read_text(encoding, errors).splitlines(keepends)

    def write_lines(
        self, data: Iterable[str], encoding: str | None = None,
        errors: str | None = None, newline: str | None = None
    ) -> int:
        """Open the file and write the given lines."""

        return super().write_text('\n'.join(data), encoding, errors, newline)

    def append_to_stem(self, suffixes: str | Iterable[str], sep: str = '_') -> SPath:
        """Append a suffix to the stem of the path"""

        from ..functions import to_arr

        return self.with_stem(sep.join([self.stem, *to_arr(suffixes)]))  # type:ignore[list-item]

    def move_dir(self, dst: SPath, *, mode: int = 0o777) -> None:
        dst.mkdir(mode, True, True)

        for file in listdir(self):
            src_file = self / file
            dst_file = dst / file

            print(file)
            print('moving', src_file, 'into', dst_file)

            if dst_file.exists():
                src_file.unlink()
            else:
                src_file.rename(dst_file)

        self.rmdir()


SPathLike = Union[str, Path, SPath]
