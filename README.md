![SQLFluff](https://raw.githubusercontent.com/sqlfluff/sqlfluff/main/images/sqlfluff-wide.png)

# The SQL Linter for Humans

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/sqlfluff?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![codecov](https://img.shields.io/codecov/c/gh/sqlfluff/sqlfluff.svg?style=flat-square&logo=Codecov)](https://codecov.io/gh/sqlfluff/sqlfluff)
[![Requirements Status](https://img.shields.io/requires/github/sqlfluff/sqlfluff.svg?style=flat-square)](https://requires.io/github/sqlfluff/sqlfluff/requirements/?branch=main)
[![CircleCI](https://img.shields.io/circleci/build/gh/sqlfluff/sqlfluff/master?style=flat-square&logo=CircleCI)](https://circleci.com/gh/sqlfluff/sqlfluff/tree/main)
[![ReadTheDocs](https://img.shields.io/readthedocs/sqlfluff?style=flat-square&logo=Read%20the%20Docs)](https://sqlfluff.readthedocs.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

**SQLFluff** is a dialect-flexible and configurable SQL linter. Designed with ELT applications in mind, **SQLFluff** also works with jinja templating and dbt. **SQLFluff** will auto-fix most linting errors, allowing you to focus your time on what matters.

## Dialects Supported

Although SQL is reasonable consistent in its implementations, there are a number of different dialects available with variations of syntax and grammar. **SQLFluff** currently supports the following SQL dialects (though perhaps not in full):

- ANSI SQL - this is the base version and on occasion may not strictly follow the ANSI/ISO SQL definition
- [BigQuery](https://cloud.google.com/bigquery/)
- [Exasol](https://www.exasol.com/)
- [MySQL](https://www.mysql.com/)
- [PostgreSQL](https://www.postgresql.org/) (aka Postgres)
- [Snowflake](https://www.snowflake.com/)
- [Teradata](https://www.teradata.com/)

We aim to make it easy to expand on the support of these dialects and also add other, currently unsupported, dialects. Please [raise issues](https://github.com/sqlfluff/sqlfluff/issues) (or upvote any existing issues) to let us know of demand for missing support.

Pull requests from those that know the missing syntax or dialects are especially welcomed and are the question way for you to get support added. We are happy to work with any potential contributors on this to help them add this support. Please raise an issue first for any large feature change to ensure it is a good fit for this project before spedning time on this work.

## Templates Supported

SQL itself doesn't lend itself well to [modularity](https://docs.getdbt.com/docs/viewpoint#section-modularity), so to introduce some flexibility and reusability it is often [templated](https://en.wikipedia.org/wiki/Template_processor) as discussed more in [our modularity documentation](https://docs.sqlfluff.com/en/stable/realworld.html#modularity).

**SQLFluff** supports the following templates:
- [Jinja](https://jinja.palletsprojects.com/) (aka Jinja2)
- [dbt](https://www.getdbt.com/)

Again, please raise issues if you wish to support more templating languages/syntaxes.

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

You can also have a play using [**SQLFluff online**](https://online.sqlfluff.com/).

For full [CLI usage](https://docs.sqlfluff.com/en/stable/cli.html) and [rules reference](https://docs.sqlfluff.com/en/stable/rules.html), see [the SQLFLuff docs](https://docs.sqlfluff.com/en/stable/).

# Documentation

For full documentation visit [docs.sqlfluff.com](https://docs.sqlfluff.com/en/stable/). This documentation is generated from this repository so please raise [issues](https://github.com/sqlfluff/sqlfluff/issues) or pull requests for any additions, corrections, or clarifications.

# Releases

**SQLFluff** is in beta phase - expect the tool to change significantly with potentially non-backward compatible api and configuration changes in future releases. If you'd like to join in please consider [contributing](CONTRIBUTING.md).

New releases are made monthly. For more information, visit [Releases](https://github.com/sqlfluff/sqlfluff/releases).

# SQLFluff on Slack

We have a fast-growing community [on Slack](https://join.slack.com/t/sqlfluff/shared_invite/zt-o1f4x0e8-pZzarAIlQmKj_6ZwD16w0g), come and join us!

# SQLFluff on Twitter

Follow us [on Twitter @SQLFLuff](https://twitter.com/SQLFluff) for announcements and other related posts.

# Contributing

We are grateful for all our [contributors](https://github.com/sqlfluff/sqlfluff/graphs/contributors). There's lots to do in this project, and we're just getting started.

If you want to understand more about the architecture of **SQLFluff**, you can find [more here](https://docs.sqlfluff.com/en/latest/architecture.html).

If you'd like to contribute, check out the [open issues on GitHub](https://github.com/sqlfluff/sqlfluff/issues). You can also see the guide to [contributing](CONTRIBUTING.md).
