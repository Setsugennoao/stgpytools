from __future__ import annotations

from functools import partial, wraps
from inspect import Signature
from inspect import _empty as empty_param
from inspect import isclass
from typing import (
    TYPE_CHECKING, Any, Callable, Concatenate, Generator, Generic, Iterable, Iterator, Mapping, NoReturn, Protocol,
    Sequence, TypeVar, cast, no_type_check, overload
)

from .builtins import F0, F1, P0, P1, R0, R1, T0, T1, T2, KwargsT, P, R, T

__all__ = [
    'copy_signature',

    'inject_self',

    'inject_kwargs_params',

    'complex_hash',

    'get_subclasses',

    'classproperty', 'cachedproperty',

    'KwargsNotNone',

    'Singleton', 'to_singleton',

    'LinearRangeLut'
]


class copy_signature(Generic[F0]):
    """
    Type util to copy the signature of one function to another function.\n
    Especially useful for passthrough functions.

    .. code-block::

       class SomeClass:
           def __init__(
               self, some: Any, complex: Any, /, *args: Any,
               long: Any, signature: Any, **kwargs: Any
           ) -> None:
               ...

       class SomeClassChild(SomeClass):
           @copy_signature(SomeClass.__init__)
           def __init__(*args: Any, **kwargs: Any) -> None:
               super().__init__(*args, **kwargs)
               # do some other thing

       class Example(SomeClass):
           @copy_signature(SomeClass.__init__)
           def __init__(*args: Any, **kwargs: Any) -> None:
               super().__init__(*args, **kwargs)
               # another thing
    """

    def __init__(self, target: F0) -> None:
        """Copy the signature of ``target``."""

    def __call__(self, wrapped: Callable[..., Any]) -> F0:
        return cast(F0, wrapped)


