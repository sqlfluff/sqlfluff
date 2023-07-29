"""File Helpers for the parser module."""

import chardet

from sqlfluff.core.config import FluffConfig


def get_encoding(fname: str, config: FluffConfig) -> str:
    """Get the encoding of the file (autodetect)."""
    encoding_config: str = config.get("encoding", default="autodetect")

    if encoding_config == "autodetect":
        with open(fname, "rb") as f:
            data = f.read()
        return chardet.detect(data)["encoding"]

    return encoding_config
