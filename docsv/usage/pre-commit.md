# Using `pre-commit`

[pre-commit](https://pre-commit.com/) is a framework to manage git "hooks"
triggered right before a commit is made.

A [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) is a git feature to "fire off custom scripts"
when specific actions occur.

Using [pre-commit](https://pre-commit.com/) with SQLFluff is a good way
to provide automated linting to SQL developers.

With [pre-commit](https://pre-commit.com/), you also get the benefit of
only linting/fixing the files that changed.

SQLFluff comes with two [pre-commit](https://pre-commit.com/) hooks:

* `sqlfluff-lint`: returns linting errors.
* `sqlfluff-fix`: attempts to fix rule violations.

::: danger WARNING
For safety reasons, `sqlfluff-fix` by default will not make any fixes in
files that had templating or parse errors, even if those errors were ignored
using `noqa` or `--ignore`.

Although it is not advised, you *can* tell SQLFluff to try and fix
these files by overriding the `fix_even_unparsable` setting
in `.sqlfluff` config file or using the `sqlfluff fix --FIX-EVEN-UNPARSABLE`
command line option.

*Overriding this behavior may break your SQL. If you use this override,
always be sure to review any fixes applied to files with templating or parse
errors to verify they are okay.*
:::

You should create a file named `.pre-commit-config.yaml`
at the root of your git project, which should look
like this:

```yaml
repos:
- repo: https://github.com/sqlfluff/sqlfluff
  rev: |release|
  hooks:
    - id: sqlfluff-lint
      # For dbt projects, this installs the dbt "extras".
      # You will need to select the relevant dbt adapter for your dialect
      # (https://docs.getdbt.com/docs/available-adapters):
      # additional_dependencies: ['<dbt-adapter>', 'sqlfluff-templater-dbt']
    - id: sqlfluff-fix
      # Arbitrary arguments to show an example
      # args: [--rules, "LT02,CP02"]
      # additional_dependencies: ['<dbt-adapter>', 'sqlfluff-templater-dbt']
```

When trying to use the [dbt templater](../configuration/templating/dbt), uncomment the
`additional_dependencies` to install the extras.
This is equivalent to running `pip install <dbt-adapter> sqlfluff-templater-dbt`.

You can specify the version of `dbt-adapter` used in [pre-commit](https://pre-commit.com/),
for example:

```yaml
additional_dependencies : ['dbt-bigquery==1.0.0', 'sqlfluff-templater-dbt']
```

See the list of available [dbt-adapters](https://docs.getdbt.com/docs/available-adapters).

Note that you can pass the same arguments available
through the CLI using `args:`.

## Ignoring files while using `pre-commit`

Under the hood, [pre-commit](https://pre-commit.com/) works by passing specific files to *SQLFluff*.
For example, if the only two files that are modified in your commit are
`file_a.sql` and `file_b.sql`, then the command which is called
in the background is `sqlfluff lint file_a.sql file_b.sql`. While this
is efficient, it does produce some unwanted noise when also
using [.sqlfluffignore](../configuration/ignoring#sqlfluffignore). This is because *SQLFluff* is designed to allow
users to override an *ignore* configuration by passing the name of the file
directly. This makes a lot of sense in a CLI context, but less so in the context
of being invoked by [pre-commit](https://pre-commit.com/).

To avoid noisy logs when using both [pre-commit](https://pre-commit.com/) and [.sqlfluffignore](../configuration/ignoring#sqlfluffignore),
we recommend also setting the `exclude` argument in your
`.pre-commit-config.yaml` file (either the [top level config](https://pre-commit.com/#top_level-exclude) or the
[hook specific config](https://pre-commit.com/#config-exclude)). This will prevent files matching the given pattern
being passed to *SQLFluff* and so silence any warnings about the
[.sqlfluffignore](../configuration/ignoring#sqlfluffignore) being overridden.
