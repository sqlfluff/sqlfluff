"""The core elements of sqlfluff."""

# flake8: noqa: F401

# Config objects
from .config import FluffConfig

# Public classes
from .linter import Linter
from .parser import Lexer, Parser

# All of the errors.
from .errors import (
    SQLBaseError,
    SQLTemplaterError,
    SQLLexError,
    SQLParseError,
    SQLLintError,
)

# Dialect introspection.
# TODO: This feels untidy, maybe refactor into a class.
from .dialects import dialect_selector, dialect_readout
