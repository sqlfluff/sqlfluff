"""Defines the jinja builtins for dbt."""

from typing import Any, Union

from sqlfluff.core.templaters.builtins.common import FunctionWrapper


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
    "config": FunctionWrapper("config", lambda **kwargs: ""),
    "var": FunctionWrapper("var", lambda variable, default="": "item"),
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
}
