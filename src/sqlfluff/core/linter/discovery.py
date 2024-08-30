"""Discovery methods for sql files.

The main public method here is `paths_from_path` which takes
potentially ambiguous paths and file input and resolves them
into specific file references. The method also processes the
`.sqlfluffignore` functionality in the process.
"""

import sys
import logging
import os
from pathlib import Path
from typing import (
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Callable,
    Dict,
)

import pathspec

from sqlfluff.core.errors import (
    SQLFluffUserError,
)
from sqlfluff.core.helpers.file import iter_intermediate_paths

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]
IgnoreSpecRecord = Tuple[str, str, pathspec.PathSpec]
IgnoreSpecRecords = List[IgnoreSpecRecord]


def _check_ignore_specs(
    absolute_filepath: str, ignore_specs: IgnoreSpecRecords
) -> Optional[str]:
    """Check a filepath against the loaded ignore files.

    Returns:
        The path of an ignorefile if found, None otherwise.
    """
    for dirname, filename, spec in ignore_specs:
        if spec.match_file(os.path.relpath(absolute_filepath, dirname)):
            return os.path.join(dirname, filename)
    return None


def _load_specs_from_lines(lines: Iterable[str]) -> pathspec.PathSpec:
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def _load_ignorefile(dirpath: str, filename: str) -> IgnoreSpecRecord:
    """Load a sqlfluffignore file, returning the parsed spec."""
    filepath = os.path.join(dirpath, filename)
    with open(filepath, mode="r") as f:
        try:
            spec = _load_specs_from_lines(f)
        except Exception:
            raise SQLFluffUserError(f"Error parsing ignore patterns in {filepath}.")
    return dirpath, filename, spec


def _load_pyproject(dirpath: str, filename: str) -> Optional[IgnoreSpecRecord]:
    filepath = os.path.join(dirpath, filename)
    with open(filepath, mode="r") as file:
        config = tomllib.loads(file.read())
    # Get the `[tool.sqlfluff.ignore]` section from the toml.
    ignore_section = config.get("tool", {}).get("sqlfluff", {}).get("ignore", {})
    patterns = ignore_section.get("patterns", [])
    if not patterns:
        return None
    try:
        spec = _load_specs_from_lines(patterns)
    except Exception:
        raise SQLFluffUserError(
            f"Error parsing ignore patterns in {filepath}: {patterns}."
        )
    return dirpath, filename, spec


ignore_file_loaders: Dict[str, Callable[[str, str], Optional[IgnoreSpecRecord]]] = {
    ".sqlfluffignore": _load_ignorefile,
    "pyproject.toml": _load_pyproject,
}


def _iter_config_files(
    target_path: Path,
    working_path: Path,
) -> Iterator[Tuple[str, str]]:
    """Iterate through paths looking for valid config files."""
    for search_path in iter_intermediate_paths(target_path.absolute(), working_path):
        for _filename in ignore_file_loaders:
            filepath = os.path.join(search_path, _filename)
            if os.path.isfile(filepath):
                # Yield if a config file with this name exists at this path.
                yield str(search_path), _filename


def _match_file_extension(filepath: str, valid_extensions: Sequence[str]) -> bool:
    """Match file path against extensions.

    Assumes that valid_extensions is already all lowercase.

    Returns:
        True if the file has an extension in `valid_extensions`.
    """
    _, file_ext = os.path.splitext(filepath)
    return file_ext.lower() in valid_extensions


def _process_exact_path(
    path: str,
    working_path: str,
    lower_file_exts: Tuple[str, ...],
    outer_ignore_specs: IgnoreSpecRecords,
) -> List[str]:
    """Handle exact paths being passed to paths_from_path.

    If it's got the right extension and it's not ignored, then
    we just return the normalised version of the path. If it's
    not the right extension, return nothing, and if it's ignored
    then return nothing, but include a warning for the user.
    """
    # Does it have a relevant extension? If not, just return an empty list.
    if not _match_file_extension(path, lower_file_exts):
        return []

    # It's an exact file. We only need to handle the outer ignore files.
    # There won't be any "inner" ignores because an exact file doesn't create
    # any sub paths.
    abs_fpath = os.path.abspath(path)
    ignore_file = _check_ignore_specs(abs_fpath, outer_ignore_specs)

    if not ignore_file:
        # If not ignored, just return the file.
        return [os.path.normpath(path)]

    ignore_rel_path = os.path.relpath(ignore_file, working_path)
    linter_logger.warning(
        f"Exact file path {path} was given but it was "
        f"ignored by an ignore pattern set in {ignore_rel_path}, "
        "re-run with `--disregard-sqlfluffignores` to not process "
        "ignore files."
    )
    # Return no match, because the file is ignored.
    return []


