"""
Tests for templaters.
"""

import pytest

from sqlfluff.templaters import (RawTemplateInterface, templater_selector,
                                 PythonTemplateInterface, JinjaTemplateInterface)


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
