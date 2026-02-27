# Generic Variable Templating

Variables are available in all the templaters.
By default the templating engine will expect variables for templating to be
available in the config, and the templater will be look in the section
corresponding to the context for that templater. By convention, the config for
the `jinja` templater is found in the `sqlfluff:templater:jinja:context`
section, the config for the `python` templater is found in the
`sqlfluff:templater:python:context` section, the one for the `placeholder`
templater is found in the `sqlfluff:templater:placeholder:context` section.

For example, if passed the following *.sql* file:

```sql
SELECT {{ num_things }} FROM {{ tbl_name }} WHERE id > 10 LIMIT 5
```

...and the following configuration in *.sqlfluff* in the same directory:

```ini
[sqlfluff:templater:jinja:context]
num_things=456
tbl_name=my_table
```

...then before parsing, the sql will be transformed to:

```sql
SELECT 456 FROM my_table WHERE id > 10 LIMIT 5
```

::: warning NOTE
If there are variables in the template which cannot be found in
the current configuration context, then this will raise a
`SQLTemplatingError` and this will appear as a violation without
a line number, quoting the name of the variable that couldn't be found.
:::
