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


def test__templater_config_scalar():
    lntr = Linter(config=FluffConfig())
    p = list(lntr.parse_path('test/fixtures/templater/jinja_a/jinja.sql'))
    parsed = p[0][0]
    if parsed is None:
        print(p)
        raise RuntimeError(p[0][1])
    tpl = parsed.to_tuple(code_only=True, show_raw=True)
    assert tpl == ('file', (('statement', (('select_statement', (
        ('keyword', 'SELECT'), ('select_target_group', (('select_target_element', (('numeric_literal', '56'),)),)),
        ('from_clause', (('keyword', 'FROM'), ('table_expression', (('object_reference', (
            ('naked_identifier', 'sch1'), ('dot', '.'), ('naked_identifier', 'tbl2')
        )),))))
    )),)),))


def test__templater_config_macro(yaml_loader):
    lntr = Linter(config=FluffConfig())
    p = list(lntr.parse_path('test/fixtures/templater/jinja_b/jinja.sql'))
    parsed = p[0][0]
    if parsed is None:
        print(p)
        raise RuntimeError(p[0][1])
    # Whitespace is important here to test how that's treated
    tpl = parsed.to_tuple(code_only=False, show_raw=True)
    expected = yaml_loader('test/fixtures/templater/jinja_b/jinja.yml')
    assert tpl == expected
