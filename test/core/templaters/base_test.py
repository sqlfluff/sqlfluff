"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplateInterface,
    templater_selector,
    PythonTemplateInterface,
    JinjaTemplateInterface,
)


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
    assert instr == str(outstr)
