"""Tests for the jinja templater.

These tests also test much of the core lexer, especially
the treatment of templated sections which only really make
sense to test in the context of a templater which supports
loops and placeholders.
"""

from collections import defaultdict
import logging
from typing import List, NamedTuple

import pytest
from jinja2.exceptions import UndefinedError

from sqlfluff.core.errors import SQLFluffSkipFile, SQLTemplaterError
from sqlfluff.core.templaters import JinjaTemplater
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile
from sqlfluff.core.templaters.jinja import DummyUndefined, JinjaAnalyzer
from sqlfluff.core import Linter, FluffConfig


JINJA_STRING = (
    "SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, "
    "{% endif %}{% endfor %} WHERE {{condition}}\n\n"
)


@pytest.mark.parametrize(
    "instr, expected_outstr",
    [
        (
            JINJA_STRING,
            "SELECT * FROM f, o, o WHERE a < 10\n\n",
        ),
        # Test for issue #968. This was previously raising an UnboundLocalError.
        (
            """
{% set event_columns = ['campaign', 'click_item'] %}

SELECT
    event_id
    {% for event_column in event_columns %}
    , {{ event_column }}
    {% endfor %}
FROM events
            """,
            (
                "\n\n\nSELECT\n    event_id\n    \n    , campaign\n    \n    , "
                "click_item\n    \nFROM events\n            "
            ),
        ),
    ],
    ids=["simple", "unboundlocal_bugfix"],
)
def test__templater_jinja(instr, expected_outstr):
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplater(override_context=dict(blah="foo", condition="a < 10"))
    outstr, _ = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert str(outstr) == expected_outstr


class RawTemplatedTestCase(NamedTuple):
    """Instances of this object are test cases for test__templater_jinja_slices."""

    name: str
    instr: str
    templated_str: str

    # These fields are used to check TemplatedFile.sliced_file.
    expected_templated_sliced__source_list: List[str]
    expected_templated_sliced__templated_list: List[str]

    # This field is used to check TemplatedFile.raw_sliced.
    expected_raw_sliced__source_list: List[str]


