# Python templater

Uses native Python f-strings. As described in
[Generic Templating](generic), an example usage would look be
configured as follows:

If passed the following *.sql* file:

```sql
SELECT * FROM {tbl_name}
```

...and the following configuration in *.sqlfluff* in the same directory:

```ini
[sqlfluff]
templater = python

[sqlfluff:templater:python:context]
tbl_name = my_table
```

...then before parsing, the sql will be transformed to:

```sql
SELECT * FROM my_table
```

## Default Values

To provide a shared placeholder for variables without an explicit context value,
set `default_value` in the Python templater configuration:

```ini
[sqlfluff:templater:python]
default_value = 0

[sqlfluff:templater:python:context]
min_age = 18
```

For example, this SQL:

```sql
SELECT * FROM users WHERE age > {min_age} AND city = '{city_name}'
```

...renders as:

```sql
SELECT * FROM users WHERE age > 18 AND city = '0'
```

Explicit context values always take priority, including `0`, `False`, and empty
strings. Defaults use the same Python literal type inference as context values,
so `0` supports numeric format specifications such as `{min_age:d}`. A string
default must be compatible with any format specifications used in the template.
Defaults also apply to missing dictionary keys and dotted variable names.

Without `default_value` (or if it is `None`), missing variables still raise
templating errors unless `ignore = templating` is configured. If both options
are set, the configured default takes priority over variable-name placeholders.
This option only supplies values for rendering; fixes preserve the placeholders
in the source SQL. Choose a default that makes sense for your queries: one value
cannot represent every possible SQL expression or data type.

## Complex Python Variable Templating

[Python string formatting](https://docs.python.org/3/library/string.html#format-string-syntax) supports accessing object attributes
via dot notation (e.g. `{foo.bar}`).  However, since we cannot create Python
objects within configuration files, we need a workaround in order to provide
dummy values to render templates containing these values.  The SQLFluff
python templater will interpret any variable containing a "." as a
dictionary lookup on the *magic* fixed context key `sqlfluff`.

```sql
-- this SQL
SELECT * FROM {foo.bar}

-- becomes this
SELECT * FROM {sqlfluff["foo.bar"]}
```

..which can be populated using the following configuration:

```ini
[sqlfluff:templater:python:context]
sqlfluff = {"foo.bar": "abc"}
```
