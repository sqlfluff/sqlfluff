# Using SQLFluff as a CLI Application

The [SQLFluff CLI](/reference/cli/) is a Python application which depends on
your host Python environment — see the [installation guide](/guide/install) for
setup instructions.

## Exit Codes

The exit code returned by SQLFluff is designed to be useful in deployment
pipelines and CI/CD scripts.

| Exit code | Meaning |
|-----------|---------|
| `0` | Operation succeeded, no issues found. |
| `1` | Operation succeeded, issues found. For example, a linting violation was found, or one file could not be parsed. |
| `2` | Operation failed — an error occurred and could not be completed. For example, a configuration error or an internal SQLFluff error. |

This means a `git push` hook or CI step can simply check for a non-zero exit
code to know whether SQLFluff found anything, while still being able to
distinguish between "issues found" (`1`) and "SQLFluff itself broke" (`2`) when
needed.

For the full list of commands and options, see the [CLI Reference](/reference/cli/).