@pytest.mark.parametrize(
    "case",
    [
        RawTemplatedTestCase(
            name="basic_block",
            instr="\n\n{% set x = 42 %}\nSELECT 1, 2\n",
            templated_str="\n\n\nSELECT 1, 2\n",
            expected_templated_sliced__source_list=[
                "\n\n",
                "{% set x = 42 %}",
                "\nSELECT 1, 2\n",
            ],
            expected_templated_sliced__templated_list=[
                "\n\n",
                "",
                "\nSELECT 1, 2\n",
            ],
            expected_raw_sliced__source_list=[
                "\n\n",
                "{% set x = 42 %}",
                "\nSELECT 1, 2\n",
            ],
        ),
        RawTemplatedTestCase(
            name="strip_left_block",
            instr="\n\n{%- set x = 42 %}\nSELECT 1, 2\n",
            templated_str="\nSELECT 1, 2\n",
            expected_templated_sliced__source_list=[
                "\n\n",
                "{%- set x = 42 %}",
                "\nSELECT 1, 2\n",
            ],
            expected_templated_sliced__templated_list=[
                "",
                "",
                "\nSELECT 1, 2\n",
            ],
            expected_raw_sliced__source_list=[
                "\n\n",
                "{%- set x = 42 %}",
                "\nSELECT 1, 2\n",
            ],
        ),
        RawTemplatedTestCase(
            name="strip_both_block",
            instr="\n\n{%- set x = 42 -%}\nSELECT 1, 2\n",
            templated_str="SELECT 1, 2\n",
            expected_templated_sliced__source_list=[
                "\n\n",
                "{%- set x = 42 -%}",
                "\n",
                "SELECT 1, 2\n",
            ],
            expected_templated_sliced__templated_list=[
                "",
                "",
                "",
                "SELECT 1, 2\n",
            ],
            expected_raw_sliced__source_list=[
                "\n\n",
                "{%- set x = 42 -%}",
                "\n",
                "SELECT 1, 2\n",
            ],
        ),
        RawTemplatedTestCase(
            name="basic_data",
            instr="""select
    c1,
    {{ 'c' }}2 as user_id
""",
            templated_str="""select
    c1,
    c2 as user_id
""",
            expected_templated_sliced__source_list=[
                "select\n    c1,\n    ",
                "{{ 'c' }}",
                "2 as user_id\n",
            ],
            expected_templated_sliced__templated_list=[
                "select\n    c1,\n    ",
                "c",
                "2 as user_id\n",
            ],
            expected_raw_sliced__source_list=[
                "select\n    c1,\n    ",
                "{{ 'c' }}",
                "2 as user_id\n",
            ],
        ),
        # Note this is basically identical to the "basic_data" case above.
        # "Right strip" is not actually a thing in Jinja.
        RawTemplatedTestCase(
            name="strip_right_data",
            instr="""SELECT
  {{ 'col1,' -}}
  col2
""",
            templated_str="""SELECT
  col1,col2
""",
            expected_templated_sliced__source_list=[
                "SELECT\n  ",
                "{{ 'col1,' -}}",
                "\n  ",
                "col2\n",
            ],
            expected_templated_sliced__templated_list=[
                "SELECT\n  ",
                "col1,",
                "",
                "col2\n",
            ],
            expected_raw_sliced__source_list=[
                "SELECT\n  ",
                "{{ 'col1,' -}}",
                "\n  ",
                "col2\n",
            ],
        ),
        RawTemplatedTestCase(
            name="strip_both_data",
            instr="""select
    c1,
    {{- 'c' -}}
2 as user_id
""",
            templated_str="""select
    c1,c2 as user_id
""",
            expected_templated_sliced__source_list=[
                "select\n    c1,",
                "\n    ",
                "{{- 'c' -}}",
                "\n",
                "2 as user_id\n",
            ],
            expected_templated_sliced__templated_list=[
                "select\n    c1,",
                "",
                "c",
                "",
                "2 as user_id\n",
            ],
            expected_raw_sliced__source_list=[
                "select\n    c1,",
                "\n    ",
                "{{- 'c' -}}",
                "\n",
                "2 as user_id\n",
            ],
        ),
        RawTemplatedTestCase(
            name="strip_both_comment",
            instr="""select
    c1,
    {#- Column 2 -#} c2 as user_id
""",
            templated_str="""select
    c1,c2 as user_id
""",
            expected_templated_sliced__source_list=[
                "select\n    c1,",
                "\n    ",
                "{#- Column 2 -#}",
                " ",
                "c2 as user_id\n",
            ],
            expected_templated_sliced__templated_list=[
                "select\n    c1,",
                "",
                "",
                "",
                "c2 as user_id\n",
            ],
            expected_raw_sliced__source_list=[
                "select\n    c1,",
                "\n    ",
                "{#- Column 2 -#}",
                " ",
                "c2 as user_id\n",
            ],
        ),
        RawTemplatedTestCase(
            name="union_all_loop1",
            instr="""{% set products = [
  'table1',
  'table2',
  ] %}

{% for product in products %}
SELECT
  brand
FROM
  {{ product }}
{% if not loop.last -%} UNION ALL {%- endif %}
{% endfor %}
""",
            templated_str=(
                "\n\n\nSELECT\n  brand\nFROM\n  table1\nUNION ALL\n\nSELECT\n  "
                "brand\nFROM\n  table2\n\n\n"
            ),
            expected_templated_sliced__source_list=[
                "{% set products = [\n  'table1',\n  'table2',\n  ] %}",
                "\n\n",
                "{% for product in products %}",
                "\nSELECT\n  brand\nFROM\n  ",
                "{{ product }}",
                "\n",
                "{% if not loop.last -%}",
                " ",
                "UNION ALL",
                " ",
                "{%- endif %}",
                "\n",
                "{% endfor %}",
                "\nSELECT\n  brand\nFROM\n  ",
                "{{ product }}",
                "\n",
                "{% if not loop.last -%}",
                "{%- endif %}",
                "\n",
                "{% endfor %}",
                "\n",
            ],
            expected_templated_sliced__templated_list=[
                "",
                "\n\n",
                "",
                "\nSELECT\n  brand\nFROM\n  ",
                "table1",
                "\n",
                "",
                "",
                "UNION ALL",
                "",
                "",
                "\n",
                "",
                "\nSELECT\n  brand\nFROM\n  ",
                "table2",
                "\n",
                "",
                "",
                "\n",
                "",
                "\n",
            ],
            expected_raw_sliced__source_list=[
                "{% set products = [\n  'table1',\n  'table2',\n  ] %}",
                "\n\n",
                "{% for product in products %}",
                "\nSELECT\n  brand\nFROM\n  ",
                "{{ product }}",
                "\n",
                "{% if not loop.last -%}",
                " ",
                "UNION ALL",
                " ",
                "{%- endif %}",
                "\n",
                "{% endfor %}",
                "\n",
            ],
        ),
        RawTemplatedTestCase(
            "set_multiple_variables_and_define_macro",
            """{% macro echo(text) %}
{{text}}
{% endmacro %}

{% set a, b = 1, 2 %}

SELECT
    {{ echo(a) }},
    {{ echo(b) }}""",
            "\n\n\n\nSELECT\n    \n1\n,\n    \n2\n",
            [
                "{% macro echo(text) %}",
                "\n",
                "{{text}}",
                "\n",
                "{% endmacro %}",
                "\n\n",
                "{% set a, b = 1, 2 %}",
                "\n\nSELECT\n    ",
                "{{ echo(a) }}",
                ",\n    ",
                "{{ echo(b) }}",
            ],
            [
                "",
                "",
                "",
                "",
                "",
                "\n\n",
                "",
                "\n\nSELECT\n    ",
                "\n1\n",
                ",\n    ",
                "\n2\n",
            ],
            [
                "{% macro echo(text) %}",
                "\n",
                "{{text}}",
                "\n",
                "{% endmacro %}",
                "\n\n",
                "{% set a, b = 1, 2 %}",
                "\n\nSELECT\n    ",
                "{{ echo(a) }}",
                ",\n    ",
                "{{ echo(b) }}",
            ],
        ),
    ],
    ids=lambda case: case.name,
)
def test__templater_jinja_slices(case: RawTemplatedTestCase):
    """Test that Jinja templater slices raw and templated file correctly."""
    t = JinjaTemplater()
    templated_file, _ = t.process(
        in_str=case.instr,
        fname="test",
        config=FluffConfig(overrides={"dialect": "ansi"}),
    )
    assert templated_file
    assert templated_file.source_str == case.instr
    assert templated_file.templated_str == case.templated_str
    # Build and check the list of source strings referenced by "sliced_file".
    actual_ts_source_list = [
        case.instr[ts.source_slice] for ts in templated_file.sliced_file
    ]
    assert actual_ts_source_list == case.expected_templated_sliced__source_list

    # Build and check the list of templated strings referenced by "sliced_file".
    actual_ts_templated_list = [
        templated_file.templated_str[ts.templated_slice]
        for ts in templated_file.sliced_file
    ]
    assert actual_ts_templated_list == case.expected_templated_sliced__templated_list

    # Build and check the list of source strings referenced by "raw_sliced".
    previous_rs = None
    actual_rs_source_list: List[RawFileSlice] = []
    for rs in templated_file.raw_sliced + [None]:  # type: ignore
        if previous_rs:
            if rs:
                actual_source = case.instr[previous_rs.source_idx : rs.source_idx]
            else:
                actual_source = case.instr[previous_rs.source_idx :]
            actual_rs_source_list.append(actual_source)
        previous_rs = rs
    assert actual_rs_source_list == case.expected_raw_sliced__source_list


