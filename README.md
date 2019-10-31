# SqlFluff :scroll: :black_nib: :sparkles:
## The SQL Linter for humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Verions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/alanmcruickshank/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/alanmcruickshank/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/alanmcruickshank/sqlfluff.svg?style=flat-square)](https://requires.io/github/alanmcruickshank/sqlfluff/requirements/?branch=master)
[![CircleCI](https://img.shields.io/circleci/build/gh/alanmcruickshank/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/alanmcruickshank/sqlfluff/tree/master)

Bored of not having a good SQL linter that works with whichever dialiect you're
working with? Fluff is an extensible and modular linter designed to help you write
good SQL and catch errors and bad SQL before it hits your database.

> **Sqlfluff** is still in an open alpha phase - expect the tool to change significantly
> over the coming months, and expect potentially non-backward compatable api changes
> to happen at any point. In particular moving from 0.0.x to 0.1.x introduced some
> non backward compatible changes and potential loss in functionality. If you'd like to
> help please consider [contributing](CONTRIBUTING.md).

# Getting Started

To get started just install the package, make a sql file and then run sqlfluff and point it at the file.

```shell
$ pip install sqlfluff
$ echo "  SELECT a  +  b FROM tbl;  " > test.sql
$ sqlfluff lint test.sql
== [test.sql] FAIL
L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
L:   1 | P:  27 | L001 | Unnecessary trailing whitespace
```

# Usage

For more details on usage see the docs on github [here](DOCS.md).

# Progress

There's lots to do in this project, and we're just getting started. __NB: This list__
__has started again from the top due to the re-write__. If you want to understand more
about the architecture of sqlfluff, you can find [more here](ARCHITECTURE.md).

- [x] Command line interface
  - [x] Basic linting, both of paths and files
  - [x] Version information
  - [x] Nicely formatted readout of linting success or fail
  - [x] Exit codes which reflect linting success or fail
  - [x] Filtering to particular codes in the linting step
  - [x] Allow basic correction of some linting codes
- [x] Basic ANSI linting
  - [x] Simple whitespace testing
  - [x] Whitespace around operators
  - [x] Indentation (size and mix of tabs and spaces)
  - [ ] Indentation between lines and when to indent
  - [ ] Number of blank lines
  - [ ] Indentation of comments
  - [ ] Inconsistent capitalisation of keywords
  - [ ] Inconsistent capitalisation of unquoted identifiers
  - [ ] _(idea)_ Implement a context manager in the parse and match
    functions to avoid passing around so many variables.
- [ ] Configurable linting
  - [ ] Command line options for config
  - [ ] Ability to read from config files
  - [ ] Ability to read config from block comment
    sections in `.sql` files.
  - [x] Ignore particular rules (blacklisting)
  - [ ] Specifying particlar dialects to use
  - [ ] Preconfiguring verbosity
- [x] Dialects
  - [ ] ANSI
    - [ ] Implement singleton matching for `::`, `:` and `||`.
    - [ ] Bring in a much wider selection of test queries to identify
      next gaps.
    - [ ] Flesh out function coverage.
  - [ ] MySQL 
  - [ ] Redshift
  - [ ] Snowflake
  - [ ] Detecting dialect from a config file of some kind
  - [ ] jinja2 compatible linting (for dbt)
- [ ] Documentation
  - [x] Basic architectural principles
  - [ ] Update CLI docs to match current state