class injected_self_func(Generic[T, P, R], Protocol):  # type: ignore[misc]
    @overload
    @staticmethod
    def __call__(*args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(self: T, _self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(cls: type[T], *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @overload
    @staticmethod
    def __call__(cls: type[T], _cls: type[T], *args: P.args, **kwargs: P.kwargs) -> R:
        ...

    @staticmethod
    def __call__(*args: Any, **kwds: Any) -> Any:
        ...


self_objects_cache = dict[type[T], T]()  # type: ignore


class inject_self_base(Generic[T, P, R]):
    def __init__(self, function: Callable[Concatenate[T, P], R], /, *, cache: bool = False) -> None:
        """
        Wrap ``function`` to always have a self provided to it.

        :param function:    Method to wrap.
        :param cache:       Whether to cache the self object.
        """

        self.cache = self.init_kwargs = None

        if isinstance(self, inject_self.cached):
            self.cache = True

        self.function = function

        self.signature = self.first_key = self.init_kwargs = None

        self.args = tuple[Any]()
        self.kwargs = dict[str, Any]()

        self.clean_kwargs = False

    def __get__(
        self, class_obj: type[T] | T | None, class_type: type[T] | type[type[T]]  # type: ignore
    ) -> injected_self_func[T, P, R]:
        if not self.signature or not self.first_key:  # type: ignore
            self.signature = Signature.from_callable(self.function, eval_str=True)  # type: ignore
            self.first_key = next(iter(list(self.signature.parameters.keys())), None)  # type: ignore

            if isinstance(self, inject_self.init_kwargs):
                from ..exceptions import CustomValueError

                if 4 not in {x.kind for x in self.signature.parameters.values()}:  # type: ignore
                    raise CustomValueError(
                        'This function hasn\'t got any kwargs!', 'inject_self.init_kwargs', self.function
                    )

                self.init_kwargs = list[str](  # type: ignore
                    k for k, x in self.signature.parameters.items() if x.kind != 4  # type: ignore
                )

        @wraps(self.function)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            first_arg = (args[0] if args else None) or (
                kwargs.get(self.first_key, None) if self.first_key else None  # type: ignore
            )

            if (
                first_arg and (
                    (is_obj := isinstance(first_arg, class_type))
                    or isinstance(first_arg, type(class_type))  # noqa
                    or first_arg is class_type  # noqa
                )
            ):
                obj = first_arg if is_obj else first_arg()
                if args:
                    args = args[1:]
                elif kwargs and self.first_key:
                    kwargs.pop(self.first_key)  # type: ignore
            elif class_obj is None:
                if self.cache:
                    if class_type not in self_objects_cache:
                        obj = self_objects_cache[class_type] = class_type(*self.args, **self.kwargs)
                    else:
                        obj = self_objects_cache[class_type]
                elif self.init_kwargs:
                    obj = class_type(  # type: ignore
                        *self.args, **(self.kwargs | {k: v for k, v in kwargs.items() if k not in self.init_kwargs})
                    )
                    if self.clean_kwargs:
                        kwargs = {k: v for k, v in kwargs.items() if k in self.init_kwargs}
                else:
                    obj = class_type(*self.args, **self.kwargs)
            else:
                obj = class_obj

            return self.function(obj, *args, **kwargs)

        return _wrapper

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.__get__(None, self)(*args, **kwargs)  # type: ignore

    @property
    def __signature__(self) -> Signature:
        return Signature.from_callable(self.function)

    @classmethod
    def with_args(
        cls, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[Concatenate[T0, P0], R0]], inject_self[T0, P0, R0]]:
        """Provide custom args to instantiate the ``self`` object with."""

        def _wrapper(function: Callable[Concatenate[T0, P0], R0]) -> inject_self[T0, P0, R0]:
            inj = cls(function)  # type: ignore
            inj.args = args
            inj.kwargs = kwargs
            return inj  # type: ignore
        return _wrapper


class inject_self(Generic[T, P, R], inject_self_base[T, P, R]):
    """Wrap a method so it always has a constructed ``self`` provided to it."""

    class cached(Generic[T0, P0, R0], inject_self_base[T0, P0, R0]):
        """
        Wrap a method so it always has a constructed ``self`` provided to it.
        Once ``self`` is constructed, it will be reused.
        """

        class property(Generic[T1, R1]):
            def __init__(self, function: Callable[[T1], R1]) -> None:
                self.function = inject_self(function)

            def __get__(
                self, class_obj: type[T1] | T1 | None, class_type: type[T1] | type[type[T1]]  # type: ignore
            ) -> R1:
                return self.function.__get__(class_obj, class_type)()

    class init_kwargs(Generic[T0, P0, R0], inject_self_base[T0, P0, R0]):
        """
        Wrap a method so it always has a constructed ``self`` provided to it.
        When constructed, kwargs to the function will be passed to the constructor.
        """

        @classmethod
        def clean(cls, function: Callable[Concatenate[T0, P0], R0]) -> inject_self[T0, P0, R0]:
            """Wrap a method, pass kwargs to the constructor and remove them from actual **kwargs."""
            inj = cls(function)
            inj.clean_kwargs = True
            return inj  # type: ignore

    class property(Generic[T0, R0]):
        def __init__(self, function: Callable[[T0], R0]) -> None:
            self.function = inject_self(function)

        def __get__(
            self, class_obj: type[T0] | T0 | None, class_type: type[T0] | type[type[T0]]  # type: ignore
        ) -> R0:
            return self.function.__get__(class_obj, class_type)()


class inject_kwargs_params_base_func(Generic[T, P, R], Callable[Concatenate[T, P], R]):  # type: ignore[misc]
    def __call__(self: T, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        ...


class inject_kwargs_params_base(Generic[T, P, R]):
    _kwargs_name = 'kwargs'

    def __init__(self, function: Callable[Concatenate[T, P], R]) -> None:
        self.function = function

        self.signature = None

    def __get__(
        self, class_obj: T, class_type: type[T]
    ) -> inject_kwargs_params_base_func[T, P, R]:
        if not self.signature:
            self.signature = Signature.from_callable(self.function, eval_str=True)  # type: ignore

            if (
                isinstance(self, inject_kwargs_params.add_to_kwargs)  # type: ignore
                and (4 not in {x.kind for x in self.signature.parameters.values()})  # type: ignore
            ):
                from ..exceptions import CustomValueError

                raise CustomValueError(
                    'This function hasn\'t got any kwargs!', 'inject_kwargs_params.add_to_kwargs', self.function
                )

        this = self

        @wraps(self.function)
        def _wrapper(self: T, *_args: P.args, **kwargs: P.kwargs) -> R:
            assert this.signature

            if class_obj and not isinstance(self, class_type):  # type: ignore
                _args = (self, *_args)
                self = class_obj

            if not hasattr(self, this._kwargs_name):
                from ..exceptions import CustomRuntimeError

                raise CustomRuntimeError(
                    f'This class doesn\'t have any "{this._kwargs_name}" attribute!', reason=self.__class__
                )

            this_kwargs = self.kwargs.copy()
            args, n_args = list(_args), len(_args)

            for i, (key, value) in enumerate(this.signature.parameters.items()):
                if key not in this_kwargs:
                    continue

                kw_value = this_kwargs.pop(key)

                if value.default is empty_param:
                    continue

                if i < n_args:
                    if args[i] != value.default:
                        continue

                    args[i] = kw_value
                else:
                    if key in kwargs and kwargs[key] != value.default:
                        continue

                    kwargs[key] = kw_value

            if isinstance(this, inject_kwargs_params.add_to_kwargs):
                kwargs |= this_kwargs

            return this.function(self, *args, **kwargs)

        return _wrapper  # type: ignore

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.__get__(None, self)(*args, **kwargs)  # type: ignore

    @property
    def __signature__(self) -> Signature:
        return Signature.from_callable(self.function)

    @classmethod
    def with_name(cls, kwargs_name: str) -> type[inject_kwargs_params]:  # type: ignore
        class _inner(inject_kwargs_params):  # type: ignore
            _kwargs_name = kwargs_name

        return _inner


if TYPE_CHECKING:  # love you mypy...
    class _add_to_kwargs:
        def __call__(self, func: F1) -> F1:
            ...

    class _inject_kwargs_params:
        def __call__(self, func: F0) -> F0:
            ...

        add_to_kwargs = _add_to_kwargs()

    inject_kwargs_params = _inject_kwargs_params()
else:
    class inject_kwargs_params(Generic[T, P, R], inject_kwargs_params_base[T, P, R]):
        class add_to_kwargs(Generic[T0, P0, R0], inject_kwargs_params_base[T0, P0, R0]):
            ...


class complex_hash(Generic[T]):
    """
    Decorator for classes to add a ``__hash__`` method to them.

    Especially useful for NamedTuples.
    """

    def __new__(cls, class_type: T) -> T:  # type: ignore
        class inner_class_type(class_type):  # type: ignore
            def __hash__(self) -> int:
                return complex_hash.hash(
                    self.__class__.__name__, *(
                        getattr(self, key) for key in self.__annotations__.keys()
                    )
                )

        return inner_class_type  # type: ignore

    @staticmethod
    def hash(*args: Any) -> int:
        """
        Recursively hash every unhashable object in ``*args``.

        :param *args:   Objects to be hashed.

        :return:        Hash of all the combined objects' hashes.
        """

        values = list[str]()
        for value in args:
            try:
                new_hash = hash(value)
            except TypeError:
                if isinstance(value, Iterable):
                    new_hash = complex_hash.hash(*value)
                else:
                    new_hash = hash(str(value))

            values.append(str(new_hash))

        return hash('_'.join(values))


def get_subclasses(family: type[T], exclude: Sequence[type[T]] = []) -> list[type[T]]:
    """
    Get all subclasses of a given type.

    :param family:  "Main" type all other classes inherit from.
    :param exclude: Excluded types from the yield. Note that they won't be excluded from search.
                    For examples, subclasses of these excluded classes will be yield.

    :return:        List of all subclasses of "family".
    """

    def _subclasses(cls: type[T]) -> Generator[type[T], None, None]:
        for subclass in cls.__subclasses__():
            yield from _subclasses(subclass)
            if subclass in exclude:
                continue
            yield subclass

    return list(set(_subclasses(family)))


class classproperty(Generic[P, R, T, T0, P0]):
    """
    Make a class property. A combination between classmethod and property.
    """

    __isabstractmethod__: bool = False

    class metaclass(type):
        """This must be set for the decorator to work."""

        def __setattr__(self, key: str, value: Any) -> None:
            if key in self.__dict__:
                obj = self.__dict__.get(key)

                if obj and isinstance(obj, classproperty):
                    obj.__set__(self, value)
                    return

            super(classproperty.metaclass, self).__setattr__(key, value)

    @no_type_check
    def __init__(
        self,
        fget: classmethod[T, P, R] | Callable[P, R],
        fset: classmethod[T, P, None] | Callable[[T, T0], None] | None = None,
        fdel: classmethod[T, P1, None] | Callable[P1, None] | None = None,
        doc: str | None = None,
    ) -> None:
        self.fget = self._wrap(fget)
        self.fset = self._wrap(fset) if fset is not None else fset
        self.fdel = self._wrap(fdel) if fdel is not None else fdel

        self.doc = doc

    def _wrap(self, func: classmethod[T1, P1, R1] | Callable[P1, R1]) -> classmethod[T1, P1, R1]:
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)  # type: ignore

        return func

    def getter(self, __fget: classmethod[T, P, R] | Callable[P1, R1]) -> classproperty[P1, R1, T, T0, P0]:
        self.fget = self._wrap(__fget)  # type: ignore
        return self  # type: ignore

    @no_type_check
    def setter(self, __fset: classmethod[T1, P, None] | Callable[[T1, T2], None]) -> classproperty[P, R, T1, T2, P0]:
        self.fset = self._wrap(__fset)
        return self

    def deleter(self, __fdel: classmethod[T1, P1, None] | Callable[P1, None]) -> classproperty[P, R, T, T0, P1]:
        self.fdel = self._wrap(__fdel)  # type: ignore
        return self  # type: ignore

    def __get__(self, __obj: Any, __type: type | None = None) -> R:
        if __type is None:
            __type = type(__obj)

        return self.fget.__get__(__obj, __type)()  # type: ignore

    def __set__(self, __obj: Any, __value: T1) -> None:
        from ..exceptions import CustomError

        if not self.fset:  # type: ignore
            raise CustomError[AttributeError]("Can't set attribute")

        if isclass(__obj):
            type_, __obj = __obj, None
        else:
            type_ = type(__obj)

        return self.fset.__get__(__obj, type_)(__value)  # type: ignore

    def __delete__(self, __obj: Any) -> None:
        from ..exceptions import CustomError

        if not self.fdel:  # type: ignore
            raise CustomError[AttributeError]("Can't delete attribute")

        if isclass(__obj):
            type_, __obj = __obj, None
        else:
            type_ = type(__obj)

        return self.fdel.__delete__(__obj, type_)(__obj)  # type: ignore

    def __name__(self) -> str:
        return self.fget.__name__  # type: ignore


class cachedproperty(property, Generic[P, R, T, T0, P0]):
    """
    Wrapper for a one-time get property, that will be cached.

    Keep in mind two things:

     * The cache is per-object. Don't hold a reference to itself or it will never get garbage collected.
     * Your class has to either manually set __dict__[cachedproperty.cache_key]
       or inherit from cachedproperty.baseclass.
    """

    __isabstractmethod__: bool = False

    cache_key = '_stgpt_cachedproperty_cache'

    class baseclass:
        """Inherit from this class to automatically set the cache dict."""

        if not TYPE_CHECKING:
            def __new__(cls, *args: Any, **kwargs: Any) -> None:
                try:
                    self = super().__new__(cls, *args, **kwargs)
                except TypeError:
                    self = super().__new__(cls)
                self.__dict__.__setitem__(cachedproperty.cache_key, dict[str, Any]())
                return self

    if TYPE_CHECKING:
        def __init__(
            self, fget: Callable[P, R], fset: Callable[[T, T0], None] | None = None,
            fdel: Callable[P0, None] | None = None, doc: str | None = None,
        ) -> None:
            ...

        def getter(self, __fget: Callable[P1, R1]) -> cachedproperty[P1, R1, T, T0, P0]:
            ...

        def setter(self, __fset: Callable[[T1, T2], None]) -> cachedproperty[P, R, T1, T2, P0]:
            ...

        def deleter(self, __fdel: Callable[P1, None]) -> cachedproperty[P, R, T, T0, P1]:
            ...

    def __get__(self, __obj: Any, __type: type | None = None) -> R:
        if isinstance(self.fget, classproperty):
            function = partial(self.fget.__get__, __obj, __type)
            __obj = __type

            if not hasattr(__obj, cachedproperty.cache_key):
                setattr(__obj, cachedproperty.cache_key, dict[str, Any]())

            cache = getattr(__obj, cachedproperty.cache_key)
            name = self.fget.__name__
        else:
            function = self.fget.__get__(__obj, __type)  # type: ignore
            cache = __obj.__dict__.get(cachedproperty.cache_key)
            name = function.__name__

        if name not in cache:
            cache[name] = function()

        return cache[name]  # type: ignore


class KwargsNotNone(KwargsT):
    """Remove all None objects from this kwargs dict."""

    if not TYPE_CHECKING:
        def __new__(cls, *args: Any, **kwargs: Any) -> KwargsNotNone:
            return KwargsT(**{
                key: value for key, value in KwargsT(*args, **kwargs).items()
                if value is not None
            })


SingleMeta = TypeVar('SingleMeta', bound=type)


class SingletonMeta(type):
    _instances = dict[type[SingleMeta], SingleMeta]()  # type: ignore
    _singleton_init: bool

    def __new__(
        cls: type[SingletonSelf], name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any
    ) -> SingletonSelf:
        return type.__new__(cls, name, bases, namespace | {'_singleton_init': kwargs.pop('init', False)})

    def __call__(cls: type[SingletonSelf], *args: Any, **kwargs: Any) -> SingletonSelf:  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        elif cls._singleton_init:
            cls._instances[cls].__init__(*args, **kwargs)  # type: ignore

        return cls._instances[cls]


SingletonSelf = TypeVar('SingletonSelf', bound=SingletonMeta)


class Singleton(metaclass=SingletonMeta):
    """Handy class to inherit to have the SingletonMeta metaclass."""


class to_singleton_impl:
    _ts_args = tuple[str, ...]()
    _ts_kwargs = dict[str, Any]()
    _add_classes = tuple[type, ...]()

    def __new__(_cls, cls: type[T]) -> T:  # type: ignore
        if _cls._add_classes:
            class rcls(cls, *_cls._add_classes):  # type: ignore
                ...
        else:
            rcls = cls  # type: ignore

        return rcls(*_cls._ts_args, **_cls._ts_kwargs)

    @classmethod
    def with_args(cls, *args: Any, **kwargs: Any) -> type[to_singleton]:
        class _inner_singl(cls):  # type: ignore
            _ts_args = args
            _ts_kwargs = kwargs

        return _inner_singl


class to_singleton(to_singleton_impl):
    class as_property(to_singleton_impl):
        _add_classes = (property, )


class LinearRangeLut(Mapping[int, int]):
    __slots__ = ('ranges', '_ranges_idx_lut', '_misses_n')

    def __init__(self, ranges: Mapping[int, range]) -> None:
        self.ranges = ranges

        self._ranges_idx_lut = list(self.ranges.items())
        self._misses_n = 0

    def __getitem__(self, n: int) -> int:
        for missed_hit, (idx, k) in enumerate(self._ranges_idx_lut):
            if n in k:
                break

        if missed_hit:
            self._misses_n += 1

            if self._misses_n > 2:
                self._ranges_idx_lut = self._ranges_idx_lut[missed_hit:] + self._ranges_idx_lut[:missed_hit]

        return idx

    def __len__(self) -> int:
        return len(self.ranges)

    def __iter__(self) -> Iterator[int]:
        return iter(range(len(self)))

    def __setitem__(self, n: int, _range: range) -> NoReturn:
        raise NotImplementedError

    def __delitem__(self, n: int) -> NoReturn:
        raise NotImplementedError
