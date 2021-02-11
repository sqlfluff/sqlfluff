"""The core elements of sqlfluff."""

# flake8: noqa: F401

# Config objects
from src.sqlfluff.core.config import FluffConfig

# Public classes
from src.sqlfluff.core.linter import Linter
from src.sqlfluff.core.parser import Lexer, Parser

# All of the errors.
from src.sqlfluff.core.errors import (
    SQLBaseError,
    SQLTemplaterError,
    SQLLexError,
    SQLParseError,
    SQLLintError,
)

# Dialect introspection.
# TODO: This feels untidy, maybe refactor into a class.
from src.sqlfluff.core.dialects import dialect_selector, dialect_readout
