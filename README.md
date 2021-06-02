![SQLFluff](https://raw.githubusercontent.com/sqlfluff/sqlfluff/master/images/sqlfluff-wide.png)

## The SQL Linter for humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/sqlfluff?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/sqlfluff/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/sqlfluff/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/sqlfluff/sqlfluff.svg?style=flat-square)](https://requires.io/github/sqlfluff/sqlfluff/requirements/?branch=master)
[![CircleCI](https://img.shields.io/circleci/build/gh/sqlfluff/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/sqlfluff/sqlfluff/tree/master)
[![ReadTheDocs](https://img.shields.io/readthedocs/sqlfluff?style=flat-square&logo=Read%20the%20Docs)](https://sqlfluff.readthedocs.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

SQLFluff is a dialect-flexible and configurable SQL linter. Designed with ELT applications in mind, SQLFluff also works with jinja templating and dbt. SQLFluff will auto-fix most linting errors, allowing you to focus your time on what matters.


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

You can also have a play using [SQLFluff online](https://online.sqlfluff.com/).

For full CLI usage and rules reference, see the docs.

# Documentation

For full documentation visit [docs.sqlfluff.com](https://docs.sqlfluff.com/en/stable/).

# Releases

**SQLFluff** is in beta phase - expect the tool to change significantly with potentially non-backward compatible api and configuration changes in future releases. If you'd like to join in please consider [contributing](CONTRIBUTING.md).

New releases are made monthly. For more information, visit [Releases](https://github.com/sqlfluff/sqlfluff/releases).

# SQLFluff on Slack

We have a fast-growing community on Slack, come and join us!

https://join.slack.com/t/sqlfluff/shared_invite/zt-o1f4x0e8-pZzarAIlQmKj_6ZwD16w0g

# Contributing

There's lots to do in this project, and we're just getting started. If you want to understand more
about the architecture of SQLFluff, you can find [more here](https://docs.sqlfluff.com/en/latest/architecture.html).

If you'd like to contribute, check out the
[open issues on GitHub](https://github.com/sqlfluff/sqlfluff/issues).
You can also see the guide to [contributing](CONTRIBUTING.md).
