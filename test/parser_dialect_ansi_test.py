""" The Test file for the ANSI dialect of SQLFluff """

import pytest

from sqlfluff.parser.dialects import ansi


def test__parser__dialect_ansi_simple():
    ansi.parse('SelECt sdfsaasd    FrOM   asdfawwwww   GroUP BY  asdfawwwww.fasfekjhsf   order BY  something_else    ')
