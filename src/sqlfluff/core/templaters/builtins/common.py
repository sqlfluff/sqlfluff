"""Common classes and functions for defining templating builtins."""

from typing import Any, Callable

from sqlfluff.core.errors import SQLTemplaterError


class FunctionWrapper:
    """Class to wrap a callable, for better error handling.

    When called, it just delegates to the provided callable, but if
    it is rendered as a string directly, it generates a templating
    error.
    """

    def __init__(self, name: str, callable: Callable[..., Any]):
        self._name = name
        self._callable = callable

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """When the wrapper is called, call the internal function."""
        return self._callable(*args, **kwargs)

    def __str__(self) -> str:
        """If we try and render the wrapper directly, throw an error."""
        raise SQLTemplaterError(
            f"Unable to render builtin callable {self._name!r} as a "
            "variable because it is defined as a function. To remove "
            "this function from the context, set `apply_dbt_builtins` "
            "to False."
        )