def test_templater_set_block_handling():
    """Test handling of literals in {% set %} blocks.

    Specifically, verify they are not modified in the alternate template.
    """

    def run_query(sql):
        # Prior to the bug fix, this assertion failed. This was bad because,
        # inside JinjaTracer, dbt templates similar to the one in this test
        # would call the database with funky SQL (including weird strings it
        # uses internally like: 00000000000000000000000000000002.
        assert sql == "\n\nselect 1 from foobarfoobarfoobarfoobar_dev\n\n"
        return sql

    t = JinjaTemplater(override_context=dict(run_query=run_query))
    instr = """{% set my_query1 %}
select 1 from foobarfoobarfoobarfoobar_{{ "dev" }}
{% endset %}
{% set my_query2 %}
{{ my_query1 }}
{% endset %}

{{ run_query(my_query2) }}
"""
    outstr, vs = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert str(outstr) == "\n\n\n\n\nselect 1 from foobarfoobarfoobarfoobar_dev\n\n\n"
    assert len(vs) == 0


def test__templater_jinja_error_variable():
    """Test missing variable error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah="foo"))
    instr = JINJA_STRING
    outstr, vs = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert str(outstr) == "SELECT * FROM f, o, o WHERE \n\n"
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no == 1 for v in vs)


def test__templater_jinja_dynamic_variable_no_violations():
    """Test no templater violation for variable defined within template."""
    t = JinjaTemplater(override_context=dict(blah="foo"))
    instr = """{% if True %}
    {% set some_var %}1{% endset %}
    SELECT {{some_var}}
{% endif %}
"""
    outstr, vs = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert str(outstr) == "\n    \n    SELECT 1\n\n"
    # Check we have no violations.
    assert len(vs) == 0


def test__templater_jinja_error_syntax():
    """Test syntax problems in the jinja templater."""
    t = JinjaTemplater()
    instr = "SELECT {{foo} FROM jinja_error\n"
    outstr, vs = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    # Check we just skip templating.
    assert str(outstr) == instr
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no == 1 for v in vs)


def test__templater_jinja_error_catastrophic():
    """Test error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah=7))
    instr = JINJA_STRING
    outstr, vs = t.process(
        in_str=instr, fname="test", config=FluffConfig(overrides={"dialect": "ansi"})
    )
    assert not outstr
    assert len(vs) > 0


def test__templater_jinja_error_macro_path_does_not_exist():
    """Tests that an error is raised if macro path doesn't exist."""
    with pytest.raises(ValueError) as e:
        JinjaTemplater().template_builder(
            config=FluffConfig.from_path(
                "test/fixtures/templater/jinja_macro_path_does_not_exist"
            )
        )
    assert str(e.value).startswith("Path does not exist")


def test__templater_jinja_lint_empty():
    """Check that parsing a file which renders to an empty string.

    No exception should be raised, but the parsed tree should be None.
    """
    lntr = Linter(dialect="ansi")
    parsed = lntr.parse_string(in_str='{{ "" }}')
    assert parsed.templated_file.source_str == '{{ "" }}'
    assert parsed.templated_file.templated_str == ""
    assert parsed.tree is None


def assert_structure(yaml_loader, path, code_only=True, include_meta=False):
    """Check that a parsed sql file matches the yaml file with the same name."""
    lntr = Linter()
    p = list(lntr.parse_path(path + ".sql"))
    parsed = p[0][0]
    if parsed is None:
        print(p)
        raise RuntimeError(p[0][1])
    # Whitespace is important here to test how that's treated
    tpl = parsed.to_tuple(code_only=code_only, show_raw=True, include_meta=include_meta)
    # Check nothing unparsable
    if "unparsable" in parsed.type_set():
        print(parsed.stringify())
        raise ValueError("Input file is unparsable.")
    _hash, expected = yaml_loader(path + ".yml")
    assert tpl == expected


@pytest.mark.parametrize(
    "subpath,code_only,include_meta",
    [
        # Config Scalar
        ("jinja_a/jinja", True, False),
        # Macros
        ("jinja_b/jinja", False, False),
        # dbt builtins
        ("jinja_c_dbt/dbt_builtins_config", True, False),
        ("jinja_c_dbt/dbt_builtins_is_incremental", True, False),
        ("jinja_c_dbt/dbt_builtins_ref", True, False),
        ("jinja_c_dbt/dbt_builtins_source", True, False),
        ("jinja_c_dbt/dbt_builtins_this", True, False),
        ("jinja_c_dbt/dbt_builtins_var_default", True, False),
        # do directive
        ("jinja_e/jinja", True, False),
        # case sensitivity and python literals
        ("jinja_f/jinja", True, False),
        # Macro loading from a folder
        ("jinja_g_macros/jinja", True, False),
        # jinja raw tag
        ("jinja_h_macros/jinja", True, False),
        ("jinja_i_raw/raw_tag", True, False),
        ("jinja_i_raw/raw_tag_2", True, False),
        # Library Loading from a folder
        ("jinja_j_libraries/jinja", True, False),
        # Priority of macros
        ("jinja_k_config_override_path_macros/jinja", True, False),
        # Placeholders and metas
        ("jinja_l_metas/001", False, True),
        ("jinja_l_metas/002", False, True),
        ("jinja_l_metas/003", False, True),
        ("jinja_l_metas/004", False, True),
        ("jinja_l_metas/005", False, True),
        ("jinja_l_metas/006", False, True),
        # Library Loading from a folder when library is module
        ("jinja_m_libraries_module/jinja", True, False),
        ("jinja_n_nested_macros/jinja", True, False),
        # Test more dbt configurations
        ("jinja_o_config_override_dbt_builtins/override_dbt_builtins", True, False),
        ("jinja_p_disable_dbt_builtins/disable_dbt_builtins", True, False),
        # Load all the macros
        ("jinja_q_multiple_path_macros/jinja", True, False),
    ],
)
def test__templater_full(subpath, code_only, include_meta, yaml_loader, caplog):
    """Check structure can be parsed from jinja templated files."""
    # Log the templater and lexer throughout this test
    caplog.set_level(logging.DEBUG, logger="sqlfluff.templater")
    caplog.set_level(logging.DEBUG, logger="sqlfluff.lexer")

    assert_structure(
        yaml_loader,
        "test/fixtures/templater/" + subpath,
        code_only=code_only,
        include_meta=include_meta,
    )


