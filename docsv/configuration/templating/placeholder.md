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

The text captured by the named group `param_name` is used to look up the
sample value in the configuration. If the group is missing, the parameter is
assumed to be positional and numbers are used instead.

Also consider making a pull request to the project to have your style added,
it may be useful to other people and simplify your configuration.
:::

## Overriding an inherited matcher

Set an inherited `param_style` or `param_regex` to `None` in a nested
`.sqlfluff` file before selecting the other matcher. For example, to replace
an inherited named style with a custom regex:

```ini
[sqlfluff:templater:placeholder]
param_style = None
param_regex = __(?P<param_name>[\w_]+)__
my_name = 'john'
```

In this example, `SELECT __my_name__` renders as `SELECT 'john'`: the group
`param_name` captures `my_name`, which selects the configured sample value.

To switch back to a named style, set `param_regex = None` and provide
`param_style`. Exactly one matcher must have a non-`None` value.

An empty `param_regex` (a setting with no value after `=`) does not clear the
inherited matcher. It compiles to an empty regular expression that matches
at every position in the input. Use `None` to clear it instead.
