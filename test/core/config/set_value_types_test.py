"""Regression tests for values set through the configuration API."""

from decimal import Decimal

import pytest

from sqlfluff.core import FluffConfig, Linter


class _CustomFloat(float):
    def __int__(self):
        return 7


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, True),
        (False, False),
        (2.75, 2.75),
        (None, None),
        (2, 2),
        (" true ", True),
        ("false", False),
        ("02", 2),
        ("2.75", 2.75),
        ("None", None),
        ("text", "text"),
        (b"12", 12),
        (Decimal("2.75"), 2),
        (_CustomFloat(2.75), 7),
    ],
)
def test_set_value_scalar_types(value, expected):
    """Preserve typed scalars and keep the existing coercions."""
    config = FluffConfig(overrides={"dialect": "ansi"}, ignore_local_config=True)
    path = ("templater", "jinja", "context", "value")
    config.set_value(path, value)
    missing = object()
    actual = config.get(path[-1], section=path[:-1], default=missing)

    assert actual is not missing
    assert type(actual) is type(expected)
    assert actual == expected


@pytest.mark.parametrize("enabled", [True, False])
def test_set_value_controls_jinja_dbt_builtins(enabled):
    """Render with the assigned Python boolean."""
    config = FluffConfig(overrides={"dialect": "ansi"}, ignore_local_config=True)
    config.set_value(("templater", "jinja", "apply_dbt_builtins"), enabled)
    rendered = Linter(config=config).render_string(
        "select * from {{ ref('table') }}", "<string>", config, "utf8"
    )

    if enabled:
        assert not rendered.templater_violations
        assert rendered.templated_variants[0].templated_str == "select * from table"
    else:
        assert [violation.desc() for violation in rendered.templater_violations] == [
            "Undefined jinja template variable: 'ref'"
        ]
