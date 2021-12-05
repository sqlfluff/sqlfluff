"""Tests for templaters."""

import logging
from typing import List, NamedTuple

import pytest

from sqlfluff.core.templaters import JinjaTemplater
from sqlfluff.core.templaters.jinja import JinjaTracer
from sqlfluff.core import Linter, FluffConfig


JINJA_STRING = "SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %} WHERE {{condition}}\n\n"


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
            "\n\n\nSELECT\n    event_id\n    \n    , campaign\n    \n    , click_item\n    \nFROM events\n            ",
        ),
    ],
    ids=["simple", "unboundlocal_bugfix"],
)
def test__templater_jinja(instr, expected_outstr):
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplater(override_context=dict(blah="foo", condition="a < 10"))
    outstr, _ = t.process(in_str=instr, fname="test", config=FluffConfig())
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
            templated_str="\n\n\nSELECT\n  brand\nFROM\n  table1\nUNION ALL\n\nSELECT\n  brand\nFROM\n  table2\n\n\n",
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
    ],
    ids=lambda case: case.name,
)
def test__templater_jinja_slices(case: RawTemplatedTestCase):
    """Test that Jinja templater slices raw and templated file correctly."""
    t = JinjaTemplater()
    templated_file, _ = t.process(in_str=case.instr, fname="test", config=FluffConfig())
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
    actual_rs_source_list = []
    for rs in templated_file.raw_sliced + [None]:
        if previous_rs:
            if rs:
                actual_source = case.instr[previous_rs.source_idx : rs.source_idx]
            else:
                actual_source = case.instr[previous_rs.source_idx :]
            actual_rs_source_list.append(actual_source)
        previous_rs = rs
    assert actual_rs_source_list == case.expected_raw_sliced__source_list


def test__templater_jinja_error_variable():
    """Test missing variable error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah="foo"))
    instr = JINJA_STRING
    outstr, vs = t.process(in_str=instr, fname="test", config=FluffConfig())
    assert str(outstr) == "SELECT * FROM f, o, o WHERE \n\n"
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no == 1 for v in vs)


def test__templater_jinja_error_syntax():
    """Test syntax problems in the jinja templater."""
    t = JinjaTemplater()
    instr = "SELECT {{foo} FROM jinja_error\n"
    outstr, vs = t.process(in_str=instr, fname="test", config=FluffConfig())
    # Check we just skip templating.
    assert str(outstr) == instr
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no == 1 for v in vs)


def test__templater_jinja_error_catatrophic():
    """Test error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah=7))
    instr = JINJA_STRING
    outstr, vs = t.process(in_str=instr, fname="test", config=FluffConfig())
    assert not outstr
    assert len(vs) > 0


def test__templater_jinja_lint_empty():
    """Check that parsing a file which renders to an empty string.

    No exception should be raised, but the parsed tree should be None.
    """
    lntr = Linter()
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
        raise ValueError("Input file is contains unparsable.")
    _hash, expected = yaml_loader(path + ".yml")
    assert tpl == expected


@pytest.mark.parametrize(
    "subpath,code_only,include_meta",
    [
        # Config Scalar
        ("jinja_a/jinja", True, False),
        # Macros
        ("jinja_b/jinja", False, False),
        # dbt builting
        ("jinja_c_dbt/dbt_builtins", True, False),
        ("jinja_c_dbt/var_default", True, False),
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
        # Library Loading from a folder when library is module
        ("jinja_m_libraries_module/jinja", True, False),
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
            "SELECT {# A comment #} {{field}} {% for i in [1, 3]%}, fld_{{i}}{% endfor %} FROM my_schema.{{my_table}} ",
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
    ],
)
def test__templater_jinja_slice_template(test, result):
    """Test _slice_template."""
    templater = JinjaTemplater()
    env, live_context, make_template = templater.template_builder()
    tracer = JinjaTracer(test, env, make_template)
    resp = list(tracer._slice_template())
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


@pytest.mark.parametrize(
    "raw_file,templated_file,override_context,result",
    [
        ("", "", None, []),
        ("foo", "foo", None, [("literal", slice(0, 3, None), slice(0, 3, None))]),
        # Example with no loops
        (
            "SELECT {{blah}}, boo {# comment #} from something",
            "SELECT foobar, boo  from something",
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
            "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, fld_{{i}}_x{% endfor %} FROM my_schema.{{my_table}} ",
            "SELECT  foobar , fld_1_x, fld_3_x, fld_7_x FROM my_schema.barfoo ",
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
            "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, fld_{{i}}{% endfor %} FROM my_schema.{{my_table}} ",
            "SELECT  foobar , fld_1, fld_3, fld_7 FROM my_schema.barfoo ",
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
            "{{ config(materialized='view') }}\n\nSELECT 1 FROM {{ source('finance', 'reconciled_cash_facts') }}\n\n",
            "\n\nSELECT 1 FROM finance_reconciled_cash_facts\n\n",
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
            "SELECT\n    \n        , "
            "c_1+42 AS the_meaning_of_lif\n    \n        , "
            "c_2+42 AS the_meaning_of_liff\n    \n        , "
            "c_3+42 AS the_meaning_of_lifff\n    \n"
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
            " SELECT 1",
            None,
            [
                ("block_start", slice(0, 15, None), slice(0, 0, None)),
                ("literal", slice(15, 18, None), slice(0, 0, None)),
                ("block_end", slice(18, 30, None), slice(0, 0, None)),
                ("literal", slice(30, 39, None), slice(0, 9, None)),
            ],
        ),
    ],
)
def test__templater_jinja_slice_file(
    raw_file, templated_file, override_context, result, caplog
):
    """Test slice_file."""
    templater = JinjaTemplater(override_context=override_context)
    env, live_context, make_template = templater.template_builder()

    # TODO: Now that we're generating "templated_file", eliminate this field
    # from the parametrized test cases.
    templated_file = make_template(raw_file).render()
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        _, resp, _ = JinjaTemplater.slice_file(
            raw_file, templated_file, make_template=make_template
        )
    # Check contigious on the TEMPLATED VERSION
    print(resp)
    prev_slice = None
    for elem in resp:
        print(elem)
        if prev_slice:
            assert elem[2].start == prev_slice.stop
        prev_slice = elem[2]
    # Check that all literal segments have a raw slice
    for elem in resp:
        if elem[0] == "literal":
            assert elem[1] is not None
    # check result
    actual = [
        (
            templated_file_slice.slice_type,
            templated_file_slice.source_slice,
            templated_file_slice.templated_slice,
        )
        for templated_file_slice in resp
    ]
    assert actual == result
