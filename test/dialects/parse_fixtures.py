"""Shared utility functions to retrieve all the parse fixtures."""
import os


def get_parse_fixtures(fail_on_missing_yml=False):
    """Search for all parsing fixtures."""
    parse_success_examples = []
    parse_structure_examples = []
    # Generate the filenames for each dialect from the parser test directory
    for d in os.listdir(os.path.join("test", "fixtures", "parser")):
        # Ignore documentation
        if d.endswith(".md"):
            continue
        # assume that d is now the name of a dialect
        dirlist = os.listdir(os.path.join("test", "fixtures", "parser", d))
        for f in dirlist:
            has_yml = False
            if f.endswith(".sql"):
                root = f[:-4]
                # only look for sql files
                parse_success_examples.append((d, f))
                # Look for the code_only version of the structure
                y = root + ".yml"
                if y in dirlist:
                    parse_structure_examples.append((d, f, True, y))
                    has_yml = True
                # Look for the non-code included version of the structure
                y = root + "_nc.yml"
                if y in dirlist:
                    parse_structure_examples.append((d, f, False, y))
                    has_yml = True
                if not has_yml and fail_on_missing_yml:
                    raise (
                        Exception(
                            f"Missing .yml file for {os.path.join(d, f)}. Run the test/generate_parse_fixture_yml.py script!"
                        )
                    )
    return parse_success_examples, parse_structure_examples


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join("test", "fixtures", "parser", dialect, fname)


def load_file(dialect, fname):
    """Load a file."""
    with open(make_dialect_path(dialect, fname)) as f:
        raw = f.read()
    return raw
