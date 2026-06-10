"""Regression test for LT02 indent oscillation.

See https://github.com/sqlfluff/sqlfluff/issues/7870 - a trailing comma
guarded by ``loop.last`` and rendered on its own line used to flip-flop
between two indent depths on successive ``fix`` runs. The YAML fixtures in
``LT02-indent.yml`` exercise a single fix pass; this test additionally
asserts the *roundtrip* property, i.e. that re-fixing a fixed file is a
no-op.
"""

from sqlfluff.core import FluffConfig, Linter

# The reproduction from the issue, with the trailing-comma line *under*
# indented (4 spaces). Fixing this should settle on the stable form below.
_UNDER_INDENTED = """{%- set extraction_list = [
    ('Compound', 'Canonicalized', 'ival'),
    ('IUPAC Name', 'Allowed', 'sval'),
    ('InChI', 'Standard', 'sval')
] %}

{{ config(cluster_by=['cid']) }}

SELECT
{%- for label, name, field in extraction_list %}
        (
            SELECT
                p.value.{{ field }}
            FROM UNNEST(props) AS p
            WHERE
                p.urn.label = '{{ label }}'
                AND p.urn.name = '{{ name }}'
            LIMIT 1
        )
            AS {{ (label ~ '_' ~ name) | lower | replace(' ', '_') | replace('-','_') }}
    {{- "," if not loop.last }}
{%- endfor %}
FROM {{ ref('pubchem_compound_raw') }}
"""

# The stable form: the trailing-comma line indented to 8 spaces.
_STABLE = """{%- set extraction_list = [
    ('Compound', 'Canonicalized', 'ival'),
    ('IUPAC Name', 'Allowed', 'sval'),
    ('InChI', 'Standard', 'sval')
] %}

{{ config(cluster_by=['cid']) }}

SELECT
{%- for label, name, field in extraction_list %}
        (
            SELECT
                p.value.{{ field }}
            FROM UNNEST(props) AS p
            WHERE
                p.urn.label = '{{ label }}'
                AND p.urn.name = '{{ name }}'
            LIMIT 1
        )
            AS {{ (label ~ '_' ~ name) | lower | replace(' ', '_') | replace('-','_') }}
        {{- "," if not loop.last }}
{%- endfor %}
FROM {{ ref('pubchem_compound_raw') }}
"""


def test_rules_std_LT02_loop_comma_no_oscillation() -> None:
    """Fixing the loop trailing-comma indent must converge, not oscillate."""
    cfg = FluffConfig(
        overrides={"dialect": "bigquery", "rules": "LT02", "templater": "jinja"}
    )
    linter = Linter(config=cfg)

    # The under-indented variant should report a single LT02 violation and
    # fix to the stable form.
    linted = linter.lint_string(_UNDER_INDENTED, fix=True)
    assert linted.check_tuples() == [("LT02", 20, 89)]
    fixed, _ = linted.fix_string()
    assert fixed == _STABLE

    # Re-fixing the stable form must be a no-op: no violations and no change.
    # Without the fix this oscillated straight back to the 4-space indent.
    relinted = linter.lint_string(_STABLE, fix=True)
    assert relinted.check_tuples() == []
    refixed, _ = relinted.fix_string()
    assert refixed == _STABLE
