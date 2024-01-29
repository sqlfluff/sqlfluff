"""File Helpers for the parser module."""

import os.path
from pathlib import Path
from typing import Iterator, Optional

import chardet


def get_encoding(fname: str, config_encoding: str = "autodetect") -> str:
    """Get the encoding of the file (autodetect)."""
    if config_encoding != "autodetect":
        return config_encoding

    with open(fname, "rb") as f:
        data = f.read()
    return chardet.detect(data)["encoding"]


def iter_intermediate_paths(inner_path: Path, outer_path: Path) -> Iterator[Path]:
    """Iterate paths between two given paths.

    If the `inner_path` is a subdirectory of the `outer_path` then all steps
    in between the two are yielded as Path objects, from outer to inner including
    the two at each end. If not, then the just the `outer_path` and `inner_path`
    are returned (in that order).
    """
    inner_path = inner_path.absolute()
    outer_path = outer_path.absolute()

    # If we've been passed a file and not a directory,
    # then go straight to the directory.
    # NOTE: We only check this for the inner path.
    if not inner_path.is_dir():
        inner_path = inner_path.parent

    common_path: Optional[Path]
    try:
        common_path = Path(os.path.commonpath([inner_path, outer_path])).absolute()
        # Check how many parts the common path has
        if not common_path.parts:
            common_path = None
    except ValueError:
        # Getting a value error means that we're likely on a windows system
        # and have been provided a `inner_path` and `outer_path` which are
        # in different drives. In this situation, there's no shared path,
        # so just yield the given path.
        common_path = None

    # Always yield the outer_path
    yield outer_path.resolve()

    # If we're in a nested path scenario, then we work between the two
    # paths, yielding config locations at each. If the inner path is
    # NOT a subpath of the outer path, then we don't.

    # NOTE: In essence I think we should only consider it to
    # be a true sub-path if `common_path` IS `working_path`,
    # however to mimic past behaviour, we work up from a shared
    # root if one exists.
    # TODO: In future we should instead work upward not from the common
    # shared path, but instead work up from the dbt project root if present.
    # However given the current location of the config loading routines
    # there isn't a good way for that location to be passed through.
    # NOTE: If this is a reverse sub-path i.e. where the outer path is
    # deeper than the inner path, don't iterate.
    if common_path and common_path != inner_path:
        # we have a sub path! We can load nested paths.
        # NOTE: As we work up, we mutate `common_path`.
        for step in inner_path.relative_to(common_path).parts:
            common_path = common_path / step
            yield common_path.resolve()
    else:
        # If not iterating, just yield the inner path
        yield inner_path.resolve()
