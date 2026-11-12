"""Defines the jinja builtins for dbt."""

import datetime
import itertools
import json
import re
from collections.abc import Iterator
from contextvars import ContextVar
from copy import deepcopy
from functools import partial
from types import BuiltinMethodType
from typing import Any, Callable, Union

import pytz
import yaml
from jinja2.runtime import Context, Macro
from jinja2.sandbox import SandboxedEnvironment

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters.builtins.common import FunctionWrapper


class DbtModules(dict[str, dict[str, Any]]):
    """Identify builtin namespaces separately from configured context overrides."""


def get_dbt_modules() -> DbtModules:
    """Create a fresh namespace containing dbt's supported module exports."""
    return DbtModules(
        {
            "datetime": {
                name: getattr(datetime, name)
                for name in ("date", "datetime", "time", "timedelta", "tzinfo")
            },
            # Include nested country timezone lists and preserve pytz's lazy,
            # case-insensitive, callable country mappings.
            "pytz": {name: deepcopy(getattr(pytz, name)) for name in pytz.__all__},
            "re": {name: getattr(re, name) for name in re.__all__},
            "itertools": {
                name: getattr(itertools, name)
                for name in (
                    "count",
                    "cycle",
                    "repeat",
                    "accumulate",
                    "chain",
                    "compress",
                    "islice",
                    "starmap",
                    "tee",
                    "zip_longest",
                    "product",
                    "permutations",
                    "combinations",
                    "combinations_with_replacement",
                )
            },
        }
    )


class RelationEmulator:
    """A class which emulates the `this` class from dbt."""

    # Tell Jinja this object is safe to call and does not alter data.
    # https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
    unsafe_callable = False
    alters_data = False

    identifier = "this_model"
    schema = "this_schema"
    database = "this_database"

    def __init__(self, identifier: str = "this_model") -> None:
        self.identifier = identifier

    def __call__(self, *args: Any, **kwargs: Any) -> "RelationEmulator":
        """When relation(*) is called return self as another relation."""
        return self

    def __getattr__(self, name: str) -> Union["RelationEmulator", bool]:
        """When relation.attribute is called return self as another relation.

        NOTE: If the attribute begins with `is_`, then return a boolean True.
        """
        if name[0:3] == "is_":
            return True
        return self

    def __str__(self) -> str:
        return self.identifier


class VarEmulator(str):
    """A string-like class which emulates dbt's `var()` return value."""

    def __new__(cls, value: str = "item") -> "VarEmulator":
        """Construct a string-like placeholder for mocked dbt `var()` output."""
        return super().__new__(cls, value)

    def __getattr__(self, name: str) -> "VarEmulator":
        """When var.attribute is called return self as another placeholder."""
        return self

    def __getitem__(self, name: Any) -> str:
        """When var['key'] is called return a placeholder instead of failing."""
        if isinstance(name, (int, slice)):
            return super().__getitem__(name)
        return self


class MacroReturn(Exception):
    """Exception used to allow macros to return non-string values."""

    def __init__(self, value: Any) -> None:
        self.value = value


def _builtin_return(value: Any) -> None:
    raise MacroReturn(value)


def _builtin_fromjson(string: str, default: Any = None) -> Any:
    """Deserialize JSON, returning the default for ValueError as dbt does."""
    try:
        return json.loads(string)
    except ValueError:
        return default


def _builtin_tojson(value: Any, default: Any = None, sort_keys: bool = False) -> Any:
    """Serialize JSON, returning the default for ValueError as dbt does."""
    try:
        return json.dumps(value, sort_keys=sort_keys)
    except ValueError:
        return default


def _builtin_fromyaml(value: str, default: Any = None) -> Any:
    """Deserialize YAML safely, returning the default on dbt's handled errors."""
    try:
        return yaml.safe_load(value)
    except (AttributeError, ValueError, yaml.YAMLError):
        return default


