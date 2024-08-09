"""Discovery methods for sql files.

The main public method here is `paths_from_path` which takes
potentially ambiguous paths and file input and resolves them
into specific file references. The method also processes the
`.sqlfluffignore` functionality in the process.
"""

import logging
import os
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple, Union

import pathspec

from sqlfluff.core.errors import (
    SQLFluffUserError,
)
from sqlfluff.core.helpers.file import iter_intermediate_paths

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]


def _find_ignore_config_files(
    path: str,
    working_path: Union[str, Path] = Path.cwd(),
    ignore_file_name: str = ".sqlfluffignore",
) -> Set[str]:
    """Finds sqlfluff ignore files from both the path and its parent paths."""
    _working_path: Path = (
        Path(working_path) if isinstance(working_path, str) else working_path
    )
    return set(
        filter(
            os.path.isfile,
            map(
                lambda x: os.path.join(x, ignore_file_name),
                iter_intermediate_paths(Path(path).absolute(), _working_path),
            ),
        )
    )

def paths_from_path(
    path: str,
    ignore_file_name: str = ".sqlfluffignore",
    ignore_non_existent_files: bool = False,
    ignore_files: bool = True,
    working_path: str = os.getcwd(),
    target_file_exts: Sequence[str] = (".sql",),
) -> List[str]:
    """Return a set of sql file paths from a potentially more ambiguous path string.

    Here we also deal with the .sqlfluffignore file if present.

    When a path to a file to be linted is explicitly passed
    we look for ignore files in all directories that are parents of the file,
    up to the current directory.

    If the current directory is not a parent of the file we only
    look for an ignore file in the direct parent of the file.
    """
    if not os.path.exists(path):
        if ignore_non_existent_files:
            return []
        else:
            raise SQLFluffUserError(
                f"Specified path does not exist. Check it/they exist(s): {path}."
            )

    # Files referred to exactly are also ignored if
    # matched, but we warn the users when that happens
    is_exact_file = os.path.isfile(path)

    path_walk: WalkableType
    if is_exact_file:
        # When the exact file to lint is passed, we
        # fill path_walk with an input that follows
        # the structure of `os.walk`:
        #   (root, directories, files)
        dirpath = os.path.dirname(path)
        files = [os.path.basename(path)]
        path_walk = [(dirpath, None, files)]
    else:
        path_walk = list(os.walk(path))

    ignore_file_paths = _find_ignore_config_files(
        path=path, working_path=working_path, ignore_file_name=ignore_file_name
    )
    # Add paths that could contain "ignore files"
    # to the path_walk list
    path_walk_ignore_file = [
        (
            os.path.dirname(ignore_file_path),
            None,
            # Only one possible file, since we only
            # have one "ignore file name"
            [os.path.basename(ignore_file_path)],
        )
        for ignore_file_path in ignore_file_paths
    ]
    path_walk += path_walk_ignore_file

    # If it's a directory then expand the path!
    buffer = []
    ignores = {}
    for dirpath, _, filenames in path_walk:
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            # Handle potential .sqlfluffignore files
            if ignore_files and fname == ignore_file_name:
                with open(fpath) as fh:
                    spec = pathspec.PathSpec.from_lines("gitwildmatch", fh)
                    ignores[dirpath] = spec
                # We don't need to process the ignore file any further
                continue

            # We won't purge files *here* because there's an edge case
            # that the ignore file is processed after the sql file.

            # Scan for remaining files
            for ext in target_file_exts:
                # is it a sql file?
                if fname.lower().endswith(ext):
                    buffer.append(fpath)

    if not ignore_files:
        return sorted(buffer)

    # Check the buffer for ignore items and normalise the rest.
    # It's a set, so we can do natural deduplication.
    filtered_buffer = set()

    for fpath in buffer:
        abs_fpath = os.path.abspath(fpath)
        for ignore_base, ignore_spec in ignores.items():
            abs_ignore_base = os.path.abspath(ignore_base)
            if abs_fpath.startswith(
                abs_ignore_base
                + (
                    ""
                    if os.path.dirname(abs_ignore_base) == abs_ignore_base
                    else os.sep
                )
            ) and ignore_spec.match_file(
                os.path.relpath(abs_fpath, abs_ignore_base)
            ):
                # This file is ignored, skip it.
                if is_exact_file:
                    linter_logger.warning(
                        "Exact file path %s was given but "
                        "it was ignored by a %s pattern in %s, "
                        "re-run with `--disregard-sqlfluffignores` to "
                        "skip %s"
                        % (
                            path,
                            ignore_file_name,
                            ignore_base,
                            ignore_file_name,
                        )
                    )
                break
        else:
            npath = os.path.normpath(fpath)
            # For debugging, log if we already have the file.
            if npath in filtered_buffer:
                linter_logger.debug(  # pragma: no cover
                    "Developer Warning: Path crawler attempted to "
                    "requeue the same file twice. %s is already in "
                    "filtered buffer.",
                    npath,
                )
            filtered_buffer.add(npath)

    # Return a sorted list
    return sorted(filtered_buffer)
