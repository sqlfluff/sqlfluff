# How to Troubleshoot SQLFluff

It can at times be tricky to troubleshoot SQLFluff as it exists within
an ecosystem of other tools, and can be deployed in wide range of ways.

This step by step guide can help you narrow down what's likely going wrong
and point you toward the swiftest resolution.

## 1. Common Errors

There are a few error messages you may get which have relatively
straightforward resolution paths.

### Parsing Errors

SQLFluff needs to be able to parse your SQL to understand it's structure.
That means if it fails to parse the SQL it will give you an error message.
The intent is that if SQLFluff cannot parse the SQL, then it should mean
the SQL is also invalid and help you understand where and why.

For example, this is a simple query which is not valid SQL:

```sql
select 1 2 3
from my_table
```

When running `sqlfluff lint` or `sqlfluff parse` we get the following
error message:

```
==== parsing violations ====
L:   1 | P:  10 |  PRS | Line 1, Position 10: Found unparsable section: '2 3'
```

Furthermore if we look at the full parsing output we can see an unparsable
section in the parse tree:

```log{12-15}
[L:  1, P:  1]      |file:
[L:  1, P:  1]      |    statement:
[L:  1, P:  1]      |        select_statement:
[L:  1, P:  1]      |            select_clause:
[L:  1, P:  1]      |                keyword:                                      'select'
[L:  1, P:  7]      |                [META] indent:
[L:  1, P:  7]      |                whitespace:                                   ' '
[L:  1, P:  8]      |                select_clause_element:
[L:  1, P:  8]      |                    numeric_literal:                          '1'
[L:  1, P:  9]      |                [META] dedent:
[L:  1, P:  9]      |                whitespace:                                   ' '
[L:  1, P: 10]      |                unparsable:                                   !! Expected: 'Nothing here.'
[L:  1, P: 10]      |                    numeric_literal:                          '2'
[L:  1, P: 11]      |                    whitespace:                               ' '
[L:  1, P: 12]      |                    numeric_literal:                          '3'
[L:  1, P: 13]      |            newline:                                          '\n'
[L:  2, P:  1]      |            from_clause:
[L:  2, P:  1]      |                keyword:                                      'from'
[L:  2, P:  5]      |                whitespace:                                   ' '
[L:  2, P:  6]      |                from_expression:
[L:  2, P:  6]      |                    [META] indent:
[L:  2, P:  6]      |                    from_expression_element:
[L:  2, P:  6]      |                        table_expression:
[L:  2, P:  6]      |                            table_reference:
[L:  2, P:  6]      |                                naked_identifier:             'my_table'
[L:  2, P: 14]      |                    [META] dedent:
[L:  2, P: 14]      |    newline:                                                  '\n'
[L:  3, P:  1]      |    [META] end_of_file:
```

SQLFluff maintains it's own version of each SQL dialect, and this may not be
exhaustive for some of the dialects which are newer to SQLFluff or which are
in very active development themselves. This means in some scenarios you may
find a query which runs fine in your environment, but cannot be parsed by
SQLFluff. This is not a *"bug"* per-se, but is an indicator of a gap in the
SQLFluff dialect.

Many of the issues raised on GitHub relate to parsing errors like this, but
it's also a great way to support the project if you feel able to contribute
a dialect improvement yourself. We have a short guide on
[contributing dialect changes](../development/dialect) to walk you through the process. In the
short term you can also ignore specific files from your overall project so
that this specific file doesn't become a blocker for the rest.
See [ignoring files configuration](../configuration/ignoring).

### Configuration Issues

If you're getting ether unexpected behaviour with your config, or errors
because config values haven't been set correctly, it's often due to config
file discovery (i.e. whether SQLFluff can find your config file, and what
order it's combining config files).

For a more general guide to this topic see [setting configuration](../configuration/index).

To help troubleshoot issues, if you run `sqlfluff` with a more verbose
logging setting (e.g. `sqlfluff lint /my/model.sql -v`, or `-vv`, or
`-vvvvvv`) you'll get a readout of the root config that SQLFluff is using.
This can help debug which values are being used.

## 2. Isolating SQLFluff

If you're still getting strange errors, then the next most useful thing you
can do, both to help narrow down the cause, but also to assist with fixing
a bug if you have found one, is to isolate SQLFluff from any other tools
you're using in parallel:

1. If you're using SQLFluff with the [dbt templater](../configuration/templating/dbt), then try and
   recreate the error with the [jinja templater](../configuration/templating/jinja) to remove the influence
   of `dbt` and any database connection related issues.

2. If you're getting an error in a remote CI suite (for example on GitHub
   actions, or a server like Jenkins), try and recreate the issue locally
   on your machine using the same tools.

3. If you're [using pre-commit](../usage/pre-commit), [diff-quality](../usage/diff-quality) or the
   [VSCode extension](https://github.com/sqlfluff/vscode-sqlfluff) try to recreate the issue by running the SQLFluff
   [CLI](../reference/cli/index.md) directly. Often this can make debugging significantly
   easier because some of these tools hide some of the error messages
   which SQLFluff gives the user to help debugging errors.

## 3. Minimise the Query

Often SQL scripts can get very long, and if you're getting an error on a very
long script, then it can be extremely difficult to work out what the issue is.
To assist with this we recommend iteratively cutting down the file (or
alternatively, iteratively building a file back up) until you have the smallest
file which still exhibits the issue. Often after this step, the issue can
become obvious.

1. If your file has multiple statements in it (i.e. statements separated
   by `;`), then remove ones until SQLFluff no longer shows the issue. When
   you get to that point, add the offending one back in and remove all the
   others.

2. Simplify individual statements. For example in a `SELECT` statement, if
   you suspect the issue is coming from a particular column, then remove the
   others, or remove CTEs, until you've got the simplest query which still
   shows the issue.