def test__templater_jinja_block_matching(caplog):
    """Test the block UUID matching works with a complicated case."""
    caplog.set_level(logging.DEBUG, logger="sqlfluff.lexer")
    path = "test/fixtures/templater/jinja_l_metas/002.sql"
    # Parse the file.
    p = list(Linter().parse_path(path))
    parsed = p[0][0]
    assert parsed
    # We only care about the template elements
    template_segments = [
        seg
        for seg in parsed.raw_segments
        if seg.is_type("template_loop", "placeholder")
    ]

    # Group them together by block UUID
    assert all(
        seg.block_uuid for seg in template_segments
    ), "All templated segments should have a block uuid!"
    grouped = defaultdict(list)
    for seg in template_segments:
        grouped[seg.block_uuid].append(seg.pos_marker.working_loc)

    print(grouped)

    # Now the matching block IDs should be found at the following positions.
    # NOTE: These are working locations in the rendered file.
    groups = {
        "for actions clause 1": [(6, 5), (9, 5), (12, 5), (15, 5)],
        "for actions clause 2": [(17, 5), (21, 5), (29, 5), (37, 5)],
        "if loop.first 1": [(18, 9), (20, 9)],
        "if loop.first 2": [(22, 9), (28, 9)],
        "if loop.first 3": [(30, 9), (36, 9)],
    }

    # Check all are accounted for:
    for clause in groups.keys():
        for block_uuid, locations in grouped.items():
            if groups[clause] == locations:
                print(f"Found {clause}, locations with UUID: {block_uuid}")
                break
        else:
            raise ValueError(f"Couldn't find appropriate grouping of blocks: {clause}")


@pytest.mark.parametrize(
    "test,result",
    [
        ("", []),
        ("foo", [("foo", "literal", 0)]),
        (
            "foo {{bar}} z ",
            [
                ("foo ", "literal", 0),
                ("{{bar}}", "templated", 4),
                (" z ", "literal", 11),
            ],
        ),
        (
            (
                "SELECT {# A comment #} {{field}} {% for i in [1, 3]%}, "
                "fld_{{i}}{% endfor %} FROM my_schema.{{my_table}} "
            ),
            [
                ("SELECT ", "literal", 0),
                ("{# A comment #}", "comment", 7),
                (" ", "literal", 22),
                ("{{field}}", "templated", 23),
                (" ", "literal", 32),
                ("{% for i in [1, 3]%}", "block_start", 33),
                (", fld_", "literal", 53),
                ("{{i}}", "templated", 59),
                ("{% endfor %}", "block_end", 64),
                (" FROM my_schema.", "literal", 76),
                ("{{my_table}}", "templated", 92),
                (" ", "literal", 104),
            ],
        ),
        (
            "{% set thing %}FOO{% endset %} BAR",
            [
                ("{% set thing %}", "block_start", 0),
                ("FOO", "literal", 15),
                ("{% endset %}", "block_end", 18),
                (" BAR", "literal", 30),
            ],
        ),
        (
            # Tests Jinja "block assignment" syntax. Also tests the use of
            # template substitution within the block: {{ "dev" }}.
            """{% set my_query %}
select 1 from foobarfoobarfoobarfoobar_{{ "dev" }}
{% endset %}
{{ my_query }}
""",
            [
                ("{% set my_query %}", "block_start", 0),
                ("\nselect 1 from foobarfoobarfoobarfoobar_", "literal", 18),
                ('{{ "dev" }}', "templated", 58),
                ("\n", "literal", 69),
                ("{% endset %}", "block_end", 70),
                ("\n", "literal", 82),
                ("{{ my_query }}", "templated", 83),
                ("\n", "literal", 97),
            ],
        ),
    ],
)
def test__templater_jinja_slice_template(test, result):
    """Test _slice_template."""
    templater = JinjaTemplater()
    env, live_context, make_template = templater.template_builder()
    analyzer = JinjaAnalyzer(test, env)
    analyzer.analyze(make_template)
    resp = analyzer.raw_sliced
    # check contiguous (unless there's a comment in it)
    if "{#" not in test:
        assert "".join(elem.raw for elem in resp) == test
        # check indices
        idx = 0
        for raw_slice in resp:
            assert raw_slice.source_idx == idx
            idx += len(raw_slice.raw)
    # Check total result
    assert [
        (raw_slice.raw, raw_slice.slice_type, raw_slice.source_idx)
        for raw_slice in resp
    ] == result


def _statement(*args, **kwargs):
    return "_statement"


def _load_result(*args, **kwargs):
    return "_load_result"


