# Ignoring Errors & Files

## Ignoring individual lines

Similar to [flake8's ignore](https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html#in-line-ignoring-errors), individual lines can be ignored by adding
`-- noqa` to the end of the line. Additionally, specific rules can
be ignored by quoting their code or the category.

```sql

-- Ignore all errors
SeLeCt  1 from tBl ;    -- noqa

-- Ignore rule CP02 & rule CP03
SeLeCt  1 from tBl ;    -- noqa: CP02,CP03

-- Ignore all parsing errors
SeLeCt from tBl ;       -- noqa: PRS
```

::: tip NOTE
It should be noted that ignoring ``TMP`` and ``PRS`` errors can lead to
incorrect ``sqlfluff lint`` and ``sqfluff fix`` results as `SQLFluff` can
misinterpret the SQL being analysed.
:::

## Ignoring line ranges

Similar to [pylint's "pylint" directive](http://pylint.pycqa.org/en/latest/user_guide/message-control.html), ranges of lines can be ignored by
adding `-- noqa:disable=<rule>[,...] | all` to the line. Following this
directive, specified rules (or all rules, if "all" was specified) will be
ignored until a corresponding `-- noqa:enable=<rule>[,...] | all` directive.

```sql

-- Ignore rule AL02 from this line forward
SELECT col_a a FROM foo -- noqa: disable=AL02

-- Ignore all rules from this line forward
SELECT col_a a FROM foo -- noqa: disable=all

-- Enforce all rules from this line forward
SELECT col_a a FROM foo -- noqa: enable=all
```


## `.sqlfluffignore`

Similar to [Git's](https://git-scm.com/docs/gitignore#_pattern_format) `.gitignore` and [Docker's](https://docs.docker.com/engine/reference/builder/#dockerignore-file) `.dockerignore`,
SQLFluff supports a `sqlfluffignore` file to control which files are and
aren't linted. Under the hood we use the python [pathspec library](https://python-path-specification.readthedocs.io/) which also
has a brief tutorial in their documentation.

An example of a potential `sqlfluffignore` placed in the root of your
project would be:

```ini

# Comments start with a hash.

# Ignore anything in the "temp" path
/temp/

# Ignore anything called "testing.sql"
testing.sql

# Ignore any ".tsql" files
*.tsql
```

Ignore files can also be placed in subdirectories of a path which is being
linted and the sub files will also be applied within that subdirectory.

## Ignoring types of errors

General *categories* of errors can be ignored using the ``--ignore`` command
line option or the ``ignore`` setting in `sqlfluffignore`. Types of errors
that can be ignored include:

* `lexing`
* `linting`
* `parsing`
* `templating`