def _builtin_toyaml(value: Any, default: Any = None, sort_keys: bool = False) -> Any:
    """Serialize YAML safely with dbt's fallback and key-order behavior."""
    try:
        return yaml.safe_dump(value, sort_keys=sort_keys)
    except (ValueError, yaml.YAMLError):
        return default


_DBT_MODULE_ERRORS = (
    re.error,
    pytz.InvalidTimeError,
    ArithmeticError,
    LookupError,
    TypeError,
    ValueError,
    RecursionError,
    AttributeError,
    OSError,
)
_DBT_CALLBACK_ERRORS: ContextVar[Union[list[Exception], None]] = ContextVar(
    "dbt_callback_errors", default=None
)


def _is_dbt_module_callable(obj: Any) -> bool:
    """Identify functions, bound methods, and unbound native descriptors."""
    module_name = (
        getattr(obj, "__module__", None)
        or getattr(getattr(obj, "__self__", None), "__module__", None)
        or getattr(getattr(obj, "__objclass__", None), "__module__", None)
    )
    return module_name in ("datetime", "itertools", "re", "pytz", "pytz.tzinfo")


class _DbtModuleIterator(Iterator[Any]):
    """Keep native iteration lazy while applying the same error boundary."""

    def __init__(self, iterator: Iterator[Any], native_call: Callable[..., Any]):
        self._iterator = iterator
        self._native_call = native_call

    def __next__(self) -> Any:
        return self._native_call(next, self._iterator)

    def __repr__(self) -> str:
        return repr(self._iterator)


class DbtSandboxedEnvironment(SandboxedEnvironment):
    """Preserve sandbox checks and dbt returns at native callback boundaries."""

    def call(self, context: Context, obj: Any, /, *args: Any, **kwargs: Any) -> Any:
        """Route native callbacks through Jinja, catching returns at their macro."""
        callback_pos = None
        callback_name = None
        if obj is itertools.starmap:
            callback_pos = 0
        elif obj is itertools.accumulate:
            callback_pos, callback_name = 1, "func"
        elif (
            obj is re.sub
            or obj is re.subn
            or obj is re.Pattern.sub
            or obj is re.Pattern.subn
        ):
            callback_pos, callback_name = 1, "repl"
        elif (
            isinstance(obj, BuiltinMethodType)
            and isinstance(obj.__self__, re.Pattern)
            and obj.__name__ in ("sub", "subn")
        ):
            callback_pos, callback_name = 0, "repl"

        # The native function may invoke its callback later (e.g. starmap).
        # Check at invocation time to preserve laziness and context injection.
        if callback_pos is not None:
            # Match Context.call()'s scoped-variable injection. Native APIs are
            # not context-aware, so Jinja otherwise discards these locals.
            for scope in ("_loop_vars", "_block_vars"):
                if kwargs.get(scope):
                    context = context.derived(kwargs[scope])
            if len(args) > callback_pos:
                callback = args[callback_pos]
            else:
                callback = kwargs.get(callback_name) if callback_name else None
            if callable(callback):

                def call_callback(*callback_args: Any, **callback_kwargs: Any) -> Any:
                    try:
                        return self.call(
                            context, callback, *callback_args, **callback_kwargs
                        )
                    except _DBT_MODULE_ERRORS as exc:
                        # Share provenance with nested native calls and lazy
                        # iteration, including an eager consumer like product().
                        callback_errors = _DBT_CALLBACK_ERRORS.get()
                        if callback_errors is not None:
                            callback_errors.append(exc)
                        raise

                if len(args) > callback_pos:
                    args = (
                        *args[:callback_pos],
                        call_callback,
                        *args[callback_pos + 1 :],
                    )
                elif callback_name is not None:
                    kwargs[callback_name] = call_callback
        try:
            result = self._call_with_native_errors(
                obj, super().call, context, obj, *args, **kwargs
            )
            if obj is itertools.tee:
                return tuple(
                    _DbtModuleIterator(
                        iterator, partial(self._call_with_native_errors, obj)
                    )
                    for iterator in result
                )
            if isinstance(result, Iterator) and _is_dbt_module_callable(obj):
                return _DbtModuleIterator(
                    result, partial(self._call_with_native_errors, obj)
                )
            return result
        except MacroReturn as exc:
            if isinstance(obj, Macro):
                return exc.value
            # The return() builtin must unwind until its enclosing macro call.
            raise

    def _call_with_native_errors(
        self, obj: Any, func: Callable[..., Any], /, *args: Any, **kwargs: Any
    ) -> Any:
        """Normalize native failures, sharing callback origin until unwound."""
        callback_errors = _DBT_CALLBACK_ERRORS.get()
        token = None
        if callback_errors is None:
            callback_errors = []
            token = _DBT_CALLBACK_ERRORS.set(callback_errors)
        try:
            return func(*args, **kwargs)
        except _DBT_MODULE_ERRORS as exc:
            if any(exc is callback_error for callback_error in callback_errors):
                raise
            if _is_dbt_module_callable(obj):
                # Native parsers can include input values in their exceptions.
                # Suppress that context as well as the message; interrupts pass.
                # Macros can execute while constructing the renderer, outside
                # process()'s rendering handler, so raise the public error here.
                raise SQLTemplaterError(
                    "Invalid input to a dbt module function", line_no=1, line_pos=1
                ) from None
            raise
        finally:
            if token is not None:
                _DBT_CALLBACK_ERRORS.reset(token)


