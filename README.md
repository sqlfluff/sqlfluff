![SQLFluff](https://raw.githubusercontent.com/sqlfluff/sqlfluff/master/images/sqlfluff-wide.png)

## The SQL Linter for humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Verions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/sqlfluff?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/sqlfluff/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/sqlfluff/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/sqlfluff/sqlfluff.svg?style=flat-square)](https://requires.io/github/sqlfluff/sqlfluff/requirements/?branch=master)
[![CircleCI](https://img.shields.io/circleci/build/gh/sqlfluff/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/sqlfluff/sqlfluff/tree/master)
[![ReadTheDocs](https://img.shields.io/readthedocs/sqlfluff?style=flat-square&logo=Read%20the%20Docs)](https://sqlfluff.readthedocs.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Bored of not having a good SQL linter that works with whichever dialect you're
working with? SQLFluff is an extensible and modular linter designed to help you write
good SQL and catch errors before it hits your database. SQLFluff can auto-fix most linting
errors too.

# Getting Started

To get started, install the package and run `sqlfluff lint` or `sqlfluff fix`.

```shell
$ pip install sqlfluff
$ echo "  SELECT a  +  b FROM tbl;  " > test.sql
$ sqlfluff lint test.sql
== [test.sql] FAIL
L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
L:   1 | P:  27 | L001 | Unnecessary trailing whitespace
```

You can also have a play using [SQLFluff online](https://sqlfluff-online.herokuapp.com/).

For full CLI usage and rules reference, see the docs.

# Documentation

For full documentation visit [docs.sqlfluff.com](https://docs.sqlfluff.com/en/stable/).

# Releases

> **SQLFluff** is still in an open alpha phase - expect the tool to change significantly
> over the coming months, and expect potentially non-backward compatible api changes
> to happen at any point. If you'd like to help please consider [contributing](CONTRIBUTING.md).

* **0.4.x** (ongoing development) will fully support dbt packages and macros with significant speed improvements and new rules.
* **0.3.x** dropped support for python 2.7 and 3.4, and reworked the
  handling of indentation linting in a potentially not backward compatible way.
* **0.2.x** added templating support and a big restructure of rules
  and changed how users might interact with sqlfluff on templated code.
* **0.1.x** involved a major re-write of the parser, completely changing
  the behaviour of the tool with respect to complex parsing.

# Contributing

There's lots to do in this project, and we're just getting started. If you want to understand more
about the architecture of SQLFluff, you can find [more here](https://docs.sqlfluff.com/en/latest/architecture.html).

If you'd like to contribute, check out the
[open issues on GitHub](https://github.com/sqlfluff/sqlfluff/issues).
You can also see the guide to [contributing](CONTRIBUTING.md).
