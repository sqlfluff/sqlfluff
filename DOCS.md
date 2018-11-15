# SqlFluff
## The SQL Linter for humans

# Documentation

## `sqlfluff version`

**Purpose:** Read out the current version information of sqlfluff.

**Usage:** `sqlfluff version [-v, --verbose]`

**Parameters:**

- `[-v, --verbose]`: Verbosity, how detailed should the output be.

**Example responses:**

> *Not verbose:*
> ```shell
> $ sqlfluff version
> 0.0.4
> ```

> *Verbose:*
> ```shell
> $ sqlfluff version -v
> sqlfluff:      0.0.4 python:        3.6.7
> ```

## `sqlfluff lint`

**Purpose:** Actually lint things.

**Usage:** `sqlfluff lint [-v, --verbose] [-n, --nocolor] [--dialect ansi]`

**Parameters:**

- `[-v, --verbose]`: Verbosity, how detailed should the output be.
- `[-n, --nocolor]`: No color - if this is set then the output will be without ANSI color codes.
- `[--dialect ansi]`: Which dialect to run sqlfluff with, defaulting to `ansi`. Options
  - `ansi` - Currently the only option - assumes that the sql is in line with [_ISO/IEC 9075_](https://en.wikipedia.org/wiki/ISO/IEC_9075)
  - ... to come `mysql`, `redshift` and potentially others...

**Example responses:**

_NB: Examples of the `--nocolor` option not shown as the textual output is the same, just with different colors_

> *Not verbose:*
> ```shell
> $ sqlfluff lint test.sql
> == [test.sql] FAIL
> L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
> L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
> L:   1 | P:  27 | L001 | Unnecessary trailing whitespace
> ```

> *Verbose (with dialect):*
> ```shell
> $ sqlfluff lint test.sql -v  --dialect ansi
> ==== sqlfluff ====
> sqlfluff:      0.0.4 python:        3.6.7
> dialect:        ansi verbosity:         1
> ==== readout ====
> === [ path: test.sql ] ===
> == [test.sql] FAIL
> L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
> L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
> L:   1 | P:  27 | L001 | Unnecessary trailing whitespace
> ==== summary ====
> violations:        3 status:         FAIL
> ```


> *Very Verbose:*
> ```shell
> $ sqlfluff lint test.sql -vv
> ==== sqlfluff ====
> sqlfluff:      0.0.4 python:        3.6.7
> dialect:        ansi verbosity:         2
> ==== readout ====
> === [ path: test.sql ] ===
> == [test.sql] FAIL
> L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
> L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
> L:   1 | P:  27 | L001 | Unnecessary trailing whitespace
> ==== summary ====
> files:             1 violations:        3
> clean files:       0 unclean files:     1
> avg per file:   3.00 status:         FAIL
> ```