@pytest.mark.parametrize(
    "raw_file,override_context,result",
    [
        ("", None, []),
        ("foo", None, [("literal", slice(0, 3, None), slice(0, 3, None))]),
        # Example with no loops
        (
            "SELECT {{blah}}, boo {# comment #} from something",
            dict(blah="foobar"),
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("templated", slice(7, 15, None), slice(7, 13, None)),
                ("literal", slice(15, 21, None), slice(13, 19, None)),
                ("comment", slice(21, 34, None), slice(19, 19, None)),
                ("literal", slice(34, 49, None), slice(19, 34, None)),
            ],
        ),
        # Example with loops
        (
            (
                "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, "
                "fld_{{i}}_x{% endfor %} FROM my_schema.{{my_table}} "
            ),
            dict(field="foobar", my_table="barfoo"),
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("comment", slice(7, 22, None), slice(7, 7, None)),
                ("literal", slice(22, 23, None), slice(7, 8, None)),
                ("templated", slice(23, 32, None), slice(8, 14, None)),
                ("literal", slice(32, 33, None), slice(14, 15, None)),
                ("block_start", slice(33, 56, None), slice(15, 15, None)),
                ("literal", slice(56, 62, None), slice(15, 21, None)),
                ("templated", slice(62, 67, None), slice(21, 22, None)),
                ("literal", slice(67, 69, None), slice(22, 24, None)),
                ("block_end", slice(69, 81, None), slice(24, 24, None)),
                ("literal", slice(56, 62, None), slice(24, 30, None)),
                ("templated", slice(62, 67, None), slice(30, 31, None)),
                ("literal", slice(67, 69, None), slice(31, 33, None)),
                ("block_end", slice(69, 81, None), slice(33, 33, None)),
                ("literal", slice(56, 62, None), slice(33, 39, None)),
                ("templated", slice(62, 67, None), slice(39, 40, None)),
                ("literal", slice(67, 69, None), slice(40, 42, None)),
                ("block_end", slice(69, 81, None), slice(42, 42, None)),
                ("literal", slice(81, 97, None), slice(42, 58, None)),
                ("templated", slice(97, 109, None), slice(58, 64, None)),
                ("literal", slice(109, 110, None), slice(64, 65, None)),
            ],
        ),
        # Example with loops (and utilising the end slice code)
        (
            (
                "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, "
                "fld_{{i}}{% endfor %} FROM my_schema.{{my_table}} "
            ),
            dict(field="foobar", my_table="barfoo"),
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("comment", slice(7, 22, None), slice(7, 7, None)),
                ("literal", slice(22, 23, None), slice(7, 8, None)),
                ("templated", slice(23, 32, None), slice(8, 14, None)),
                ("literal", slice(32, 33, None), slice(14, 15, None)),
                ("block_start", slice(33, 56, None), slice(15, 15, None)),
                ("literal", slice(56, 62, None), slice(15, 21, None)),
                ("templated", slice(62, 67, None), slice(21, 22, None)),
                ("block_end", slice(67, 79, None), slice(22, 22, None)),
                ("literal", slice(56, 62, None), slice(22, 28, None)),
                ("templated", slice(62, 67, None), slice(28, 29, None)),
                ("block_end", slice(67, 79, None), slice(29, 29, None)),
                ("literal", slice(56, 62, None), slice(29, 35, None)),
                ("templated", slice(62, 67, None), slice(35, 36, None)),
                ("block_end", slice(67, 79, None), slice(36, 36, None)),
                ("literal", slice(79, 95, None), slice(36, 52, None)),
                ("templated", slice(95, 107, None), slice(52, 58, None)),
                ("literal", slice(107, 108, None), slice(58, 59, None)),
            ],
        ),
        # Test a trailing split, and some variables which don't refer anything.
        (
            "{{ config(materialized='view') }}\n\nSELECT 1 FROM {{ source('finance', "
            "'reconciled_cash_facts') }}\n\n",
            dict(
                config=lambda *args, **kwargs: "",
                source=lambda *args, **kwargs: "finance_reconciled_cash_facts",
            ),
            [
                ("templated", slice(0, 33, None), slice(0, 0, None)),
                ("literal", slice(33, 49, None), slice(0, 16, None)),
                ("templated", slice(49, 97, None), slice(16, 45, None)),
                ("literal", slice(97, 99, None), slice(45, 47, None)),
            ],
        ),
        # Test splitting with a loop.
        (
            "SELECT\n    "
            "{% for i in [1, 2, 3] %}\n        , "
            "c_{{i}}+42 AS the_meaning_of_li{{ 'f' * i }}\n    "
            "{% endfor %}\n"
            "FROM my_table",
            None,
            [
                ("literal", slice(0, 11, None), slice(0, 11, None)),
                ("block_start", slice(11, 35, None), slice(11, 11, None)),
                ("literal", slice(35, 48, None), slice(11, 24, None)),
                ("templated", slice(48, 53, None), slice(24, 25, None)),
                ("literal", slice(53, 77, None), slice(25, 49, None)),
                ("templated", slice(77, 90, None), slice(49, 50, None)),
                ("literal", slice(90, 95, None), slice(50, 55, None)),
                ("block_end", slice(95, 107, None), slice(55, 55, None)),
                ("literal", slice(35, 48, None), slice(55, 68, None)),
                ("templated", slice(48, 53, None), slice(68, 69, None)),
                ("literal", slice(53, 77, None), slice(69, 93, None)),
                ("templated", slice(77, 90, None), slice(93, 95, None)),
                ("literal", slice(90, 95, None), slice(95, 100, None)),
                ("block_end", slice(95, 107, None), slice(100, 100, None)),
                ("literal", slice(35, 48, None), slice(100, 113, None)),
                ("templated", slice(48, 53, None), slice(113, 114, None)),
                ("literal", slice(53, 77, None), slice(114, 138, None)),
                ("templated", slice(77, 90, None), slice(138, 141, None)),
                ("literal", slice(90, 95, None), slice(141, 146, None)),
                ("block_end", slice(95, 107, None), slice(146, 146, None)),
                ("literal", slice(107, 121, None), slice(146, 160, None)),
            ],
        ),
        # Test an example where a block is removed entirely.
        (
            "{% set thing %}FOO{% endset %} SELECT 1",
            None,
            [
                ("block_start", slice(0, 15, None), slice(0, 0, None)),
                ("literal", slice(15, 18, None), slice(0, 0, None)),
                ("block_end", slice(18, 30, None), slice(0, 0, None)),
                ("literal", slice(30, 39, None), slice(0, 9, None)),
            ],
        ),
        (
            # Tests Jinja "include" directive.
            """{% include 'subdir/include_comment.sql' %}

SELECT 1
""",
            None,
            [
                ("templated", slice(0, 42, None), slice(0, 18, None)),
                ("literal", slice(42, 53, None), slice(18, 29, None)),
            ],
        ),
        (
            # Tests Jinja "from import" directive..
            """{% from 'echo.sql' import echo %}
{% from 'echoecho.sql' import echoecho %}

SELECT
    {{ echo("foo") }},
    {{ echoecho("bar") }}
""",
            None,
            [
                ("block_start", slice(0, 33, None), slice(0, 0, None)),
                ("literal", slice(33, 34, None), slice(0, 1, None)),
                ("block_start", slice(34, 75, None), slice(1, 1, None)),
                ("literal", slice(75, 88, None), slice(1, 14, None)),
                ("templated", slice(88, 105, None), slice(14, 19, None)),
                ("literal", slice(105, 111, None), slice(19, 25, None)),
                ("templated", slice(111, 132, None), slice(25, 34, None)),
                ("literal", slice(132, 133, None), slice(34, 35, None)),
            ],
        ),
        (
            # Tests issue 2541, a bug where the {%- endfor %} was causing
            # IndexError: list index out of range.
            """{% for x in ['A', 'B'] %}
    {% if x != 'A' %}
    SELECT 'E'
    {% endif %}
{%- endfor %}
""",
            None,
            [
                ("block_start", slice(0, 25, None), slice(0, 0, None)),
                ("literal", slice(25, 30, None), slice(0, 5, None)),
                ("block_start", slice(30, 47, None), slice(5, 5, None)),
                ("block_end", slice(67, 78, None), slice(5, 5, None)),
                ("literal", slice(78, 79, None), slice(5, 5, None)),
                ("block_end", slice(79, 92, None), slice(5, 5, None)),
                ("literal", slice(25, 30, None), slice(5, 10, None)),
                ("block_start", slice(30, 47, None), slice(10, 10, None)),
                ("literal", slice(47, 67, None), slice(10, 30, None)),
                ("block_end", slice(67, 78, None), slice(30, 30, None)),
                ("literal", slice(78, 79, None), slice(30, 30, None)),
                ("block_end", slice(79, 92, None), slice(30, 30, None)),
                ("literal", slice(92, 93, None), slice(30, 31, None)),
            ],
        ),
        (
            # Similar to the test above for issue 2541, but it's even trickier:
            # whitespace control everywhere and NO NEWLINES or other characters
            # between Jinja segments. In order to get a thorough-enough trace,
            # JinjaTracer has to build the alternate template with whitespace
            # control removed, as this increases the amount of trace output.
            "{%- for x in ['A', 'B'] -%}"
            "{%- if x == 'B' -%}"
            "SELECT 'B';"
            "{%- endif -%}"
            "{%- if x == 'A' -%}"
            "SELECT 'A';"
            "{%- endif -%}"
            "{%- endfor -%}",
            None,
            [
                ("block_start", slice(0, 27, None), slice(0, 0, None)),
                ("block_start", slice(27, 46, None), slice(0, 0, None)),
                ("block_end", slice(57, 70, None), slice(0, 0, None)),
                ("block_start", slice(70, 89, None), slice(0, 0, None)),
                ("literal", slice(89, 100, None), slice(0, 11, None)),
                ("block_end", slice(100, 113, None), slice(11, 11, None)),
                ("block_end", slice(113, 127, None), slice(11, 11, None)),
                ("block_start", slice(27, 46, None), slice(11, 11, None)),
                ("literal", slice(46, 57, None), slice(11, 22, None)),
                ("block_end", slice(57, 70, None), slice(22, 22, None)),
                ("block_start", slice(70, 89, None), slice(22, 22, None)),
                ("block_end", slice(100, 113, None), slice(22, 22, None)),
                ("block_end", slice(113, 127, None), slice(22, 22, None)),
            ],
        ),
        (
            # Test for issue 2786. Also lots of whitespace control. In this
            # case, removing whitespace control alone wasn't enough. In order
            # to get a good trace, JinjaTracer had to be updated so the
            # alternate template included output for the discarded whitespace.
            """select
    id,
    {%- for features in ["value4", "value5"] %}
        {%- if features in ["value7"] %}
            {{features}}
            {%- if not loop.last -%},{% endif %}
        {%- else -%}
            {{features}}
            {%- if not loop.last -%},{% endif %}
        {%- endif -%}
    {%- endfor %}
from my_table
""",
            None,
            [
                ("literal", slice(0, 14, None), slice(0, 14, None)),
                ("literal", slice(14, 19, None), slice(14, 14, None)),
                ("block_start", slice(19, 62, None), slice(14, 14, None)),
                ("literal", slice(62, 71, None), slice(14, 14, None)),
                ("block_start", slice(71, 103, None), slice(14, 14, None)),
                ("block_mid", slice(186, 198, None), slice(14, 14, None)),
                ("literal", slice(198, 211, None), slice(14, 14, None)),
                ("templated", slice(211, 223, None), slice(14, 20, None)),
                ("literal", slice(223, 236, None), slice(20, 20, None)),
                ("block_start", slice(236, 260, None), slice(20, 20, None)),
                ("literal", slice(260, 261, None), slice(20, 21, None)),
                ("block_end", slice(261, 272, None), slice(21, 21, None)),
                ("literal", slice(272, 281, None), slice(21, 21, None)),
                ("block_end", slice(281, 294, None), slice(21, 21, None)),
                ("literal", slice(294, 299, None), slice(21, 21, None)),
                ("block_end", slice(299, 312, None), slice(21, 21, None)),
                ("literal", slice(62, 71, None), slice(21, 21, None)),
                ("block_start", slice(71, 103, None), slice(21, 21, None)),
                ("block_mid", slice(186, 198, None), slice(21, 21, None)),
                ("literal", slice(198, 211, None), slice(21, 21, None)),
                ("templated", slice(211, 223, None), slice(21, 27, None)),
                ("literal", slice(223, 236, None), slice(27, 27, None)),
                ("block_start", slice(236, 260, None), slice(27, 27, None)),
                ("block_end", slice(261, 272, None), slice(27, 27, None)),
                ("literal", slice(272, 281, None), slice(27, 27, None)),
                ("block_end", slice(281, 294, None), slice(27, 27, None)),
                ("literal", slice(294, 299, None), slice(27, 27, None)),
                ("block_end", slice(299, 312, None), slice(27, 27, None)),
                ("literal", slice(312, 327, None), slice(27, 42, None)),
            ],
        ),
        (
            # Test for issue 2835. There's no space between "col" and "="
            """{% set col= "col1" %}
SELECT {{ col }}
""",
            None,
            [
                ("block_start", slice(0, 21, None), slice(0, 0, None)),
                ("literal", slice(21, 29, None), slice(0, 8, None)),
                ("templated", slice(29, 38, None), slice(8, 12, None)),
                ("literal", slice(38, 39, None), slice(12, 13, None)),
            ],
        ),
        (
            # Another test for issue 2835. The {% for %} loop inside the
            # {% set %} caused JinjaTracer to think the {% set %} ended
            # at the {% endfor %}
            """{% set some_part_of_the_query %}
    {% for col in ["col1"] %}
    {{col}}
    {% endfor %}
{% endset %}

SELECT {{some_part_of_the_query}}
FROM SOME_TABLE
""",
            None,
            [
                ("block_start", slice(0, 32, None), slice(0, 0, None)),
                ("literal", slice(32, 37, None), slice(0, 0, None)),
                ("block_start", slice(37, 62, None), slice(0, 0, None)),
                ("literal", slice(62, 67, None), slice(0, 0, None)),
                ("templated", slice(67, 74, None), slice(0, 0, None)),
                ("literal", slice(74, 79, None), slice(0, 0, None)),
                ("block_end", slice(79, 91, None), slice(0, 0, None)),
                ("literal", slice(91, 92, None), slice(0, 0, None)),
                ("block_end", slice(92, 104, None), slice(0, 0, None)),
                ("literal", slice(104, 113, None), slice(0, 9, None)),
                ("templated", slice(113, 139, None), slice(9, 29, None)),
                ("literal", slice(139, 156, None), slice(29, 46, None)),
            ],
        ),
        (
            # Third test for issue 2835. This was the original SQL provided in
            # the issue report.
            """{% set whitelisted= [
    {'name': 'COL_1'},
    {'name': 'COL_2'},
    {'name': 'COL_3'}
] %}

{% set some_part_of_the_query %}
    {% for col in whitelisted %}
    {{col.name}}{{ ", " if not loop.last }}
    {% endfor %}
{% endset %}

SELECT {{some_part_of_the_query}}
FROM SOME_TABLE
""",
            None,
            [
                ("block_start", slice(0, 94, None), slice(0, 0, None)),
                ("literal", slice(94, 96, None), slice(0, 2, None)),
                ("block_start", slice(96, 128, None), slice(2, 2, None)),
                ("literal", slice(128, 133, None), slice(2, 2, None)),
                ("block_start", slice(133, 161, None), slice(2, 2, None)),
                ("literal", slice(161, 166, None), slice(2, 2, None)),
                ("templated", slice(166, 178, None), slice(2, 2, None)),
                ("templated", slice(178, 205, None), slice(2, 2, None)),
                ("literal", slice(205, 210, None), slice(2, 2, None)),
                ("block_end", slice(210, 222, None), slice(2, 2, None)),
                ("literal", slice(222, 223, None), slice(2, 2, None)),
                ("block_end", slice(223, 235, None), slice(2, 2, None)),
                ("literal", slice(235, 244, None), slice(2, 11, None)),
                ("templated", slice(244, 270, None), slice(11, 66, None)),
                ("literal", slice(270, 287, None), slice(66, 83, None)),
            ],
        ),
        (
            # Test for issue 2822: Handle slicing when there's no newline after
            # the Jinja block end.
            "{% if true %}\nSELECT 1 + 1\n{%- endif %}",
            None,
            [
                ("block_start", slice(0, 13, None), slice(0, 0, None)),
                ("literal", slice(13, 26, None), slice(0, 13, None)),
                ("literal", slice(26, 27, None), slice(13, 13, None)),
                ("block_end", slice(27, 39, None), slice(13, 13, None)),
            ],
        ),
        (
            # Test for issue 3434: Handle {% block %}.
            "SELECT {% block table_name %}block_contents{% endblock %} "
            "FROM {{ self.table_name() }}\n",
            None,
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("literal", slice(29, 43, None), slice(7, 21, None)),
                ("block_start", slice(7, 29, None), slice(21, 21, None)),
                ("literal", slice(29, 43, None), slice(21, 21, None)),
                ("block_end", slice(43, 57, None), slice(21, 21, None)),
                ("literal", slice(57, 63, None), slice(21, 27, None)),
                ("templated", slice(63, 86, None), slice(27, 27, None)),
                ("literal", slice(29, 43, None), slice(27, 41, None)),
                ("literal", slice(86, 87, None), slice(41, 42, None)),
            ],
        ),
        (
            # Another test for issue 3434: Similar to the first, but uses
            # the block inside a loop.
            """{% block table_name %}block_contents{% endblock %}
SELECT
{% for j in [4, 5, 6] %}
FROM {{ j }}{{ self.table_name() }}
{% endfor %}
""",
            None,
            [
                ("literal", slice(22, 36, None), slice(0, 14, None)),
                ("block_start", slice(0, 22, None), slice(14, 14, None)),
                ("literal", slice(22, 36, None), slice(14, 14, None)),
                ("block_end", slice(36, 50, None), slice(14, 14, None)),
                ("literal", slice(50, 58, None), slice(14, 22, None)),
                ("block_start", slice(58, 82, None), slice(22, 22, None)),
                ("literal", slice(82, 88, None), slice(22, 28, None)),
                ("templated", slice(88, 95, None), slice(28, 29, None)),
                ("templated", slice(95, 118, None), slice(29, 29, None)),
                ("literal", slice(22, 36, None), slice(29, 43, None)),
                ("literal", slice(118, 119, None), slice(43, 44, None)),
                ("block_end", slice(119, 131, None), slice(44, 44, None)),
                ("literal", slice(82, 88, None), slice(44, 50, None)),
                ("templated", slice(88, 95, None), slice(50, 51, None)),
                ("templated", slice(95, 118, None), slice(51, 51, None)),
                ("literal", slice(22, 36, None), slice(51, 65, None)),
                ("literal", slice(118, 119, None), slice(65, 66, None)),
                ("block_end", slice(119, 131, None), slice(66, 66, None)),
                ("literal", slice(82, 88, None), slice(66, 72, None)),
                ("templated", slice(88, 95, None), slice(72, 73, None)),
                ("templated", slice(95, 118, None), slice(73, 73, None)),
                ("literal", slice(22, 36, None), slice(73, 87, None)),
                ("literal", slice(118, 119, None), slice(87, 88, None)),
                ("block_end", slice(119, 131, None), slice(88, 88, None)),
                ("literal", slice(131, 132, None), slice(88, 89, None)),
            ],
        ),
        (
            """{{ statement('variables', fetch_result=true) }}
""",
            dict(
                statement=_statement,
                load_result=_load_result,
            ),
            [
                ("templated", slice(0, 47, None), slice(0, 10, None)),
                ("literal", slice(47, 48, None), slice(10, 11, None)),
            ],
        ),
        (
            "{% call statement('variables', fetch_result=true) %}"
            "select 1 as test"
            "{% endcall %}\n",
            dict(
                statement=_statement,
                load_result=_load_result,
            ),
            [
                ("templated", slice(0, 52, None), slice(0, 10, None)),
                ("literal", slice(52, 68, None), slice(10, 10, None)),
                ("block_end", slice(68, 81, None), slice(10, 10, None)),
                ("literal", slice(81, 82, None), slice(10, 11, None)),
            ],
        ),
    ],
)
def test__templater_jinja_slice_file(raw_file, override_context, result, caplog):
    """Test slice_file."""
    templater = JinjaTemplater(override_context=override_context)
    env, live_context, make_template = templater.template_builder(
        config=FluffConfig.from_path(
            "test/fixtures/templater/jinja_slice_template_macros"
        )
    )

    templated_file = make_template(raw_file).render()
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        raw_sliced, sliced_file, templated_str = templater.slice_file(
            raw_file, templated_file, make_template=make_template
        )
    # Create a TemplatedFile from the results. This runs some useful sanity
    # checks.
    _ = TemplatedFile(raw_file, "<<DUMMY>>", templated_str, sliced_file, raw_sliced)
    # Check contiguous on the TEMPLATED VERSION
    print(sliced_file)
    prev_slice = None
    for elem in sliced_file:
        print(elem)
        if prev_slice:
            assert elem[2].start == prev_slice.stop
        prev_slice = elem[2]
    # Check that all literal segments have a raw slice
    for elem in sliced_file:
        if elem[0] == "literal":
            assert elem[1] is not None
    # check result
    actual = [
        (
            templated_file_slice.slice_type,
            templated_file_slice.source_slice,
            templated_file_slice.templated_slice,
        )
        for templated_file_slice in sliced_file
    ]
    assert actual == result


