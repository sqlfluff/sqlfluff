"""The core elements of sqlfluff."""

# flake8: noqa: F401

# Config objects
from sqlfluff.core.config import FluffConfig

# Public classes
from sqlfluff.core.linter import Linter
from sqlfluff.core.parser import Lexer, Parser

# All of the errors.
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLTemplaterError,
    SQLLexError,
    SQLParseError,
    SQLLintError,
)

# Dialect introspection.
# TODO: This feels untidy, maybe refactor into a class.
from sqlfluff.core.dialects import dialect_selector, dialect_readout
