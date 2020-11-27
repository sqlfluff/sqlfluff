This [dbt](https://github.com/fishtown-analytics/dbt) package contains macros that can be (re)used across dbt projects.

## Installation Instructions
Check [dbt Hub](https://hub.getdbt.com/fishtown-analytics/dbt_utils/latest/) for the latest installation instructions, or [read the docs](https://docs.getdbt.com/docs/package-management) for more information on installing packages.

----

## Macros
### Cross-database
While these macros are cross database, they do not support all databases.
These macros are provided to make date calculations easier and are not a core part of dbt.
Most date macros are not supported on postgres.

#### current_timestamp ([source](macros/cross_db_utils/current_timestamp.sql))
This macro returns the current timestamp.

Usage:
```
{{ dbt_utils.current_timestamp() }}
```

#### dateadd ([source](macros/cross_db_utils/dateadd.sql))
This macro adds a time/day interval to the supplied date/timestamp. Note: The `datepart` argument is database-specific.

Usage:
```
{{ dbt_utils.dateadd(datepart='day', interval=1, from_date_or_timestamp="'2017-01-01'") }}
```

#### datediff ([source](macros/cross_db_utils/datediff.sql))
This macro calculates the difference between two dates.

Usage:
```
{{ dbt_utils.datediff("'2018-01-01'", "'2018-01-20'", 'day') }}
```


#### split_part ([source](macros/cross_db_utils/split_part.sql))
This macro splits a string of text using the supplied delimiter and returns the supplied part number (1-indexed).

Usage:
```
{{ dbt_utils.split_part(string_text='1,2,3', delimiter_text=',', part_number=1) }}
```

#### date_trunc ([source](macros/cross_db_utils/date_trunc.sql))
Truncates a date or timestamp to the specified datepart. Note: The `datepart` argument is database-specific.

Usage:
```
{{ dbt_utils.date_trunc(datepart, date) }}
```

#### last_day ([source](macros/cross_db_utils/last_day.sql))
Gets the last day for a given date and datepart. Notes:

- The `datepart` argument is database-specific.
- This macro currently only supports dateparts of `month` and `quarter`.

Usage:
```
{{ dbt_utils.last_day(date, datepart) }}
```

#### width_bucket ([source](macros/cross_db_utils/width_bucket.sql))
This macro is modeled after the `width_bucket` function natively available in Snowflake.

From the original Snowflake [documentation](https://docs.snowflake.net/manuals/sql-reference/functions/width_bucket.html):

Constructs equi-width histograms, in which the histogram range is divided into intervals of identical size, and returns the bucket number into which the value of an expression falls, after it has been evaluated. The function returns an integer value or null (if any input is null).
Notes:

- `expr`
  The expression for which the histogram is created. This expression must evaluate to a numeric value or to a value that can be implicitly converted to a numeric value.

- `min_value` and `max_value`
  The low and high end points of the acceptable range for the expression. The end points must also evaluate to numeric values and not be equal.

- `num_buckets`
  The desired number of buckets; must be a positive integer value. A value from the expression is assigned to each bucket, and the function then returns the corresponding bucket number.

  When an expression falls outside the range, the function returns:

    `0` if the expression is less than min_value.

    `num_buckets + 1` if the expression is greater than or equal to max_value.


Usage:
```
{{ dbt_utils.width_bucket(expr, min_value, max_value, num_buckets) }}
```

---
### Date/Time
#### date_spine ([source](macros/datetime/date_spine.sql))
This macro returns the sql required to build a date spine.

Usage:
```
{{ dbt_utils.date_spine(
    datepart="minute",
    start_date="to_date('01/01/2016', 'mm/dd/yyyy')",
    end_date="dateadd(week, 1, current_date)"
   )
}}
```
---
### Geo
#### haversine_distance ([source](macros/geo/haversine_distance.sql))
This macro calculates the [haversine distance](http://daynebatten.com/2015/09/latitude-longitude-distance-sql/) between a pair of x/y coordinates.

Usage:
```
{{ dbt_utils.haversine_distance(lat1=<float>,lon1=<float>,lat2=<float>,lon2=<float>) }}
```
---
### Schema Tests
#### equal_rowcount ([source](macros/schema_tests/equal_rowcount.sql))
This schema test asserts the that two relations have the same number of rows.

Usage:
```yaml
version: 2

models:
  - name: model_name
    tests:
      - dbt_utils.equal_rowcount:
          compare_model: ref('other_table_name')

```

#### equality ([source](macros/schema_tests/equality.sql))
This schema test asserts the equality of two relations. Optionally specify a subset of columns to compare.

Usage:
```yaml
version: 2

models:
  - name: model_name
    tests:
      - dbt_utils.equality:
          compare_model: ref('other_table_name')
          compare_columns:
            - first_column
            - second_column

```

#### expression_is_true ([source](macros/schema_tests/expression_is_true.sql))
This schema test asserts that a valid sql expression is true for all records. This is useful when checking integrity across columns, for example, that a total is equal to the sum of its parts, or that at least one column is true.

Usage:
```yaml
version: 2

models:
  - name: model_name
    tests:
      - dbt_utils.expression_is_true:
          expression: "col_a + col_b = total"

```

The macro accepts an optional parameter `condition` that allows for asserting
the `expression` on a subset of all records.

Usage:
```yaml
version: 2

models:
  - name: model_name
    tests:
      - dbt_utils.expression_is_true:
          expression: "col_a + col_b = total"
          condition: "created_at > '2018-12-31'"

```


#### recency ([source](macros/schema_tests/recency.sql))
This schema test asserts that there is data in the referenced model at least as recent as the defined interval prior to the current timestamp.

Usage:
```yaml
version: 2

models:
  - name: model_name
    tests:
      - dbt_utils.recency:
          datepart: day
          field: created_at
          interval: 1
```

#### at_least_one ([source](macros/schema_tests/at_least_one.sql))
This schema test asserts if column has at least one value.

Usage:
```yaml
version: 2

models:
  - name: model_name
    columns:
      - name: col_name
        tests:
          - dbt_utils.at_least_one


```

#### not_constant ([source](macros/schema_tests/not_constant.sql))
This schema test asserts if column does not have same value in all rows.

Usage:
```yaml
version: 2

models:
  - name: model_name
    columns:
      - name: column_name
        tests:
          - dbt_utils.not_constant

```

#### cardinality_equality ([source](macros/schema_tests/cardinality_equality.sql))
This schema test asserts if values in a given column have exactly the same cardinality as values from a different column in a different model.

Usage:
```yaml
version: 2

models:
  - name: model_name
    columns:
      - name: from_column
        tests:
          - dbt_utils.cardinality_equality:
              field: other_column_name
              to: ref('other_model_name')

```

#### unique_where ([source](macros/schema_tests/unique_where.sql))
This test validates that there are no duplicate values present in a field for a subset of rows by specifying a `where` clause.

Usage:
```yaml
version: 2

models:
  - name: my_model
    columns:
      - name: id
        tests:
          - dbt_utils.unique_where:
              where: "_deleted = false"
```

#### not_null_where ([source](macros/schema_tests/not_null_where.sql))
This test validates that there are no null values present in a column for a subset of rows by specifying a `where` clause.

Usage:
```yaml
version: 2

models:
  - name: my_model
    columns:
      - name: id
        tests:
          - dbt_utils.not_null_where:
              where: "_deleted = false"
```

#### relationships_where ([source](macros/schema_tests/relationships_where.sql))
This test validates the referential integrity between two relations (same as the core relationships schema test) with an added predicate to filter out some rows from the test. This is useful to exclude records such as test entities, rows created in the last X minutes/hours to account for temporary gaps due to ETL limitations, etc.

Usage:
```yaml
version: 2

models:
  - name: model_name
    columns:
      - name: id
        tests:
          - dbt_utils.relationships_where:
              to: ref('other_model_name')
              field: client_id
              from_condition: id <> '4ca448b8-24bf-4b88-96c6-b1609499c38b'

```

#### mutually_exclusive_ranges ([source](macros/schema_tests/mutually_exclusive_ranges.sql))
This test confirms that for a given lower_bound_column and upper_bound_column,
the ranges of between the lower and upper bounds do not overlap with the ranges
of another row.

**Usage:**
```yaml
version: 2

models:
  # test that age ranges do not overlap
  - name: age_brackets
    tests:
      - dbt_utils.mutually_exclusive_ranges:
          lower_bound_column: min_age
          upper_bound_column: max_age
          gaps: not_allowed

  # test that each customer can only have one subscription at a time
  - name: subscriptions
    tests:
      - dbt_utils.mutually_exclusive_ranges:
          lower_bound_column: started_at
          upper_bound_column: ended_at
          partition_by: customer_id
          gaps: required
```
**Args:**
* `lower_bound_column` (required): The name of the column that represents the
lower value of the range. Must be not null.
* `upper_bound_column` (required): The name of the column that represents the
upper value of the range. Must be not null.
* `partition_by` (optional): If a subset of records should be mutually exclusive
(e.g. all periods for a single subscription_id are mutually exclusive), use this
argument to indicate which column to partition by. `default=none`
* `gaps` (optional): Whether there can be gaps are allowed between ranges.
`default='allowed', one_of=['not_allowed', 'allowed', 'required']`

**Note:** Both `lower_bound_column` and `upper_bound_column` should be not null.
If this is not the case in your data source, consider passing a coalesce function
to the `lower_` and `upper_bound_column` arguments, like so:
```yaml
version: 2

models:
- name: subscriptions
  tests:
    - dbt_utils.mutually_exclusive_ranges:
        lower_bound_column: coalesce(started_at, '1900-01-01')
        upper_bound_column: coalesce(ended_at, '2099-12-31')
        partition_by: customer_id
        gaps: allowed
```

**Understanding the `gaps` parameter:**
Here are a number of examples for each allowed `gaps` parameter.
* `gaps:not_allowed`: The upper bound of one record must be the lower bound of
the next record.

| lower_bound | upper_bound |
|-------------|-------------|
| 0           | 1           |
| 1           | 2           |
| 2           | 3           |

* `gaps:allowed` (default): There may be a gap between the upper bound of one
record and the lower bound of the next record.

| lower_bound | upper_bound |
|-------------|-------------|
| 0           | 1           |
| 2           | 3           |
| 3           | 4           |

* `gaps:required`: There must be a gap between the upper bound of one record and
the lower bound of the next record (common for date ranges).

| lower_bound | upper_bound |
|-------------|-------------|
| 0           | 1           |
| 2           | 3           |
| 4           | 5           |

#### unique_combination_of_columns ([source](macros/schema_tests/unique_combination_of_columns.sql))
This test confirms that the combination of columns is unique. For example, the
combination of month and product is unique, however neither column is unique
in isolation.

We generally recommend testing this uniqueness condition by either:
* generating a [surrogate_key](#surrogate_key-source) for your model and testing
the uniqueness of said key, OR
* passing the `unique` test a coalesce of the columns (as discussed [here](https://docs.getdbt.com/docs/building-a-dbt-project/testing-and-documentation/testing/#testing-expressions)).

However, these approaches can become non-perfomant on large data sets, in which
case we recommend using this test instead.

**Usage:**
```yaml
- name: revenue_by_product_by_month
  tests:
    - dbt_utils.unique_combination_of_columns:
        combination_of_columns:
          - month
          - product
```

An optional `quote_columns` parameter (`default=false`) can also be used if a column name needs to be quoted.

```yaml
- name: revenue_by_product_by_month
  tests:
    - dbt_utils.unique_combination_of_columns:
        combination_of_columns:
          - month
          - group
        quote_columns: true
```

---
### SQL helpers
#### get_query_results_as_dict ([source](macros/sql/get_query_results_as_dict.sql))
This macro returns a dictionary from a sql query, so that you don't need to interact with the Agate library to operate on the result

Usage:
```
-- Returns a dictionary of the users table where the state is California
{% set california_cities = dbt_utils.get_query_results_as_dict("select * from" ~ ref('cities') ~ "where state = 'CA' and city is not null ") %}
select
  city,
{% for city in california_cities %}
  sum(case when city = {{ city }} then 1 else 0 end) as users_in_{{ city }},
{% endfor %}
  count(*) as total
from {{ ref('users') }}

group by 1
```

#### get_column_values ([source](macros/sql/get_column_values.sql))
This macro returns the unique values for a column in a given [relation](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation).
It takes an options `default` argument for compiling when the relation does not already exist.

Usage:
```
-- Returns a list of the top 50 states in the `users` table
{% set states = dbt_utils.get_column_values(table=ref('users'), column='state', max_records=50, default=[]) %}

{% for state in states %}
    ...
{% endfor %}

...
```
#### get_relations_by_prefix
Returns a list of [Relations](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation)
that match a given prefix, with an optional exclusion pattern. It's particularly
handy paired with `union_relations`.
**Usage:**
```
-- Returns a list of relations that match schema.prefix%
{% set relations = dbt_utils.get_relations_by_prefix('my_schema', 'my_prefix') %}

-- Returns a list of relations as above, excluding any that end in `deprecated`
{% set relations = dbt_utils.get_relations_by_prefix('my_schema', 'my_prefix', '%deprecated') %}

-- Example using the union_relations macro
{% set event_relations = dbt_utils.get_relations_by_prefix('events', 'event_') %}
{{ dbt_utils.union_relations(relations = event_relations) }}
```

**Args:**
* `schema` (required): The schema to inspect for relations.
* `prefix` (required): The prefix of the table/view (case insensitive)
* `exclude` (optional): Exclude any relations that match this pattern.
* `database` (optional, default = `target.database`): The database to inspect
for relations.

#### get_relations_by_pattern
> This was built from the get_relations_by_prefix macro.

Returns a list of [Relations](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation)
that match a given schema or table pattern and table/view name with an optional exclusion pattern. Like its cousin
get_relations_by_prefix, it's particularly handy paired with `union_relations`.
**Usage:**
```
-- Returns a list of relations that match schema%.table
{% set relations = dbt_utils.get_relations_by_pattern('schema_pattern%', 'table_pattern') %}

-- Returns a list of relations that match schema.table%
{% set relations = dbt_utils.get_relations_by_pattern('schema_pattern', 'table_pattern%') %}

-- Returns a list of relations as above, excluding any that end in `deprecated`
{% set relations = dbt_utils.get_relations_by_pattern('schema_pattern', 'table_pattern%', '%deprecated') %}

-- Example using the union_relations macro
{% set event_relations = dbt_utils.get_relations_by_pattern('venue%', 'clicks') %}
{{ dbt_utils.union_relations(relations = event_relations) }}
```

**Args:**
* `schema_pattern` (required): The schema pattern to inspect for relations.
* `table_pattern` (required): The name of the table/view (case insensitive).
* `exclude` (optional): Exclude any relations that match this table pattern.
* `database` (optional, default = `target.database`): The database to inspect
for relations.

#### group_by ([source](macros/sql/groupby.sql))
This macro build a group by statement for fields 1...N

Usage:
```
{{ dbt_utils.group_by(n=3) }} --> group by 1,2,3
```

#### star ([source](macros/sql/star.sql))
This macro generates a list of all fields that exist in the `from` relation, excluding any fields listed in the `except` argument. The construction is identical to `select * from {{ref('my_model')}}`, replacing star (`*`) with the star macro. This macro also has an optional `relation_alias` argument that will prefix all generated fields with an alias.

Usage:
```
select
{{ dbt_utils.star(from=ref('my_model'), except=["exclude_field_1", "exclude_field_2"]) }}
from {{ref('my_model')}}
```

#### union_relations ([source](macros/sql/union.sql))

This macro unions together an array of [Relations](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation),
even when columns have differing orders in each Relation, and/or some columns are
missing from some relations. Any columns exclusive to a subset of these
relations will be filled with `null` where not present. An new column
(`_dbt_source_relation`) is also added to indicate the source for each record.

**Usage:**
```
{{ dbt_utils.union_relations(
    relations=[ref('my_model'), source('my_source', 'my_table')],
    exclude=["_loaded_at"]
) }}
```
**Args:**
* `relations` (required): An array of [Relations](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation).
* `exclude` (optional): A list of column names that should be excluded from
the final query.
* `include` (optional): A list of column names that should be included in the
final query. Note the `include` and `exclude` parameters are mutually exclusive.
* `column_override` (optional): A dictionary of explicit column type overrides,
e.g. `{"some_field": "varchar(100)"}`.``
* `source_column_name` (optional, `default="_dbt_source_relation"`): The name of
the column that records the source of this row.

#### generate_series ([source](macros/sql/generate_series.sql))
This macro implements a cross-database mechanism to generate an arbitrarily long list of numbers. Specify the maximum number you'd like in your list and it will create a 1-indexed SQL result set.

Usage:
```
{{ dbt_utils.generate_series(upper_bound=1000) }}
```

#### surrogate_key ([source](macros/sql/surrogate_key.sql))
Implements a cross-database way to generate a hashed surrogate key using the fields specified.

Usage:
```
{{ dbt_utils.surrogate_key(['field_a', 'field_b'[,...]]) }}
```

#### safe_add ([source](macros/sql/safe_add.sql))
Implements a cross-database way to sum nullable fiellds using the fields specified.

Usage:
```
{{ dbt_utils.safe_add('field_a', 'field_b'[,...]) }}
```

#### pivot ([source](macros/sql/pivot.sql))
This macro pivots values from rows to columns.

Usage:
```
{{ dbt_utils.pivot(<column>, <list of values>) }}
```

Example:

    Input: orders

    | size | color |
    |------|-------|
    | S    | red   |
    | S    | blue  |
    | S    | red   |
    | M    | red   |

    select
      size,
      {{ dbt_utils.pivot(
          'color',
          dbt_utils.get_column_values(ref('orders'), 'color')
      ) }}
    from {{ ref('orders') }}
    group by size

    Output:

    | size | red | blue |
    |------|-----|------|
    | S    | 2   | 1    |
    | M    | 1   | 0    |

Arguments:

    - column: Column name, required
    - values: List of row values to turn into columns, required
    - alias: Whether to create column aliases, default is True
    - agg: SQL aggregation function, default is sum
    - cmp: SQL value comparison, default is =
    - prefix: Column alias prefix, default is blank
    - suffix: Column alias postfix, default is blank
    - then_value: Value to use if comparison succeeds, default is 1
    - else_value: Value to use if comparison fails, default is 0
    - quote_identifiers: Whether to surround column aliases with double quotes, default is true

#### unpivot ([source](macros/sql/unpivot.sql))
This macro "un-pivots" a table from wide format to long format. Functionality is similar to pandas [melt](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.melt.html) function.

Usage:
```
{{ dbt_utils.unpivot(
  relation=ref('table_name'),
  cast_to='datatype',
  exclude=[<list of columns to exclude from unpivot>],
  remove=[<list of columns to remove>],
  field_name=<column name for field>,
  value_name=<column name for value>
) }}
```

**Usage:**

    Input: orders

    | date       | size | color | status     |
    |------------|------|-------|------------|
    | 2017-01-01 | S    | red   | complete   |
    | 2017-03-01 | S    | red   | processing |

    {{ dbt_utils.unpivot(ref('orders'), cast_to='varchar', exclude=['date','status']) }}

    Output:

    | date       | status     | field_name | value |
    |------------|------------|------------|-------|
    | 2017-01-01 | complete   | size       | S     |
    | 2017-01-01 | complete   | color      | red   |
    | 2017-03-01 | processing | size       | S     |
    | 2017-03-01 | processing | color      | red   |

**Args**:
- `relation`: The [Relation](https://docs.getdbt.com/docs/writing-code-in-dbt/class-reference/#relation) to unpivot.
- `cast_to`: The data type to cast the unpivoted values to, default is varchar
- `exclude`: A list of columns to exclude from the unpivot operation but keep in the resulting table.
- `remove`: A list of columns to remove from the resulting table.
- `field_name`: column name in the resulting table for field
- `value_name`: column name in the resulting table for value

---
### Web
#### get_url_parameter ([source](macros/web/get_url_parameter.sql))
This macro extracts a url parameter from a column containing a url.

Usage:
```
{{ dbt_utils.get_url_parameter(field='page_url', url_parameter='utm_source') }}
```

#### get_url_host ([source](macros/web/get_url_host.sql))
This macro extracts a hostname from a column containing a url.

Usage:
```
{{ dbt_utils.get_url_host(field='page_url') }}
```

#### get_url_path ([source](macros/web/get_url_path.sql))
This macro extracts a page path from a column containing a url.

Usage:
```
{{ dbt_utils.get_url_path(field='page_url') }}
```

---
### Logger
#### pretty_time ([source](macros/logger/pretty_time.sql))
This macro returns a string of the current timestamp, optionally taking a datestring format.
```sql
{#- This will return a string like '14:50:34' -#}
{{ dbt_utils.pretty_time() }}

{#- This will return a string like '2019-05-02 14:50:34' -#}
{{ dbt_utils.pretty_time(format='%Y-%m-%d %H:%M:%S') }}
```

#### pretty_log_format ([source](macros/logger/pretty_log_format.sql))
This macro formats the input in a way that will print nicely to the command line when you `log` it.
```sql
{#- This will return a string like:
"11:07:31 + my pretty message"
-#}

{{ dbt_utils.pretty_log_format("my pretty message") }}
```
#### log_info ([source](macros/logger/log_info.sql))
This macro logs a formatted message (with a timestamp) to the command line.
```sql
{{ dbt_utils.log_info("my pretty message") }}
```

```
11:07:28 | 1 of 1 START table model analytics.fct_orders........................ [RUN]
11:07:31 + my pretty message
```

### Materializations
#### insert_by_period ([source](macros/materializations/insert_by_period_materialization.sql))
`insert_by_period` allows dbt to insert records into a table one period (i.e. day, week) at a time.

This materialization is appropriate for event data that can be processed in discrete periods. It is similar in concept to the built-in incremental materialization, but has the added benefit of building the model in chunks even during a full-refresh so is particularly useful for models where the initial run can be problematic.

Should a run of a model using this materialization be interrupted, a subsequent run will continue building the target table from where it was interrupted (granted the `--full-refresh` flag is omitted).

Progress is logged in the command line for easy monitoring.

Usage:
```sql
{{
  config(
    materialized = "insert_by_period",
    period = "day",
    timestamp_field = "created_at",
    start_date = "2018-01-01",
    stop_date = "2018-06-01")
}}

with events as (

  select *
  from {{ ref('events') }}
  where __PERIOD_FILTER__ -- This will be replaced with a filter in the materialization code

)

....complex aggregates here....

```
Configuration values:
* `period`: period to break the model into, must be a valid [datepart](https://docs.aws.amazon.com/redshift/latest/dg/r_Dateparts_for_datetime_functions.html) (default='Week')
* `timestamp_field`: the column name of the timestamp field that will be used to break the model into smaller queries
* `start_date`: literal date or timestamp - generally choose a date that is earlier than the start of your data
* `stop_date`: literal date or timestamp (default=current_timestamp)

Caveats:
* This materialization is compatible with dbt 0.10.1.
* This materialization has been written for Redshift.
* This materialization can only be used for a model where records are not expected to change after they are created.
* Any model post-hooks that use `{{ this }}` will fail using this materialization. For example:
```yaml
models:
    project-name:
        post-hook: "grant select on {{ this }} to db_reader"
```
A useful workaround is to change the above post-hook to:
```yaml
        post-hook: "grant select on {{ this.schema }}.{{ this.name }} to db_reader"
```

----

### Contributing

We welcome contributions to this repo! To contribute a new feature or a fix, please open a Pull Request with 1) your changes, 2) updated documentation for the `README.md` file, and 3) a working integration test. See [this page](integration_tests/README.md) for more information.

----

### Dispatch macros

**Note:** This is primarily relevant to users and maintainers of community-supported
database plugins. If you use Postgres, Redshift, Snowflake, or Bigquery, this likely
does not apply to you.

dbt v0.18.0 introduces `adapter.dispatch()`, a reliable way to define different implementations of the same macro
across different databases.

All dispatched macros in `dbt_utils` have an override setting: a `var` named
`dbt_utils_dispatch_list` that accepts a list of package names. If you set this
variable in your project, when dbt searches for implementations of a dispatched
`dbt_utils` macro, it will search through your listed packages _before_ using
the implementations defined in `dbt_utils`.

Set the variable:
```yml
vars:
  dbt_utils_dispatch_list:
    - first_package_to_search    # likely the name of your root project
    - second_package_to_search   # likely an "add-on" package, such as spark_utils
    # dbt_utils is always the last place searched
```

When running on Spark, if dbt needs to dispatch `dbt_utils.datediff`, it will search for the following in order:
```
first_package_to_search.spark__datediff
first_package_to_search.default__datediff
second_package_to_search.spark__datediff
second_package_to_search.default__datediff
dbt_utils.spark__datediff
dbt_utils.default__datediff
```

----

### Getting started with dbt

- [What is dbt]?
- Read the [dbt viewpoint]
- [Installation]
- Join the [chat][slack-url] on Slack for live questions and support.


## Code of Conduct

Everyone interacting in the dbt project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct].



[PyPA Code of Conduct]: https://www.pypa.io/en/latest/code-of-conduct/
[slack-url]: http://ac-slackin.herokuapp.com/
[Installation]: https://dbt.readme.io/docs/installation
[What is dbt]: https://dbt.readme.io/docs/overview
[dbt viewpoint]: https://dbt.readme.io/docs/viewpoint
