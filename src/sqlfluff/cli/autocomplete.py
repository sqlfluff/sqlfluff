"""autocompletion commands."""

from sqlfluff import list_dialects

# Older versions of click don't have shell completion
# so handle for now, as version 8 still fairly recent
# See: https://github.com/sqlfluff/sqlfluff/issues/2543
shell_completion_enabled = True
try:
    from click import shell_completion as completion
except ImportError:  # pragma: no cover
    shell_completion_enabled = False


def dialect_shell_complete(ctx, param, incomplete):
    """Shell completion for possible dialect names.

    We use this over click.Choice as we want to internally
    handle error messages and codes for incorrect/outdated dialects.
    """
    dialect_names = [e.name for e in list_dialects()]
    return [
        completion.CompletionItem(name)
        for name in dialect_names
        if name.startswith(incomplete)
    ]
