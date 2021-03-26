"""File Helpers for the parser module."""

import chardet

from sqlfluff.core.config import FluffConfig


def get_encoding(fname: str, config: FluffConfig) -> str:
    """Get the encoding of the file (autodetect)."""
    encoding_config = config.get("encoding", default="autodetect")

    if encoding_config == "autodetect":
        return chardet.detect(open(fname, "rb").read())["encoding"]

    return encoding_config
