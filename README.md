# SqlFluff :scroll: :black_nib: :sparkles:
## The SQL Linter for humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Verions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/alanmcruickshank/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/alanmcruickshank/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/alanmcruickshank/sqlfluff.svg?style=flat-square)](https://requires.io/github/alanmcruickshank/sqlfluff/requirements/?branch=master)
[![CircleCI](https://img.shields.io/circleci/build/gh/alanmcruickshank/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/alanmcruickshank/sqlfluff/tree/master)

> ## *NOTE:* sqlfluff is currently undergoing a major re-write to the parser, and so is not currently accepting pull requests.

Bored of not having a good SQL linter that works with whichever dialiect you're
working with? Fluff is an extensible and modular linter designed to help you write
good SQL and catch errors and bad SQL before it hits your database.

> **Sqlfluff** is still in an open alpha phase - expect the tool to change significantly
> over the coming months, and expect potentially non-backward compatable api changes
> to happen at any point.

> **Sqlfluff** has had a big rearchitecture to it's parsing engine. To read more about
> that then you can find details [here](https://github.com/alanmcruickshank/sqlfluff/blob/master/ARCHITECTURE.md).

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

For more details on usage see the docs on github [here](https://github.com/alanmcruickshank/sqlfluff/blob/master/DOCS.md).

# Progress

There's lots to do in this project, and we're just getting started. __NB: This list__
__has started again from the top due to the re-write__.

- [x] Command line interface
  - [x] Basic linting, both of paths and files
  - [ ] Version information
  - [ ] Nicely formatted readout of linting success or fail
  - [ ] Exist codes which reflect linting success or fail
  - [ ] Filtering to particular codes in the linting step
  - [ ] Allow basic correction of some linting codes
- [ ] Basic ANSI linting
  - [ ] Simple whitespace testing
  - [ ] Whitespace around operators
  - [ ] Indentation (size and mix of tabs and spaces)
  - [ ] Indentation between lines and when to indent
  - [ ] Number of blank lines
  - [ ] Indentation of comments
- [ ] Configurable linting
  - [ ] Command line options for config
  - [ ] Ability to read from config files
  - [ ] Ignore particular rules
  - [ ] Specifying particlar dialects to use
  - [ ] Preconfiguring verbosity
- [ ] Dialects
  - [ ] MySQL 
  - [ ] Redshift
  - [ ] Snowflake
  - [ ] Detecting dialect from a config file of some kind
  - [ ] jinja2 compatible linting (for dbt)
