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
[![DeepSource](https://img.shields.io/static/v1?label=DeepSource&message=on&color=green&style=flat-square)](https://deepsource.io/gh/alanmcruickshank/sqlfluff/)

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

# Roadmap

There's lots to do in this project, and we're just getting started. If you want to understand more
about the architecture of sqlfluff, you can find [more here](https://sqlfluff.readthedocs.io/en/latest/architecture.html).

If you'd like to contribute, check out the
[open issues on github](https://github.com/alanmcruickshank/sqlfluff/issues).
You can also see the guide to [contributing](CONTRIBUTING.md).
