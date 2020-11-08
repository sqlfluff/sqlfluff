"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplater,
    templater_selector,
    PythonTemplater,
    JinjaTemplater,
    TemplatedFile,
)


def test__templater_selection():
    """Test template selection by name."""
    assert templater_selector().__class__ is JinjaTemplater
    assert templater_selector("raw").__class__ is RawTemplater
    assert templater_selector("python").__class__ is PythonTemplater
    assert templater_selector("jinja").__class__ is JinjaTemplater
    with pytest.raises(ValueError):
        templater_selector("afefhlsakufe")


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplater()
    instr = "SELECT * FROM {{blah}}"
    outstr, _ = t.process(instr)
    assert instr == str(outstr)


@pytest.mark.parametrize(
    "in_slice,out_slice,is_literal,file_slices",
    [
        # Simple example
        (slice(5,10), slice(5,10), True, [("literal", slice(0, 20, None), slice(0, 20, None))]),
        # Unrealistic, but should still work
        (slice(5,10), slice(55,60), True, [("literal", slice(50, 70, None), slice(0, 20, None))]),
        # Spanning a template
        (
            slice(5, 15),
            slice(5, 20),
            False,
            [
                ("literal", slice(0, 10, None), slice(0, 10, None)),
                ("templated", slice(10, 17, None), slice(10, 12, None)),
                ("literal", slice(17, 25, None), slice(12, 20, None)),
            ],
        ),
        # Handling templated
        (
            slice(5, 15),
            slice(0, 25),
            False,
            [
                ("templated", slice(0, 10, None), slice(0, 10, None)),
                ("templated", slice(10, 17, None), slice(10, 12, None)),
                ("templated", slice(17, 25, None), slice(12, 20, None)),
            ],
        ),
    ],
)
def test__templated_file_template_slice_to_source_slice(in_slice,out_slice,is_literal,file_slices):
    """Test TemplatedFile.template_slice_to_source_slice."""
    file = TemplatedFile(source_str="Dummy String", sliced_file=file_slices)
    source_slice, literal_test = file.template_slice_to_source_slice(in_slice)
    assert is_literal == literal_test
    assert source_slice == out_slice
