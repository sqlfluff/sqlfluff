"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import PythonTemplateInterface
from sqlfluff.core import SQLTemplaterError


PYTHON_STRING = "SELECT * FROM {blah}"


def test__templater_python():
    """Test the python templater."""
    t = PythonTemplateInterface(override_context=dict(blah="foo"))
    instr = PYTHON_STRING
    outstr, _ = t.process(instr)
    assert str(outstr) == "SELECT * FROM foo"


def test__templater_python_error():
    """Test error handling in the python templater."""
    t = PythonTemplateInterface(override_context=dict(noblah="foo"))
    instr = PYTHON_STRING
    with pytest.raises(SQLTemplaterError):
        t.process(instr)
