"""
Tests for templaters.
"""

import pytest

from sqlfluff.templaters import (RawTemplateInterface, templater_selector,
                                 PythonTemplateInterface, JinjaTemplateInterface)
from sqlfluff.linter import Linter
from sqlfluff.config import FluffConfig


def test__templater_selection():
    assert templater_selector().__class__ is JinjaTemplateInterface
    assert templater_selector('raw').__class__ is RawTemplateInterface
    assert templater_selector('python').__class__ is PythonTemplateInterface
    assert templater_selector('jinja').__class__ is JinjaTemplateInterface
    with pytest.raises(ValueError):
        templater_selector('afefhlsakufe')


def test__templater_raw():
    t = RawTemplateInterface()
    instr = 'SELECT * FROM {{blah}}'
    outstr = t.process(instr)
    assert instr == outstr


def test__templater_python():
    t = PythonTemplateInterface(override_context=dict(blah='foo'))
    instr = 'SELECT * FROM {blah}'
    outstr = t.process(instr)
    assert outstr == 'SELECT * FROM foo'


def test__templater_jinja():
    """ NB We're explicitly checking the final newline treatment too """
    t = JinjaTemplateInterface(override_context=dict(blah='foo'))
    instr = 'SELECT * FROM {% for c in blah %}{{c}}{% if not loop.last %}, {% endif %}{% endfor %}\n\n'
    outstr = t.process(instr)
    assert outstr == 'SELECT * FROM f, o, o\n\n'


def assert_structure(yaml_loader, path, code_only=True):
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
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_a/jinja')


def test__templater_config_macro(yaml_loader):
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_b/jinja', code_only=False)


def test__templater_config_dbt(yaml_loader):
    assert_structure(yaml_loader, 'test/fixtures/templater/jinja_c_dbt/dbt_builtins')
