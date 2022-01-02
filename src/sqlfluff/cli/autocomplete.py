"""autocompletion commands."""

from click.shell_completion import CompletionItem

from sqlfluff import list_dialects


def dialect_shell_complete(ctx, param, incomplete):
    """Shell completion for possible dialect names.

    We use this over click.Choice as we want to internally
    handle error messages and codes for incorrect/outdated dialects.
    """
    dialect_names = [e.name for e in list_dialects()]
    return [
        CompletionItem(name) for name in dialect_names if name.startswith(incomplete)
    ]
