# Security Considerations

A full list of [Security Advisories is available on GitHub](https://github.com/sqlfluff/sqlfluff/security/advisories).

Given the context of how SQLFluff is designed to be used, there are three
different tiers of access which users may have the ability to manipulate how the
tool functions in a secure environment.

## 1. Users with SQL edit access

While SQLFluff does not execute the SQL itself, during the
[templating step](/configuration/templating/) (in particular via Jinja or dbt),
certain macros may have the ability to execute arbitrary SQL code (e.g. the
[dbt run_query macro](https://docs.getdbt.com/reference/dbt-jinja-functions/run_query)).
For the Jinja templater, SQLFluff uses the
[Jinja2 SandboxedEnvironment](https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment)
to limit execution of unsafe code. See [tier 3](#3-users-with-invocation-access)
below for ways to further restrict the ability of users to import libraries.

Even without macro execution, malicious SQL can attempt to consume excessive
parser resources through extremely deep or unusually expansive query structures.
To reduce that risk, keep the `max_parse_depth` and `max_parse_nodes` limits
enabled. These settings bound parser recursion and total parse tree size
respectively, and can be adjusted upward for trusted projects with legitimately
complex queries. See the [Default Configuration](/configuration/defaults) for
their default values.

## 2. Users with config file access

In many environments, users who can edit SQL files may also be able to edit
the [configuration files](/configuration/). It's important to note that because
of [in-file configuration](/configuration/#in-file-configuration), users who
can edit the SQL files being linted will already have access to the vast
majority of configuration options anyway. This means that restricting access
to `.sqlfluff` config files provides minimal additional protection for users
who can already edit the linting target files.

## 3. Users with invocation access

SQLFluff can be invoked either as a CLI tool or via the Python API. The primary
risk vector is the macro environment: via the `library_path` configuration value
(see [Jinja library templating](/configuration/templating/jinja#library-templating)),
users could potentially bring arbitrary Python code into SQLFluff.

For secure environments, override `library_path` at the point of invocation so
that it cannot be overridden by config files on disk.

**Via the CLI:**

```bash
sqlfluff lint my_path --library-path none
```

**Via the Python API:**

```python
from sqlfluff.core import FluffConfig, Linter

config = FluffConfig(
    overrides={
        "dialect": "snowflake",
        # Pass the string "none" rather than Python None: a None value
        # would not override a library_path set in a config file on disk,
        # whereas a string override takes unconditional precedence.
        "library_path": "none",
    }
)

linted_file = Linter(config=config).lint_string(sql)
```

::: info
The CLI converts `--library-path none` into an explicit `None` internally, which stops library loading cleanly. The Python API override uses the string `"none"` instead — this prevents any config-file `library_path` from being picked up and, in practice, no libraries are loaded because no directory named `"none"` typically exists. If you want an unconditional guarantee, pass the path to an empty directory rather than relying on `"none"`.
:::
