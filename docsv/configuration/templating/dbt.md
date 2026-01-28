# `dbt` templater

::: tip NOTE
From sqlfluff version 0.7.0 onwards, the dbt templater has been moved
to a separate plugin and python package. Projects that were already using
the dbt templater may initially fail after an upgrade to 0.7.0+. See the
installation instructions below to install the dbt templater.

dbt templating is still a relatively new feature added in 0.4.0 and
is still in very active development! If you encounter an issue, please
let us know in a GitHub issue or on the SQLFluff slack workspace.
:::

`dbt` is not the default templater for *SQLFluff* (it is `jinja`).
`dbt` is a complex tool, so using the default `jinja` templater
will be simpler. You should be aware when using the `dbt` templater that
you will be exposed to some of the complexity of `dbt`. Users may wish to
try both templaters and choose according to how they intend to use *SQLFluff*.

A simple rule of thumb might be:

- If you are using *SQLFluff* in a CI/CD context, where speed is not
  critical but accuracy in rendering sql is, then the `dbt` templater
  may be more appropriate.
- If you are using *SQLFluff* in an IDE or on a git hook, where speed
  of response may be more important, then the `jinja` templater may
  be more appropriate.

Pros:

* Most (potentially all) macros will work

Cons:

* More complex, e.g. using it successfully may require deeper
  understanding of your models and/or macros (including third-party macros)

  * More configuration decisions to make
  * Best practices are not yet established or documented

* If your `dbt` model files access a database at compile time, using
  SQLFluff with the `dbt` templater will **also** require access to a
  database.

  * Note that you can often point SQLFluff and the `dbt` templater at a
    test database (i.e. it doesn't have to be the production database).

* Runs slower

## Installation & Configuration

In order to get started using *SQLFluff* with a dbt project you will
first need to install the relevant [dbt adapter](https://docs.getdbt.com/docs/available-adapters) for your dialect
and the `sqlfluff-templater-dbt` package using
your package manager of choice (e.g.
`pip install dbt-postgres sqlfluff-templater-dbt`) and then will need the
following configuration:


In *.sqlfluff*:

```ini
[sqlfluff]
templater = dbt
```

In *.sqlfluffignore*:

```ini
target/
# dbt <1.0.0
dbt_modules/
# dbt >=1.0.0
dbt_packages/
macros/
```

You can set the dbt project directory, profiles directory and profile with:

```ini
[sqlfluff:templater:dbt]
project_dir = <relative or absolute path to dbt_project directory, can be overridden by env var DBT_PROJECT_DIR>
profiles_dir = <relative or absolute path to the directory that contains the profiles.yml file, can be overridden by env var DBT_PROFILES_DIR>
profile = <dbt profile>
target = <dbt target>
dbt_skip_compilation_error = <True or False, default is True>
```

::: tip NOTE

If the `profiles_dir` setting is omitted, SQLFluff will look for the profile
in the default location, which varies by operating system. On Unix-like
operating systems (e.g. Linux or macOS), the default profile directory is
`~/.dbt/`. On Windows, you can determine your default profile directory by
running `dbt debug --config-dir`.
:::

::: warning WARNING
A fatal error can be raised at compile time. That can sometimes happen for SQLFluff related reasons (it used
to happen if we tried to compile ephemeral models in the wrong order), but more often because a macro tries to query
a table at compile time which doesn't exist.
By default, `dbt_skip_compilation_error` parameter is set to `True`, that's why such errors will be ignored.
However if you want to see them, you can set it to `False` and SQLFluff will raise a fatal error.
:::

To use builtin dbt Jinja functions SQLFluff provides a configuration option
that enables usage within templates.

```ini
[sqlfluff:templater:jinja]
apply_dbt_builtins = True
```

This will provide dbt macros like `ref`, `var`, `is_incremental()`. If the need
arises builtin dbt macros can be customised via Jinja macros in `.sqlfluff`
configuration file.

```ini
[sqlfluff:templater:jinja:macros]
# Macros provided as builtins for dbt projects
dbt_ref = {% macro ref(model_ref) %}{{model_ref}}{% endmacro %}
dbt_source = {% macro source(source_name, table) %}{{source_name}}_{{table}}{% endmacro %}
dbt_config = {% macro config() %}{% for k in kwargs %}{% endfor %}{% endmacro %}
dbt_var = {% macro var(variable, default='') %}item{% endmacro %}
dbt_is_incremental = {% macro is_incremental() %}True{% endmacro %}
```

If your project requires that you pass variables to dbt through command line,
you can specify them in `template:dbt:context` section of `.sqlfluff`.
See below configuration and its equivalent dbt command:

```ini
[sqlfluff:templater:dbt:context]
my_variable = 1
```

```bash
dbt run --vars '{"my_variable": 1}'
```

## Known Caveats

- To use the dbt templater, you must set `templater = dbt` in the `.sqlfluff`
  config file in the directory where sqlfluff is run. The templater cannot
  be changed in `.sqlfluff` files in subdirectories.
- In SQLFluff 0.4.0 using the dbt templater requires that all files
  within the root and child directories of the dbt project must be part
  of the project. If there are deployment scripts which refer to SQL files
  not part of the project for instance, this will result in an error.
  You can overcome this by adding any non-dbt project SQL files to
  .sqlfluffignore.
