# Placeholder templater

Libraries such as SQLAlchemy or Psycopg use different parameter placeholder
styles to mark where a parameter has to be inserted in the query.

For example a query in SQLAlchemy can look like this:

```sql
SELECT * FROM table WHERE id = :myid
```

At runtime `:myid` will be replace by a value provided by the application and
escaped as needed, but this is not standard SQL and cannot be parsed as is.

In order to parse these queries is then necessary to replace these
placeholders with sample values, and this is done with the placeholder
templater.

Placeholder templating can be enabled in the config using:

```ini
[sqlfluff]
templater = placeholder
```

A few common styles are supported:

```sql
-- colon
WHERE bla = :my_name

-- colon_nospaces
-- (use with caution as more prone to false positives)
WHERE bla = table:my_name

-- colon_optional_quotes
SELECT :"column" FROM :table WHERE bla = :'my_name'

-- numeric_colon
WHERE bla = :2

-- pyformat
WHERE bla = %(my_name)s

-- dollar
WHERE bla = $my_name or WHERE bla = ${my_name}

-- databricks (notebook widget and dashboard parameters)
WHERE bla = ${my_name} or WHERE bla = $my_name or
    WHERE bla = ${dotted.name} or WHERE bla = {{ dashboard_param }} or
    WHERE bla = ${}  -- empty widget, filled by position like question_mark

-- dollar_surround (DbUp compatible variable)
WHERE bla = $my_name$

-- question_mark
WHERE bla = ?

-- numeric_dollar
WHERE bla = $3 or WHERE bla = ${3}

-- percent
WHERE bla = %s

-- ampersand
WHERE bla = &s or WHERE bla = &{s} or USE DATABASE MARK_{ENV}
```

These can be configured by setting `param_style` to the names above:

```ini
[sqlfluff:templater:placeholder]
param_style = colon
my_name = 'john'
```

then you can set sample values for each parameter, like `my_name`
above. Notice that the value needs to be escaped as it will be replaced as a
string during parsing. When the sample values aren't provided, the templater
will use parameter names themselves by default.

When parameters are positional, like `question_mark`, then their name is
simply the order in which they appear, starting with `1`.

```ini
[sqlfluff:templater:placeholder]
param_style = question_mark
1 = 'john'
```

To process multiple styles, set `param_style` to a comma-separated list:

```ini
[sqlfluff:templater:placeholder]
param_style = colon, pyformat, percent
my_name = 'john'
1 = 42
```

This replaces both `:my_name` and `%(my_name)s` with `'john'`, and the first
`%s` with `42`. Positional parameters share one counter across all selected
styles, in the order they appear in the SQL. Named parameters do not advance
that counter. Replacements are not processed again.

If multiple styles match at the same position, the first listed style wins.
List more specific styles first, for example `dollar_surround, dollar` to
match `$my_name$` before `$my_name`. A TOML configuration can also use a list
of strings, such as `param_style = ["colon", "pyformat"]`.

In case you need a parameter style different from the ones above, you can pass
a custom regex.

```ini
[sqlfluff:templater:placeholder]
param_regex = __(?P<param_name>[\w_]+)__
my_name = 'john'
```

::: tip NOTE
Quotes around `param_regex` in the config are
interpreted literally by the templater.
e.g. `param_regex='__(?P<param_name>[\w_]+)__'` matches
`'__some_param__'` not `__some_param__`

the named parameter `param_name` will be used as the key to replace, if
missing, the parameter is assumed to be positional and numbers are used
instead.

Also consider making a pull request to the project to have your style added,
it may be useful to other people and simplify your configuration.
:::
