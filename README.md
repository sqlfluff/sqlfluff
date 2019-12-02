# SqlFluff :scroll: :black_nib: :sparkles:
## The SQL Linter for humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Verions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/alanmcruickshank/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/alanmcruickshank/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/alanmcruickshank/sqlfluff.svg?style=flat-square)](https://requires.io/github/alanmcruickshank/sqlfluff/requirements/?branch=master)
[![CircleCI](https://img.shields.io/circleci/build/gh/alanmcruickshank/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/alanmcruickshank/sqlfluff/tree/master)
[![ReadTheDocs](https://img.shields.io/readthedocs/sqlfluff?style=flat-square&logo=Read%20the%20Docs)](https://sqlfluff.readthedocs.io)

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

For more details on usage see the docs on readthedocs [here](http://sqlfluff.readthedocs.io).

# Progress

There's lots to do in this project, and we're just getting started. If you want to understand more
about the architecture of sqlfluff, you can find [more here](https://sqlfluff.readthedocs.io/en/latest/architecture.html).

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
  - [x] Inconsistent capitalisation of keywords
  - [x] Inconsistent capitalisation of unquoted identifiers
  - [x] Implement a context manager in the parse and match
        functions to avoid passing around so many variables.
  - [x] Reenable disabled linter tests
- [x] Configurable linting
  - [x] Command line options for config
    - [x] Rough parity between command line and file based config
  - [x] Ability to read from config files
    - [x] Documentation of the config loading system
  - [ ] Ability to read config from block comment
        sections in `.sql` files.
  - [x] Ignore particular rules (blacklisting)
  - [x] Specifying particlar dialects to use
  - [x] Specifying particlar templaters to use
  - [x] Preconfiguring verbosity
  - [ ] Delta-configs for individual files printed before each above some
        level of verbosity.
  - [x] Work out a solution to templating *macros*.
  - [x] Allow configuration for *rules*, e.g. indentation multiplier for
        L003 or the capitalisation for the keyword rule.
- [x] Dialects
  - [ ] ANSI
    - [ ] Implement singleton matching for `::`, `:` and `||`.
    - [ ] Bring in a much wider selection of test queries to identify
          next gaps.
    - [x] Flesh out function coverage.
  - [ ] MySQL 
  - [ ] Redshift
  - [ ] Snowflake
  - [x] Detecting dialect from a config file of some kind
  - [x] jinja2 compatible linting (for dbt)
    - [x] a preconfigured default set of templating macros for dbt use which can be loaded
          as config.
  - [x] Move the configuration of the *lexer* into the dialect.
- [ ] Documentation
  - [x] Basic architectural principles
  - [ ] Update CLI docs to match current state
  - [x] Auto-document Rules
  - [ ] Auto-document Grammars
  - [ ] Auto-document Templaters
  - [ ] Auto-docuemnt Dialects
