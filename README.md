# SqlFluff
## The SQL Linter for humans

[![image](https://img.shields.io/pypi/v/sqlfluff.svg)](https://pypi.org/project/sqlfluff/)
[![image](https://img.shields.io/pypi/l/sqlfluff.svg)](https://pypi.org/project/sqlfluff/)
[![image](https://img.shields.io/pypi/pyversions/sqlfluff.svg)](https://pypi.org/project/sqlfluff/)
[![codecov](https://codecov.io/gh/alanmcruickshank/sqlfluff/branch/master/graph/badge.svg)](https://codecov.io/gh/alanmcruickshank/sqlfluff)
[![CircleCI](https://circleci.com/gh/alanmcruickshank/sqlfluff/tree/master.svg?style=svg)](https://circleci.com/gh/alanmcruickshank/sqlfluff/tree/master)


Bored of not having a good SQL linter that works with whichever dialiect you're
working with? Fluff is an extensible and modular linter designed to help you write
good SQL and catch errors and bad SQL before it hits your database.

# Getting Started

To get started just install the package and run it in your path of choice

```shell
$ pip install sqlfluff
$ sqlfluff lint
== [/path/you/ran/sqlfluff/in/query.sql] FAIL
L:   2 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
```

# TODO

There's lots to do in this project, and we're just getting started. Things 
still to do:

- Basic ANSI linting
- MySQL 
- Redshift
- Detecting dialect from a config file of some kind
