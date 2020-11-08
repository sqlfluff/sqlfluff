"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import JinjaTemplater
from sqlfluff.core import Linter, FluffConfig


JINJA_STRING = "SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %} WHERE {{condition}}\n\n"


def test__templater_jinja():
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplater(override_context=dict(blah="foo", condition="a < 10"))
    instr = JINJA_STRING
    outstr, _ = t.process(instr, config=FluffConfig())
    assert str(outstr) == "SELECT * FROM f, o, o WHERE a < 10\n\n"


def test__templater_jinja_error():
    """Test error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah="foo"))
    instr = JINJA_STRING
    outstr, vs = t.process(instr, config=FluffConfig())
    assert str(outstr) == "SELECT * FROM f, o, o WHERE \n\n"
    # Check we have violations.
    assert len(vs) > 0


def test__templater_jinja_error_catatrophic():
    """Test error handling in the jinja templater."""
    t = JinjaTemplater(override_context=dict(blah=7))
    instr = JINJA_STRING
    outstr, vs = t.process(instr, config=FluffConfig())
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
def test__templater_full(subpath, code_only, yaml_loader):
    """Check structure can be parsed from jinja templated files."""
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
                # NB: Comments should be ignore from the slice.
                # ("{# A comment #}", "comment", 7),
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
                # NB: Comment results in two literals
                ("literal", slice(34, 49, None), slice(19, 34, None)),
            ],
        ),
        # Example with loops
        (
            "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, fld_{{i}}_x{% endfor %} FROM my_schema.{{my_table}} ",
            "SELECT  foobar , fld_1_x, fld_3_x, fld_7_x FROM my_schema.barfoo ",
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("literal", slice(22, 23, None), slice(7, 8, None)),
                ("templated", slice(23, 56, None), slice(8, 15, None)),
                ("literal", slice(56, 62, None), slice(15, 21, None)),
                ("templated", slice(62, 67, None), slice(21, 22, None)),
                ("literal", slice(67, 69, None), slice(22, 24, None)),
                ("literal", slice(56, 62, None), slice(24, 30, None)),
                ("templated", slice(62, 67, None), slice(30, 31, None)),
                ("literal", slice(67, 69, None), slice(31, 33, None)),
                ("literal", slice(56, 62, None), slice(33, 39, None)),
                ("templated", slice(62, 67, None), slice(39, 40, None)),
                ("literal", slice(67, 69, None), slice(40, 42, None)),
                ("literal", slice(81, 97, None), slice(42, 58, None)),
            ],
        ),
        # Example with loops (and utilising the end slice code)
        (
            "SELECT {# A comment #} {{field}} {% for i in [1, 3, 7]%}, fld_{{i}}{% endfor %} FROM my_schema.{{my_table}} ",
            "SELECT  foobar , fld_1, fld_3, fld_7 FROM my_schema.barfoo",
            [
                ("literal", slice(0, 7, None), slice(0, 7, None)),
                ("literal", slice(22, 23, None), slice(7, 8, None)),
                ("templated", slice(23, 56, None), slice(8, 15, None)),
                ("literal", slice(56, 62, None), slice(15, 21, None)),
                ("templated", slice(56, 67, None), slice(21, 22, None)),
                ("literal", slice(56, 62, None), slice(22, 28, None)),
                ("templated", slice(56, 67, None), slice(28, 29, None)),
                ("literal", slice(56, 62, None), slice(29, 35, None)),
                ("templated", slice(62, 79, None), slice(35, 36, None)),
                ("literal", slice(79, 95, None), slice(36, 52, None)),
            ],
        ),
    ],
)
def test__templater_jinja_slice_file(raw_file, templated_file, result):
    """Test slice_file."""
    resp = list(
        JinjaTemplater.slice_file(
            raw_file,
            templated_file,
        )
    )
    # Check contigious on the TEMPLATED VERSION
    prev_slice = None
    for elem in resp:
        if prev_slice:
            assert elem[2].start == prev_slice.stop
        prev_slice = elem[2]
    # Check that all literal segments have a raw slice
    for elem in resp:
        if elem[0] == "literal":
            assert elem[1] is not None
    # check result
    assert resp == result
