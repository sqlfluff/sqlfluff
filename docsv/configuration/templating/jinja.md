# Jinja templater

The Jinja templater uses [Jinja2](https://jinja.palletsprojects.com/) to render templates.

There are multiple, complementary ways of configuring the Jinja templater.

- Reading variables and Jinja macros directly from the SQLFLuff config file
- Loading macros from a path
- Using a library

| Configuration | Variables | Macros | Filters | Documentation |
|---|---|---|---|---|
| Config file | ✅ | ✅ | ❌ | [Complex Jinja Variable Templating](#complex-jinja-variable-templating) and [Jinja Macro Templating (from config)](#jinja-macro-templating-from-config) |
| Macro Path | ❌ | ✅ | ❌ | [Jinja Macro Templating (from file)](#jinja-macro-templating-from-file) |
| Library | ✅ | ✅ | ✅ | [Library Templating](#library-templating) |

For example, a snippet from a `.sqlfluff` file that uses all config
options:

```ini
[sqlfluff]
templater = jinja

[sqlfluff:templater:jinja]
apply_dbt_builtins = True
load_macros_from_path = my_macros
loader_search_path = included_templates
library_path = sqlfluff_libs
exclude_macros_from_path = my_macros_exclude

[sqlfluff:templater:jinja:context]
my_list = ['a', 'b', 'c']
MY_LIST = ("d", "e", "f")
my_where_dict = {"field_1": 1, "field_2": 2}

[sqlfluff:templater:jinja:macros]
a_macro_def = {% macro my_macro(n) %}{{ n }} + {{ n * 2 }}{% endmacro %}
```

## Complex Jinja Variable Templating

Apart from the Generic variable templating that is supported for all
templaters, two more advanced features of variable templating are available for
Jinja.

*case sensitivity* and *native python types*.
Both are illustrated in the following example:

```ini
[sqlfluff:templater:jinja:context]
my_list = ['a', 'b', 'c']
MY_LIST = ("d", "e", "f")
my_where_dict = {"field_1": 1, "field_2": 2}
```

```sql
SELECT
    {% for elem in MY_LIST %}
        '{{elem}}' {% if not loop.last %}||{% endif %}
    {% endfor %} as concatenated_list
FROM tbl
WHERE
    {% for field, value in my_where_dict.items() %}
        {{field}} = {{value}} {% if not loop.last %}and{% endif %}
    {% endfor %}
```

...will render as...

```sql
SELECT
    'd' || 'e' || 'f' as concatenated_list
FROM tbl
WHERE
    field_1 = 1 and field_2 = 2
```

Note that the variable was replaced in a case sensitive way and that the
settings in the config file were interpreted as native python types.

## Jinja Macro Templating (from config)

Macros (which also look and feel like *functions*) are available only in the
*jinja* templater. Similar to [Generic Variable Templating](generic), these are
specified in config files, what's different in this case is how they are named.
Similar to the *context* section above, macros are configured separately in the
*macros* section of the config.

Consider the following example.

If passed the following *.sql* file:

```sql
SELECT {{ my_macro(6) }} FROM some_table
```

...and the following configuration in *.sqlfluff* in the same directory (note
the tight control of whitespace):

```ini
[sqlfluff:templater:jinja:macros]
a_macro_def = {% macro my_macro(n) %}{{ n }} + {{ n * 2 }}{% endmacro %}
```

...then before parsing, the sql will be transformed to:

```sql
SELECT 6 + 12 FROM some_table
```

Note that in the code block above, the variable name in the config is
*a_macro_def*, and this isn't apparently otherwise used anywhere else.
Broadly this is accurate, however within the configuration loader this will
still be used to overwrite previous *values* in other config files. As such
this introduces the idea of config *blocks* which could be selectively
overwritten by other configuration files downstream as required.

## Jinja Macro Templating (from file)

In addition to macros specified in the config file, macros can also be
loaded from files or folders. This is specified in the config file:

```ini
[sqlfluff:templater:jinja]
load_macros_from_path = my_macros,other_macros
```

`load_macros_from_path` is a comma-separated list of `.sql` files or
folders. Locations are *relative to the config file*. For example, if the
config file above was found at `/home/my_project/.sqlfluff`, then
SQLFluff will look for macros in the folders `/home/my_project/my_macros/`
and  `/home/my_project/other_macros/`, including any of their subfolders.
Any macros defined in the config will always take precedence over a macro
defined in the path.

`exclude_macros_from_path` works in the same manner as `load_macros_from_path` but
allows you to have sqlfluff ignore certain macros. This can be useful if you have
custom jinja tags.

Macros loaded from these files are available in every `.sql` file without
requiring a Jinja `include` or `import`.  They are loaded into the
[`Jinja Global Namespace`](https://jinja.palletsprojects.com/en/3.1.x/api/#global-namespace).

::: tip NOTE
The `load_macros_from_path` setting also defines the search
path for Jinja
[`include`](https://jinja.palletsprojects.com/en/3.1.x/templates/#include) or
[`import`](https://jinja.palletsprojects.com/en/3.1.x/templates/#import).
As with loaded macros, subdirectories are also supported. For example,
if `load_macros_from_path` is set to `my_macros`, and there is a
file `my_macros/subdir/my_file.sql`, you can do:
:::

```jinja
{% include 'subdir/my_file.sql' %}
```

If you would like to define the Jinja search path without also loading the
macros into the global namespace, use the `loader_search_path` setting
instead.

::: tip NOTE
Throughout the templating process **whitespace** will still be treated
rigorously, and this includes **newlines**. In particular you may choose
to provide *dummy* macros in your configuration different from the actual
macros used in production.
:::

::: warning REMEMBER
The reason SQLFluff supports macros is to *enable* it to parse
templated sql without it being a blocker. It shouldn't be a requirement that
the *templating* is accurate - it only needs to work well enough that
*parsing* and *linting* are helpful.
:::

## Builtin Jinja Macro Blocks

One of the main use cases which inspired *SQLFluff* as a project was [dbt](https://www.getdbt.com/).
It uses jinja templating extensively and leads to some users maintaining large
repositories of sql files which could potentially benefit from some linting.

::: tip NOTE
*SQLFluff* has now a tighter integration with dbt through the "dbt" templater.
It is the recommended templater for dbt projects. If used, it eliminates the
need for the overrides described in this section.

To use the dbt templater, go to [dbt templater](dbt).
:::

*SQLFluff* anticipates this use case and provides some built in macro blocks
in the [Default Configuration](../defaults) which assist in getting started with [dbt](https://www.getdbt.com/)
projects. In particular it provides mock objects for:

* *ref*: The mock version of this provided simply returns the model reference
  as the name of the table. In most cases this is sufficient.
* *config*: A regularly used macro in [dbt](https://www.getdbt.com/) to set configuration values. For
  linting purposes, this makes no difference and so the provided macro simply
  returns nothing.

::: tip NOTE
If there are other builtin macros which would make your life easier,
consider submitting the idea (or even better a pull request) on [github](https://www.github.com/sqlfluff/sqlfluff).
:::

## Library Templating

If using *SQLFluff* with jinja as your templater, you may have library
function calls within your sql files that can not be templated via the
normal macro templating mechanisms:

```sql
SELECT foo, bar FROM baz {{ dbt_utils.group_by(2) }}
```

To template these libraries, you can use the `sqlfluff:jinja:library_path`
config option:

```ini
[sqlfluff:templater:jinja]
library_path = sqlfluff_libs
```

This will pull in any python modules from that directory and allow sqlfluff
to use them in templates. In the above example, you might define a file at
`sqlfluff_libs/dbt_utils.py` as:

```python
def group_by(n):
    return "GROUP BY 1,2"
```

If an `__init__.py` is detected, it will be loaded alongside any modules and
submodules found within the library path.

```sql
SELECT
    {{ custom_sum('foo', 'bar') }},
    {{ foo.bar.another_sum('foo', 'bar') }}
FROM
    baz
```

`sqlfluff_libs/__init__.py`:

```python
def custom_sum(a: str, b: str) -> str:
    return a + b
```

`sqlfluff_libs/foo/__init__.py`:

```python
# empty file
```

`sqlfluff_libs/foo/bar.py`:

```python
def another_sum(a: str, b: str) -> str:
    return a + b
```

Additionally, the library can be used to expose [Jinja Filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#filters) to the Jinja environment used by SQLFluff.

This is achieve by setting a global variable named `SQLFLUFF_JINJA_FILTERS`.
`SQLFLUFF_JINJA_FILTERS` is a dictionary where

* dictionary keys map to the Jinja filter name
* dictionary values map to the Python callable

For example, to make the Airflow filter `ds` available to SQLFLuff, add
the following to the `__init__.py` of the library:

```python
# https://github.com/apache/airflow/blob/main/airflow/templates.py#L53
def ds_filter(value: datetime.date | datetime.time | None) -> str | None:
    """Date filter."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")
```

     SQLFLUFF_JINJA_FILTERS = {"ds": ds_filter}

Now, `ds` can be used in SQL

```sql
SELECT "{{ "2000-01-01" | ds }}";
```

## Jinja loader search path

The Jinja environment can be configured to search for files included with
[`include`](https://jinja.palletsprojects.com/en/3.1.x/templates/#include) or
[`import`](https://jinja.palletsprojects.com/en/3.1.x/templates/#import) in a
list of folders. This is specified in the config file:

```ini
[sqlfluff:templater:jinja]
loader_search_path = included_templates,other_templates
```

`loader_search_path` is a comma-separated list of folders. Locations are
*relative to the config file*. For example, if the config file above was found
at `/home/my_project/.sqlfluff`, then SQLFluff will look for included
files in the folders `/home/my_project/included_templates/` and
`/home/my_project/other_templates/`, including any of their subfolders.
For example, this will read from
`/home/my_project/included_templates/my_template.sql`:

```jinja
{% include 'included_templates/my_template.sql' %}
```

Any folders specified in the `load_macros_from_path` setting are
automatically appended to the `loader_search_path`.  It is not necessary to
specify a given directory in both settings.

Unlike the `load_macros_from_path` setting, any macros within these
folders are *not* automatically loaded into the global namespace.  They must be
explicitly imported using the
[`import`](https://jinja.palletsprojects.com/en/3.1.x/templates/#import) Jinja
directive.  If you would like macros to be automatically included in the
global Jinja namespace, use the `load_macros_from_path` setting instead.

## Interaction with `--ignore=templating`

Ignoring Jinja templating errors provides a way for users to use SQLFluff
while reducing or avoiding the need to spend a lot of time adding variables
to `[sqlfluff:templater:jinja:context]`.

When `--ignore=templating` is enabled, the Jinja templater behaves a bit
differently. This additional behavior is *usually* but not *always* helpful
for making the file at least partially parsable and fixable. It definitely
doesn’t **guarantee** that every file can be fixed, but it’s proven useful for
some users.

Here's how it works:

* Within the expanded SQL, undefined variables are automatically *replaced*
  with the corresponding string value.
* If you do: `{% include query %}`, and the variable `query` is not
  defined, it returns a “file” containing the string `query`.
* If you do: `{% include "query_file.sql" %}`, and that file does not exist
  or you haven’t configured a setting for `load_macros_from_path` or
  `loader_search_path`, it returns a “file” containing the text
  `query_file`.

For example:

```sql
select {{ my_variable }}
from {% include "my_table.sql" %}
```

is interpreted as:

```sql
select my_variable
from my_table
```

The values provided by the Jinja templater act *a bit* (not exactly) like a
mixture of several types:

* `str`
* `int`
* `list`
* Jinja's `Undefined` [class](https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Undefined)

Because the values behave like `Undefined`, it's possible to replace them
using Jinja's `default()` [`filter`](https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.default).
For example:

```sql
select {{ my_variable | default("col_a") }}
from my_table
```

is interpreted as:

```sql
select col_a
from my_table
```
