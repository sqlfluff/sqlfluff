"""Tests for templaters."""

import pytest
import logging

from sqlfluff.core.templaters import JinjaTemplater
from sqlfluff.core import Linter, FluffConfig


JINJA_STRING = "SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %} WHERE {{condition}}\n\n"


def test__templater_jinja():
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplater(override_context=dict(blah="foo", condition="a < 10"))
    instr = JINJA_STRING
    outstr, _ = t.process(in_str=instr, config=FluffConfig())
    assert str(outstr) == "SELECT * FROM f, o, o WHERE a < 10\n\n"


def test__templater_jinja_error_variable():
    """Test missing variable error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah="foo"))
    instr = JINJA_STRING
    outstr, vs = t.process(in_str=instr, config=FluffConfig())
    assert str(outstr) == "SELECT * FROM f, o, o WHERE \n\n"
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no() == 1 for v in vs)


def test__templater_jinja_error_syntax():
    """Test syntax problems in the jinja templater."""
    t = JinjaTemplater()
    instr = "SELECT {{foo} FROM jinja_error\n"
    outstr, vs = t.process(in_str=instr, config=FluffConfig())
    # Check we just skip templating.
    assert str(outstr) == instr
    # Check we have violations.
    assert len(vs) > 0
    # Check one of them is a templating error on line 1
    assert any(v.rule_code() == "TMP" and v.line_no() == 1 for v in vs)


def test__templater_jinja_error_catatrophic():
    """Test error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah=7))
    instr = JINJA_STRING
    outstr, vs = t.process(in_str=instr, config=FluffConfig())
    assert not outstr
    assert len(vs) > 0


def assert_structure(yaml_loader, path, code_only=True):
    """Check that a parsed sql file matches the yaml file with the same name."""
    lntr = Linter()
    p = list(lntr.parse_path(path + ".sql"))
    parsed = p[0][0]
    if parsed is None:
        print(p)
        raise RuntimeError(p[0][1])
    # Whitespace is important here to test how that's treated
    tpl = parsed.to_tuple(code_only=code_only, show_raw=True)
    # Check nothing unparsable
    if "unparsable" in parsed.type_set():
        print(parsed.stringify())
        raise ValueError("Input file is contains unparsable.")
    expected = yaml_loader(path + ".yml")
    assert tpl == expected


@pytest.mark.parametrize(
    "subpath,code_only",
    [
        # Config Scalar
        ("jinja_a/jinja", True),
        # Macros
        ("jinja_b/jinja", False),
        # dbt builting
        ("jinja_c_dbt/dbt_builtins", True),
        # do directive
        ("jinja_e/jinja", True),
        # case sensitivity and python literals
        ("jinja_f/jinja", True),
        # Macro loading from a folder
        ("jinja_g_macros/jinja", True),
    ],
)
def test__templater_full(subpath, code_only, yaml_loader, caplog):
    """Check structure can be parsed from jinja templated files."""
    # Log the templater and lexer throughout this test
    caplog.set_level(logging.DEBUG, logger="sqlfluff.templater")
    caplog.set_level(logging.DEBUG, logger="sqlfluff.lexer")

    assert_structure(
        yaml_loader, "test/fixtures/templater/" + subpath, code_only=code_only
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
    ],
)
def test__templater_jinja_slice_template(test, result):
    """Test _slice_template."""
    resp = list(JinjaTemplater._slice_template(test))
    # check contigious (unless there's a comment in it)
    if "{#" not in test:
        assert "".join(elem[0] for elem in resp) == test
        # check indices
        idx = 0
        for literal, _, pos in resp:
            assert pos == idx
            idx += len(literal)
    # Check total result
    assert resp == result


@pytest.mark.parametrize(
    "raw_file,templated_file,result",
    [
        ("", "", []),
        ("foo", "foo", [("literal", slice(0, 3, None), slice(0, 3, None))]),
        # Example with no loops
        (
            "SELECT {{blah}}, boo {# comment #} from something",
            "SELECT foobar, boo  from something",
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
                ("literal", slice(56, 62, None), slice(24, 30, None)),
                ("templated", slice(62, 67, None), slice(30, 31, None)),
                ("literal", slice(67, 69, None), slice(31, 33, None)),
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
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("comment", slice(7, 22, None), slice(7, 7, None)),
                ("literal", slice(22, 23, None), slice(7, 8, None)),
                ("templated", slice(23, 32, None), slice(8, 14, None)),
                ("literal", slice(32, 33, None), slice(14, 15, None)),
                ("block_start", slice(33, 56, None), slice(15, 15, None)),
                ("literal", slice(56, 62, None), slice(15, 21, None)),
                ("templated", slice(62, 67, None), slice(21, 22, None)),
                ("literal", slice(56, 62, None), slice(22, 28, None)),
                ("templated", slice(62, 67, None), slice(28, 29, None)),
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
            [
                ("templated", slice(0, 33, None), slice(0, 0, None)),
                ("literal", slice(33, 49, None), slice(0, 16, None)),
                ("templated", slice(49, 97, None), slice(16, 45, None)),
                ("literal", slice(97, 99, None), slice(45, 47, None)),
            ],
        ),
        # Test splitting with a loop.
        (
            "SELECT\n    {% for i in [1, 2, 3] %}\n        , c_{{i}}+42 AS the_meaning_of_li{{ 'f' * i }}\n    {% endfor %}\nFROM my_table",
            "SELECT\n    \n        , c_1+42 AS the_meaning_of_lif\n    \n        , c_2+42 AS the_meaning_of_liff\n    \n        , c_3+42 AS the_meaning_of_lifff\n    \nFROM my_table",
            [
                ("literal", slice(0, 11, None), slice(0, 11, None)),
                ("block_start", slice(11, 35, None), slice(11, 11, None)),
                ("literal", slice(35, 48, None), slice(11, 24, None)),
                ("templated", slice(48, 53, None), slice(24, 25, None)),
                ("literal", slice(53, 77, None), slice(25, 49, None)),
                # NB: A templated section which loops back, spans the whole section.
                # We get to match it more accurately here because we're lucky.
                ("templated", slice(77, 95, None), slice(49, 55, None)),
                ("literal", slice(35, 48, None), slice(55, 68, None)),
                ("templated", slice(48, 53, None), slice(68, 69, None)),
                ("literal", slice(53, 77, None), slice(69, 93, None)),
                # NB: A templated section which loops back, spans the whole section.
                # We get to match it more accurately here because we're lucky.
                ("templated", slice(77, 95, None), slice(93, 100, None)),
                ("literal", slice(35, 48, None), slice(100, 113, None)),
                ("templated", slice(48, 53, None), slice(113, 114, None)),
                ("literal", slice(53, 77, None), slice(114, 138, None)),
                ("templated", slice(77, 90, None), slice(138, 141, None)),
                ("literal", slice(90, 95, None), slice(141, 146, None)),
                ("block_end", slice(95, 107, None), slice(146, 146, None)),
                ("literal", slice(107, 121, None), slice(146, 160, None)),
            ],
        ),
    ],
)
def test__templater_jinja_slice_file(raw_file, templated_file, result, caplog):
    """Test slice_file."""
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        _, resp = JinjaTemplater.slice_file(
            raw_file,
            templated_file,
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
    assert resp == result
