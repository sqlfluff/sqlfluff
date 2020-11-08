"""Tests for templaters."""

import pytest
import os

from sqlfluff.core.templaters import (
    RawTemplateInterface,
    templater_selector,
    PythonTemplateInterface,
    JinjaTemplateInterface,
)
from sqlfluff.core import Linter, FluffConfig, SQLTemplaterError
from test.fixtures.dbt.templater import dbt_templater, in_dbt_project_dir, DBT_FLUFF_CONFIG


def test__templater_selection():
    """Test template selection by name."""
    assert templater_selector().__class__ is JinjaTemplateInterface
    assert templater_selector("raw").__class__ is RawTemplateInterface
    assert templater_selector("python").__class__ is PythonTemplateInterface
    assert templater_selector("jinja").__class__ is JinjaTemplateInterface
    with pytest.raises(ValueError):
        templater_selector("afefhlsakufe")


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplateInterface()
    instr = "SELECT * FROM {{blah}}"
    outstr, _ = t.process(instr)
    assert instr == outstr


PYTHON_STRING = "SELECT * FROM {blah}"


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplateInterface(override_context=dict(blah="foo"))
    instr = PYTHON_STRING
    outstr, _ = t.process(instr)
    assert outstr == "SELECT * FROM foo"


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplateInterface(override_context=dict(noblah="foo"))
    instr = PYTHON_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(instr)


JINJA_STRING = "SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %} WHERE {{condition}}\n\n"


def test__templater_jinja():
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplateInterface(override_context=dict(blah="foo", condition="a < 10"))
    instr = JINJA_STRING
    outstr, _ = t.process(instr, config=FluffConfig())
    assert outstr == "SELECT * FROM f, o, o WHERE a < 10\n\n"


def test__templater_jinja_error():
    """Test error handling in the jinja templater."""
    t = JinjaTemplateInterface(override_context=dict(blah="foo"))
    instr = JINJA_STRING
    outstr, vs = t.process(instr, config=FluffConfig())
    assert outstr == "SELECT * FROM f, o, o WHERE \n\n"
    # Check we have violations.
    assert len(vs) > 0


def test__templater_jinja_error_catatrophic():
    """Test error handling in the jinja templater."""
    t = JinjaTemplateInterface(override_context=dict(blah=7))
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


def test__templater_dbt_missing(dbt_templater):
    """Check that a nice error is returned when dbt module is missing."""
    try:
        import dbt  # noqa: F401

        pytest.skip(msg="Dbt is installed")
    except ModuleNotFoundError:
        pass

    with pytest.raises(ModuleNotFoundError, match=r"pip install sqlfluff\[dbt\]"):
        dbt_templater.process(
            in_str="",
            fname="models/my_new_project/test.sql",
            config=FluffConfig(configs=DBT_FluffConfig(configs=DBT_FLUFF_CONFIG)),
        )


@pytest.mark.dbt
def test__templater_dbt_profiles_dir_expanded(dbt_templater):
    """Check that the profiles_dir is expanded."""
    profiles_dir = dbt_templater._get_profiles_dir(
        FluffConfig(configs={"templater": {"dbt": {"profiles_dir": "~/.dbt"}}})
    )
    assert profiles_dir == os.path.expanduser("~/.dbt")


@pytest.mark.parametrize(
    "in_fpath,out_fpath",
    [
        # dbt_utils
        ("models/my_new_project/use_dbt_utils.sql", "../dbt/use_dbt_utils.sql"),
        # macro calling another macro
        ("models/my_new_project/macro_in_macro.sql", "../dbt/macro_in_macro.sql"),
        # config.get(...)
        ("models/my_new_project/use_headers.sql", "../dbt/use_headers.sql"),
        # var(...)
        ("models/my_new_project/use_var.sql", "../dbt/use_var.sql"),
    ]
)
@pytest.mark.dbt
def test__templater_dbt_templating_result(in_dbt_project_dir, dbt_templater, in_fpath, out_fpath):
    """Test that input sql file gets templated into output sql file."""
    outstr, _ = dbt_templater.process(
        in_str="",
        fname=in_fpath,
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    assert outstr == open(out_fpath).read()
