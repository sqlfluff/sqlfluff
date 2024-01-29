"""Export cli to __main__ for use like python -m sqlfluff."""

from sqlfluff.cli.commands import cli

if __name__ == "__main__":
    cli()
