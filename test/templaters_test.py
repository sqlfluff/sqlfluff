"""Tests for templaters."""

import pytest

from sqlfluff.templaters import (RawTemplateInterface, templater_selector,
                                 PythonTemplateInterface, JinjaTemplateInterface)
from sqlfluff.linter import Linter
from sqlfluff.config import FluffConfig
from sqlfluff.errors import SQLTemplaterError


def test__templater_selection():
    """Test template selection by name."""
    assert templater_selector().__class__ is JinjaTemplateInterface
    assert templater_selector('raw').__class__ is RawTemplateInterface
    assert templater_selector('python').__class__ is PythonTemplateInterface
    assert templater_selector('jinja').__class__ is JinjaTemplateInterface
    with pytest.raises(ValueError):
        templater_selector('afefhlsakufe')


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplateInterface()
    instr = 'SELECT * FROM {{blah}}'
    outstr = t.process(instr)
    assert instr == outstr


PYTHON_STRING = 'SELECT * FROM {blah}'


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplateInterface(override_context=dict(blah='foo'))
    instr = PYTHON_STRING
    outstr = t.process(instr)
    assert outstr == 'SELECT * FROM foo'


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplateInterface(override_context=dict(noblah='foo'))
    instr = PYTHON_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(instr)


JINJA_STRING = 'SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %} WHERE {{condition}}\n\n'


def test__templater_jinja():
    """Test jinja templating and the treatment of whitespace."""
    t = JinjaTemplateInterface(override_context=dict(
        blah='foo',
        condition='a < 10'))
    instr = JINJA_STRING
    outstr = t.process(instr)
    assert outstr == 'SELECT * FROM f, o, o WHERE a < 10\n\n'


def test__templater_jinja_error():
    """Test error handling in the jinja templater."""
    t = JinjaTemplateInterface(override_context=dict(noblah='foo'))
    instr = JINJA_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(instr)


def assert_structure(yaml_loader, path, code_only=True):
    """Check that a parsed sql file matches the yaml file with the same name."""
    lntr = Linter(config=FluffConfig())
    p = list(lntr.parse_path(path + '.sql'))
    parsed = p[0][0]
    if parsed is None:
        print(p)
        raise RuntimeError(p[0][1])
    # Whitespace is important here to test how that's treated
    tpl = parsed.to_tuple(code_only=code_only, show_raw=True)
    expected = yaml_loader(path + '.yml')
    assert tpl == expected


def test__templater_config_scalar(yaml_loader):
    """Check basic jinja substitution works."""
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_a/jinja')


def test__templater_config_macro(yaml_loader):
    """Check that configurable macros work."""
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_b/jinja', code_only=False)


def test__templater_config_dbt(yaml_loader):
    """Check that the built in dbt macros work."""
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_c_dbt/dbt_builtins')


def test__templater_do(yaml_loader):
    """Check that the do directive works."""
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_e/jinja')
