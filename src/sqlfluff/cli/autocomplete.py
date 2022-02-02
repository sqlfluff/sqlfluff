"""autocompletion commands."""

from sqlfluff import list_dialects

# Older versions of click don't have shell completion
# so handle for now, as version 8 still fairly recent
shell_completion_enabled = True
try:
    completion = __import__("click.shell_completion", fromlist=["click"])
except ImportError:
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
