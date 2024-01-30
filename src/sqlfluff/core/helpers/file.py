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
    except ValueError:
        # Getting a value error means that we're likely on a windows system
        # and have been provided a `inner_path` and `outer_path` which are
        # in different drives. In this situation, there's no shared path,
        # so just yield the given path.
        common_path = None

    # NOTE: I think the following logic here isn't correct. It is too expansive
    # in the search locations for config files. Correcting that without access
    # to the root project location for a dbt project and therefore allowing a
    # a more accurate search is not feasible. In future that path should somehow
    # be made available here.

    if not common_path:
        yield outer_path.resolve()
    else:
        # we have a sub path! We can load nested paths
        path_to_visit = common_path
        while path_to_visit != inner_path:
            yield path_to_visit.resolve()
            next_path_to_visit = (
                path_to_visit / inner_path.relative_to(path_to_visit).parts[0]
            )
            if next_path_to_visit == path_to_visit:  # pragma: no cover
                # we're not making progress...
                # [prevent infinite loop]
                break
            path_to_visit = next_path_to_visit

    yield inner_path.resolve()
