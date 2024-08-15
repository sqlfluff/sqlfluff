"""Discovery methods for sql files.

The main public method here is `paths_from_path` which takes
potentially ambiguous paths and file input and resolves them
into specific file references. The method also processes the
`.sqlfluffignore` functionality in the process.
"""

import logging
import os
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

import pathspec

from sqlfluff.core.errors import (
    SQLFluffUserError,
)
from sqlfluff.core.helpers.file import iter_intermediate_paths

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]
IgnoreSpecRecords = List[Tuple[str, str, pathspec.PathSpec]]


def _iter_config_files(
    target_path: Path,
    working_path: Path,
    config_filenames: Tuple[str],
) -> Iterator[str]:
    """Iterate through paths looking for valid config files."""
    for search_path in iter_intermediate_paths(target_path.absolute(), working_path):
        for _filename in config_filenames:
            filepath = os.path.join(search_path, _filename)
            if os.path.isfile(filepath):
                # Yield if a config file with this name exists at this path.
                yield filepath


def _check_ignore_specs(absolute_filepath: str, ignore_specs: IgnoreSpecRecords) -> bool:
    for dirname, _, spec in ignore_specs:
        if spec.match_file(os.path.relpath(absolute_filepath, dirname)):
            return True
    return False


def paths_from_path(
    path: str,
    ignore_non_existent_files: bool = False,
    ignore_files: bool = True,
    working_path: str = os.getcwd(),
    target_file_exts: Sequence[str] = (".sql",),
) -> List[str]:
    """Return a set of sql file paths from a potentially more ambiguous path string.

    Here we also deal with the .sqlfluffignore file if present.

    Only files within the path provided are returned, *however* the search area
    for ignore files is wider. They can both be within the provided path, and also
    between the working path and the given path.

    NOTE: In the situation that the given path is *not* a subdirectory of the
    working path, the current behaviour is to search for the *lowest common path*
    of the two. This might be counterintuitive, but supports an appropriate solution
    for the dbt templater without having to additionally pass the project root path.
    """
    if not os.path.exists(path):
        if ignore_non_existent_files:
            return []
        else:
            raise SQLFluffUserError(
                f"Specified path does not exist. Check it/they exist(s): {path}."
            )
        
    lower_file_exts = tuple(ext.lower() for ext in target_file_exts)
        
    # First load any ignore files from outside the path.
    # These will be applied to every file within the path, because we know that
    # they're in a parent folder.
    # NOTE: ARE THEY? What about no common path!?
    # (ignore_path, ignore_filename, ignore_spec)
    outer_ignore_specs: IgnoreSpecRecords = []
    # Only load them if we're using ignorefiles. NOTE: That if ignore_files
    # is False, we keep the routines for _checking_ we just never load the
    # files in the first place.
    if ignore_files:
        for outer_ignore_file in _iter_config_files(Path(path).absolute(), Path(working_path) if isinstance(working_path, str) else working_path, (".sqlfluffignore",)):
            outer_dirname = os.path.dirname(outer_ignore_file)
            with open(outer_ignore_file) as f:
                outer_ignore_specs.append((outer_dirname, os.path.basename(outer_ignore_file), pathspec.PathSpec.from_lines("gitwildmatch", f)))

    # Handle being passed an exact file first.
    if os.path.isfile(path):
        # Does it have a relevant extension? If not, just return an empty list.
        _, file_ext = os.path.splitext(path)
        if file_ext.lower() not in lower_file_exts:
            return []
    
        # It's an exact file. We only need to handle the outer ignore files,
        # and that's only to warn if they're being applied.
        abs_fpath = os.path.abspath(path)
        for outer_dirname, outer_file, outer_spec in outer_ignore_specs:
            if outer_spec.match_file(os.path.relpath(abs_fpath, outer_dirname)):
                ignore_file = os.path.join(outer_dirname, outer_file)
                linter_logger.warning(
                    f"Exact file path {path} was given but it was configured as"
                    f"ignored by an ignore pattern in {ignore_file}, "
                    "re-run with `--disregard-sqlfluffignores` to "
                    f"skip {ignore_file}"
                )
                # Return no match, because the file is ignored.
                return []

        return [os.path.normpath(path)]

    # Otherwise, it's not an exact path and we're going to walk the path
    # progressively, processing ignore files as we go.
    ignore_filename_set = frozenset((".sqlfluffignore",))
    # (ignore_path, ignore_filename, ignore_spec)
    inner_ignore_specs: IgnoreSpecRecords = []
    # Set up the filename buffer
    sql_file_buffer: List[str] = []
    for dirname, subdirs, filenames in os.walk(path, topdown=True):
        # First look for any ignore files in the path (if ignoring files)
        if ignore_files:
            for ignore_file in set(filenames) & ignore_filename_set:
                with open(os.path.join(dirname, ignore_file)) as f:
                    # Add them to the buffer
                    inner_ignore_specs.append((dirname, ignore_file, pathspec.PathSpec.from_lines("gitwildmatch", f)))

        # Then prune any subdirectories which are ignored (by modifying `subdirs`)
        # https://docs.python.org/3/library/os.html#os.walk
        for subdir in subdirs[:]:  # slice it so that we can modify it in the process.
            abs_fpath = os.path.abspath(os.path.join(dirname, subdir))
            # Outer specs
            if _check_ignore_specs(abs_fpath, outer_ignore_specs):
                subdirs.remove(subdir)
                continue

            # Inner specs
            if _check_ignore_specs(abs_fpath, inner_ignore_specs):
                subdirs.remove(subdir)
                continue

            for inner_dirname, inner_file, inner_spec in inner_ignore_specs[:]:
                # Additionally, prune any inner specs that are no longer relevant,
                # as indicated by us no longer being in a subdirectory of them.
                if not (
                    dirname == inner_dirname
                    or dirname.startswith(os.path.abspath(inner_dirname) + os.sep)
                ):
                    inner_ignore_specs.remove((inner_dirname, inner_file, inner_spec))

        # Then look for any relevant sql files in the path.
        for filename in filenames:
            relative_path = os.path.join(dirname, filename)
            absolute_path = os.path.abspath(relative_path)
            # Check file extension
            _, file_ext = os.path.splitext(filename)
            if file_ext.lower() not in lower_file_exts:
                continue
            
            # Check outer ignore specs
            if _check_ignore_specs(absolute_path, outer_ignore_specs):
                continue
                
            # Check inner ignore specs
            if _check_ignore_specs(absolute_path, inner_ignore_specs):
                continue
            
            # If we get here, it's one we want, add it to a buffer for sorting.
            sql_file_buffer.append(os.path.normpath(relative_path))

    return sorted(sql_file_buffer)
