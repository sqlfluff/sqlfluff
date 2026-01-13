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