def test__templater_jinja_large_file_check():
    """Test large file skipping.

    The check is separately called on each .process() method
    so it makes sense to test a few templaters.
    """
    # First check we can process the file normally without specific config.
    # i.e. check the defaults work and the default is high.
    JinjaTemplater().process(
        in_str="SELECT 1",
        fname="<string>",
        config=FluffConfig(overrides={"dialect": "ansi"}),
    )
    # Second check setting the value low disables the check
    JinjaTemplater().process(
        in_str="SELECT 1",
        fname="<string>",
        config=FluffConfig(
            overrides={"dialect": "ansi", "large_file_skip_char_limit": 0}
        ),
    )
    # Finally check we raise a skip exception when config is set low.
    with pytest.raises(SQLFluffSkipFile) as excinfo:
        JinjaTemplater().process(
            in_str="SELECT 1",
            fname="<string>",
            config=FluffConfig(
                overrides={"dialect": "ansi", "large_file_skip_char_limit": 2},
            ),
        )

    assert "Length of file" in str(excinfo.value)


@pytest.mark.parametrize(
    "ignore, expected_violation",
    [
        (
            "",
            SQLTemplaterError(
                "Undefined jinja template variable: 'test_event_cadence'"
            ),
        ),
        ("templating", None),
    ],
)
def test_jinja_undefined_callable(ignore, expected_violation):
    """Test undefined callable returns TemplatedFile and sensible error."""
    templater = JinjaTemplater()
    templated_file, violations = templater.process(
        in_str="""WITH streams_cadence_test AS (
{{  test_event_cadence(
    model= ref('fct_recording_progression_stream'),
    grouping_column='archive_id', time_column='timestamp',
    date_part='minute', threshold=1) }}
)
SELECT * FROM final
""",
        fname="test.sql",
        config=FluffConfig(overrides={"dialect": "ansi", "ignore": ignore}),
    )
    # This was previously failing to process, due to UndefinedRecorder not
    # supporting __call__(), also Jinja thinking it was not *safe* to call.
    assert templated_file is not None
    if expected_violation:
        assert len(violations) == 1
        isinstance(violations[0], type(expected_violation))
        assert str(violations[0]) == str(expected_violation)
    else:
        assert len(violations) == 0


def test_dummy_undefined_fail_with_undefined_error():
    """Tests that a recursion error bug no longer occurs."""
    ud = DummyUndefined("name")
    with pytest.raises(UndefinedError):
        # This was previously causing a recursion error.
        ud._fail_with_undefined_error()


def test_undefined_magic_methods():
    """Test all the magic methods defined on DummyUndefined."""
    ud = DummyUndefined("name")

    # _self_impl
    assert ud + ud is ud
    assert ud - ud is ud
    assert ud / ud is ud
    assert ud // ud is ud
    assert ud % ud is ud
    assert ud**ud is ud
    assert +ud is ud
    assert -ud is ud
    assert ud << ud is ud
    assert ud[ud] is ud
    assert ~ud is ud
    assert ud(ud) is ud

    # _bool_impl
    assert ud and ud
    assert ud or ud
    assert ud ^ ud
    assert bool(ud)
    assert ud < ud
    assert ud <= ud
    assert ud == ud
    assert ud != ud
    assert ud >= ud
    assert ud > ud

    assert ud + ud is ud
