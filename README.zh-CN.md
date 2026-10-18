![SQLFluff](https://raw.githubusercontent.com/sqlfluff/sqlfluff/main/images/sqlfluff-wide.png)

# 给人类用的 SQL Linter

[![PyPi Version](https://img.shields.io/pypi/v/sqlfluff.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/sqlfluff/)
[![PyPi License](https://img.shields.io/pypi/l/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Status](https://img.shields.io/pypi/status/sqlfluff.svg?style=flat-square)](https://pypi.org/project/sqlfluff/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/sqlfluff?style=flat-square)](https://pypi.org/project/sqlfluff/)

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/sqlfluff/sqlfluff/.github/workflows/ci-tests.yml?logo=github&style=flat-square)](https://github.com/sqlfluff/sqlfluff/actions/workflows/ci-tests.yml?query=branch%3Amain)
[![Documentation](https://img.shields.io/badge/docs-docs.sqlfluff.com-blue?style=flat-square)](https://docs.sqlfluff.com)
[![Linting and formatting: Ruff](https://img.shields.io/badge/linting%20%26%20formatting-ruff-D7FF64.svg?style=flat-square)](https://docs.astral.sh/ruff/)
[![Docker Pulls](https://img.shields.io/docker/pulls/sqlfluff/sqlfluff?logo=docker&style=flat-square)](https://hub.docker.com/r/sqlfluff/sqlfluff)
[![Gurubase](https://img.shields.io/badge/Gurubase-Ask%20SQLFluff%20Guru-006BFF?style=flat-square)](https://gurubase.io/g/sqlfluff)

<p align="center"><a href="./README.md"><b>English</b></a> | <b>简体中文</b></p>

**SQLFluff** 是一个方言灵活、可配置的 SQL linter。它以 [ELT](https://www.techtarget.com/searchdatamanagement/definition/Extract-Load-Transform-ELT) 应用为设计场景，同时支持 Jinja 模板和 dbt。**SQLFluff** 会自动修复大多数 linting 错误，让你把时间花在真正重要的事情上。

## 目录

1. [支持的方言](#支持的方言)
2. [支持的模板](#支持的模板)
3. [VS Code 扩展](#vs-code-扩展)
4. [快速开始](#快速开始)
5. [文档](#文档)
6. [发布](#发布)
7. [在 Slack 上加入 SQLFluff](#在-slack-上加入-sqlfluff)
8. [在 Twitter 上关注 SQLFluff](#在-twitter-上关注-sqlfluff)
9. [参与贡献](#参与贡献)
10. [赞助商](#赞助商)

## 支持的方言

尽管 SQL 的各种实现在语法和文法上大体一致，但也存在不少各有差异的方言。**SQLFluff** 目前支持以下 SQL 方言（但可能支持得并不完整）：

- ANSI SQL - 这是基础版本，有时可能并不严格遵循 ANSI/ISO SQL 的定义
- [Athena](https://aws.amazon.com/athena/)
- [BigQuery](https://cloud.google.com/bigquery/)
- [ClickHouse](https://clickhouse.com/)
- [Databricks](https://databricks.com/)（注意：它基于 `sparksql` 方言扩展了 [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html) 语法）
- [Db2](https://www.ibm.com/analytics/db2)
- [Doris](https://doris.apache.org/)
- [DuckDB](https://duckdb.org/)
- [Exasol](https://www.exasol.com/)
- [FlinkSQL](https://nightlies.apache.org/flink/flink-docs-master/)
- [Greenplum](https://greenplum.org/)
- [Hive](https://hive.apache.org/)
- [Impala](https://impala.apache.org/)
- [MariaDB](https://www.mariadb.com/)
- [Materialize](https://materialize.com/)
- [MySQL](https://www.mysql.com/)
- [Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/index.html)
- [PostgreSQL](https://www.postgresql.org/)（又名 Postgres）
- [Redshift](https://docs.aws.amazon.com/redshift/index.html)
- [Snowflake](https://www.snowflake.com/)
- [SOQL](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm)
- [SparkSQL](https://spark.apache.org/docs/latest/)
- [SQLite](https://www.sqlite.org/)
- [StarRocks](https://www.starrocks.io)
- [Teradata](https://www.teradata.com/)
- [Transact-SQL](https://docs.microsoft.com/en-us/sql/t-sql/language-reference)（又名 T-SQL）
- [Trino](https://trino.io/)
- [Vertica](https://www.vertica.com/)

我们希望让扩展这些方言的支持变得容易，也希望加入其他目前尚不支持的方言。请[提交 issue](https://github.com/sqlfluff/sqlfluff/issues)（或为已有 issue 投票）让我们知道你对缺失支持的需求。

特别欢迎了解相关缺失语法或方言的贡献者提交 pull request，这是让支持落地的最佳途径。我们乐意与任何潜在的贡献者合作，帮助他们补齐这些支持。对于任何较大的功能变更，请先提交 issue，在投入时间之前确认它适合本项目。

## 支持的模板

SQL 本身不太适合[模块化](https://docs.getdbt.com/docs/viewpoint#section-modularity)，因此为了引入一定的灵活性和可复用性，它通常会被[模板化](https://en.wikipedia.org/wiki/Template_processor)，如我们的[模块化文档](https://docs.sqlfluff.com/en/stable/perma/modularity.html)中进一步讨论的那样。

**SQLFluff** 支持以下模板：

- [Jinja](https://jinja.palletsprojects.com/)（又名 Jinja2）
- SQL 占位符（例如 SQLAlchemy 参数）
- [Python 格式字符串](https://docs.python.org/3/library/string.html#format-string-syntax)
- [dbt](https://www.getdbt.com/)（需要插件）

同样，如果你希望支持更多模板语言/语法，请提交 issue。

## VS Code 扩展

我们还有一个 VS Code 扩展：

- [GitHub 仓库](https://github.com/sqlfluff/vscode-sqlfluff)
- [VS Code 市场中的扩展](https://marketplace.visualstudio.com/items?itemName=dorzey.vscode-sqlfluff)

# 快速开始

开始使用，请安装包并运行 `sqlfluff lint` 或 `sqlfluff fix`。

```shell
$ pip install sqlfluff
$ echo "  SELECT a  +  b FROM tbl;  " > test.sql
$ sqlfluff lint test.sql --dialect ansi
== [test.sql] FAIL
L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                       | Found '  '. [layout.spacing]
L:   1 | P:   1 | LT02 | First line should not be indented.
                       | [layout.indent]
L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                       | [layout.start_of_file]
L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                       | Found '  '. [layout.spacing]
L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                       | Found '  '. [layout.spacing]
L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                       | [layout.spacing]
L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                       | [layout.end_of_file]
All Finished 📜 🎉!
```

如果你想要可选的 Rust 支持的解析器和词法分析器，请安装 `rs` extra：

```shell
$ pip install sqlfluff[rs]
```

在受支持的 CPython 3.10+ 平台上，这会安装预构建的 ABI3 wheel。如果你的平台没有发布对应的 wheel，`pip` 会退回到从源码构建 `sqlfluffrs`，这需要 Rust 工具链和可用的 C/C++ 构建环境。安装 Rust 最简单的方式是使用 [rustup](https://rustup.rs/)。

或者，你也可以使用 [**SQLFluff 官方 Docker 镜像**](https://hub.docker.com/r/sqlfluff/sqlfluff)，或在 [**SQLFluff 在线版**](https://online.sqlfluff.com/) 上把玩。

完整的 [CLI 用法](https://docs.sqlfluff.com/en/stable/perma/cli.html)和[规则参考](https://docs.sqlfluff.com/en/stable/perma/rules.html)请参阅 [SQLFluff 文档](https://docs.sqlfluff.com/en/stable/)。

# 文档

完整文档请访问 [docs.sqlfluff.com](https://docs.sqlfluff.com/en/stable/)。
本文档由本仓库生成，如有补充、更正或澄清，请提交 [issue](https://github.com/sqlfluff/sqlfluff/issues) 或 pull request。

# 发布

**SQLFluff** 遵循[语义化版本](https://semver.org/spec/v2.0.0.html)，因此破坏性变更应仅限于主版本发布。某些部分（例如 Python API）处于较不稳定的状态，可能会更频繁地出现较大变化。有关破坏性变更及如何在版本间迁移的详情，请参阅我们的[发布说明](https://docs.sqlfluff.com/en/latest/perma/releasenotes.html)。更多细节见[变更日志](CHANGELOG.md)。如果你想参与，请考虑[贡献](CONTRIBUTING.md)。

新版本每月发布一次。更多信息请访问[发布页](https://github.com/sqlfluff/sqlfluff/releases)。

# 在 Slack 上加入 SQLFluff

我们有一个快速成长的社区[在 Slack 上](https://join.slack.com/t/sqlfluff/shared_invite/zt-3qprhrisj-ClUo_1tLmYBzrVu5ZoDwIw)，快来加入我们吧！

# 在 Twitter 上关注 SQLFluff

在 Twitter 上关注 [@SQLFluff](https://twitter.com/SQLFluff)，获取公告和其他相关内容。

# 参与贡献

我们感谢所有的[贡献者](https://github.com/sqlfluff/sqlfluff/graphs/contributors)。这个项目还有很多事情要做，而我们也才刚刚起步。

如果你想更深入地了解 **SQLFluff** 的架构，可以在[这里](https://docs.sqlfluff.com/en/latest/perma/architecture.html)找到更多信息。

如果你想参与贡献，请查看 [GitHub 上未解决的 issue](https://github.com/sqlfluff/sqlfluff/issues)。你也可以参阅[贡献指南](CONTRIBUTING.md)，其中包含 pull request 的接纳原则和 AI 辅助贡献的期望。

# 赞助商

<img src="https://raw.githubusercontent.com/sqlfluff/sqlfluff/refs/heads/main/images/datacoves.png" alt="Datacoves" width="150"/><br>
开箱即用的分析技术栈，更多信息请访问 [Datacoves.com](https://datacoves.com/)。
