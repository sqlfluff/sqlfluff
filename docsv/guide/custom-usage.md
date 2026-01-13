# Custom Usage

So far we've covered the stock settings of *SQLFluff*, but there
are many different ways that people style their sql, and if you
or your organisation have different conventions, then many of
these behaviours can be configured. For example, given the
example above, what if we actually think that indents should only
be two spaces, and rather than uppercase keywords, they should
all be lowercase?

To achieve this we create a configuration file named `.sqlfluff`
and place it in the same directory as the current file. In that file
put the following content:

```ini
[sqlfluff]
dialect = ansi

[sqlfluff:indentation]
tab_space_size = 2

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = lower
```

Then rerun the same command as before.

```bash
$ sqlfluff fix test.sql --rules LT02,LT12,CP01,ST06,LT09,LT01
```

Then examine the file again, and you'll notice that the
file has been fixed accordingly.

```sql
select
    c as bar,
    a + b as foo
from my_table
```

For a full list of configuration options check out [Default Configuration](../configuration/defaults).
Note that in our example here we've only set a few configuration values
and any other configuration settings remain as per the default config.
To see how these options apply to specific rules check out the
"Configuration" section within each rule's documentation in [Rule Reference](../reference/rules/index).