def _iter_files_in_path(
    path: str,
    ignore_files: bool,
    outer_ignore_specs: IgnoreSpecRecords,
    lower_file_exts: Tuple[str, ...],
) -> Iterator[str]:
    """Handle directory paths being passed to paths_from_path.

    We're going to walk the path progressively, processing ignore
    files as we go. Those ignore files that we find (inner ignore
    files) only apply within the folder they are found, whereas the
    ignore files from outside the path (the outer ignore files) will
    always apply, so we handle them separately.
    """
    inner_ignore_specs: IgnoreSpecRecords = []
    ignore_filename_set = frozenset(ignore_file_loaders.keys())

    for dirname, subdirs, filenames in os.walk(path, topdown=True):
        # Before adding new ignore specs, remove any which are no longer relevant
        # as indicated by us no longer being in a subdirectory of them.
        # NOTE: Slice so we can modify as we go.
        for inner_dirname, inner_file, inner_spec in inner_ignore_specs[:]:
            if not (
                dirname == inner_dirname
                or dirname.startswith(os.path.abspath(inner_dirname) + os.sep)
            ):
                inner_ignore_specs.remove((inner_dirname, inner_file, inner_spec))

        # Then look for any ignore files in the path (if ignoring files), add them
        # to the inner buffer if found.
        if ignore_files:
            for ignore_file in set(filenames) & ignore_filename_set:
                ignore_spec = ignore_file_loaders[ignore_file](dirname, ignore_file)
                if ignore_spec:
                    inner_ignore_specs.append(ignore_spec)

        # Then prune any subdirectories which are ignored (by modifying `subdirs`)
        # https://docs.python.org/3/library/os.html#os.walk
        for subdir in subdirs[:]:  # slice it so that we can modify it in the process.
            # NOTE: The "*" in this next section is a bit of a hack, but pathspec
            # doesn't like matching _directories_ directly, but if we instead match
            # `directory/*` we get the same effect.
            absolute_path = os.path.abspath(os.path.join(dirname, subdir, "*"))
            if _check_ignore_specs(
                absolute_path, outer_ignore_specs
            ) or _check_ignore_specs(absolute_path, inner_ignore_specs):
                subdirs.remove(subdir)
                continue

        # Then look for any relevant sql files in the path.
        for filename in filenames:
            relative_path = os.path.join(dirname, filename)
            absolute_path = os.path.abspath(relative_path)

            # Check file extension is relevant
            if not _match_file_extension(filename, lower_file_exts):
                continue
            # Check not ignored by outer & inner ignore specs
            if _check_ignore_specs(absolute_path, outer_ignore_specs):
                continue
            if _check_ignore_specs(absolute_path, inner_ignore_specs):
                continue

            # If we get here, it's one we want. Yield it.
            yield os.path.normpath(relative_path)


def paths_from_path(
    path: str,
    ignore_non_existent_files: bool = False,
    ignore_files: bool = True,
    working_path: str = os.getcwd(),
    target_file_exts: Sequence[str] = (".sql",),
) -> List[str]:
    """Return a set of sql file paths from a potentially more ambiguous path string.

    Here we also deal with the any ignore files file if present (such as .sqlfluffignore).

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
    outer_ignore_specs: IgnoreSpecRecords = []
    # Only load them if we're using ignore files. NOTE: That if `ignore_files`
    # is False, we keep the routines for _checking_ we just never load the
    # files in the first place.
    if ignore_files:
        for ignore_path, ignore_file in _iter_config_files(
            Path(path).absolute(),
            Path(working_path) if isinstance(working_path, str) else working_path,
        ):
            ignore_spec = ignore_file_loaders[ignore_file](ignore_path, ignore_file)
            if ignore_spec:
                outer_ignore_specs.append(ignore_spec)

    # Handle being passed an exact file first.
    if os.path.isfile(path):
        return _process_exact_path(
            path, working_path, lower_file_exts, outer_ignore_specs
        )

    # Otherwise, it's not an exact path and we're going to walk the path
    # progressively, processing ignore files as we go.
    return sorted(
        _iter_files_in_path(path, ignore_files, outer_ignore_specs, lower_file_exts)
    )