class DbtMacroWrapper:
    """Class that wraps macros to catch MacroReturn exceptions during execution."""

    # Tell Jinja this object is safe to call and does not alter data.
    # https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment.is_safe_callable
    unsafe_callable = False
    alters_data = False

    def __init__(self, macro: Callable[..., Any]):
        self.macro = macro

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Wraps jinja macro calls to handle dbt's `return` jinja function."""
        try:
            return self.macro(*args, **kwargs)
        except MacroReturn as e:
            return e.value


# NOTE: we use `FunctionWrapper` on all of the callable builtins here
# so that there's a sensible error message if someone tries to render
# them directly.
DBT_BUILTINS = {
    "ref": FunctionWrapper("ref", lambda *args, **kwargs: RelationEmulator(args[-1])),
    # In case of a cross project ref in dbt, model_ref is the second
    # argument. Otherwise it is the only argument.
    "source": FunctionWrapper(
        "source",
        lambda source_name, table: RelationEmulator(f"{source_name}_{table}"),
    ),
    "function": FunctionWrapper(
        "function",
        # Mirror `ref` handling: tolerate optional qualifier args and use the
        # last positional argument as the function identifier.
        lambda *args, **kwargs: RelationEmulator(args[-1]),
    ),
    "config": FunctionWrapper("config", lambda **kwargs: ""),
    "var": FunctionWrapper("var", lambda variable, default="": VarEmulator()),
    # `is_incremental()` renders as True, always in this case.
    # TODO: This means we'll never parse other parts of the query,
    # that are only reachable when `is_incremental()` returns False.
    # We should try to find a solution to that. Perhaps forcing the file
    # to be parsed TWICE if it uses this variable.
    "is_incremental": FunctionWrapper("is_incremental", lambda: True),
    "this": RelationEmulator(),
    "zip_strict": FunctionWrapper("zip_strict", zip),
    "zip": FunctionWrapper(
        "zip",
        lambda *args, default=None: (
            zip(*args) if all(hasattr(arg, "__iter__") for arg in args) else default
        ),
    ),
    "return": FunctionWrapper("return", _builtin_return),
    "fromjson": FunctionWrapper("fromjson", _builtin_fromjson),
    "tojson": FunctionWrapper("tojson", _builtin_tojson),
    "fromyaml": FunctionWrapper("fromyaml", _builtin_fromyaml),
    "toyaml": FunctionWrapper("toyaml", _builtin_toyaml),
}
