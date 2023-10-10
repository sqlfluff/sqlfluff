"""autocompletion commands."""

from typing import List

from sqlfluff import list_dialects

# Older versions of click don't have shell completion
# so handle for now, as version 8 still fairly recent
# See: https://github.com/sqlfluff/sqlfluff/issues/2543
shell_completion_enabled = True
try:
    from click.shell_completion import CompletionItem
except ImportError:  # pragma: no cover
    # In older versions don't enable completion.
    # We don't force newer versions of click however.
    # See: https://github.com/sqlfluff/sqlfluff/issues/2543
    shell_completion_enabled = False


# NOTE: Important that we refer to the "CompletionItem" type
# as a string rather than a direct reference so that we don't
# get import errors when running with older versions of click.
def dialect_shell_complete(ctx, param, incomplete) -> List["CompletionItem"]:
    """Shell completion for possible dialect names.

    We use this over click.Choice as we want to internally
    handle error messages and codes for incorrect/outdated dialects.
    """
    dialect_names = [e.label for e in list_dialects()]
    return [
        CompletionItem(name) for name in dialect_names if name.startswith(incomplete)
    ]
