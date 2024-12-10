# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Note: Changes are now automatically tracked in [GitHub](https://github.com/sqlfluff/sqlfluff/releases) and will be copied in here on each release (please remember to update the issues and contributors to links!). There is no need to manually edit this file going forward.
-->
<!--Start Of Releases (DO NOT DELETE THIS LINE)-->

## [3.3.0] - 2024-12-10

## Highlights

This release brings a few more significant changes. Especially given the introduction
of several new rules, we highly recommend testing this release on your project before
upgrading to make sure they are configured appropriately for your project style guide.
As always, we have tried to make sure that the defaults for all new rules are both
widely applicable, and fairly light touch. While all have been tested on some existing
larger codebases which the maintainers have access to - do still report any bugs you
might find on GitHub in the usual manner.

* We've dropped the `appdirs` package as a dependency (as an abandoned project)
  and instead added `platformdirs` instead. Users should not notice any functionality
  changes beyond the different dependency.
* *TWO* new dialects: _Impala_ and _StarRocks_.
* *FIVE* new rules:
  * `AM08` (`ambiguous.join_condition`), which detects `JOIN` clauses without
    conditions (i.e. without an `ON` or `USING` clause). These are often typos
    and can result in significant row count increases if unintended.
  * `CV12` (`convention.join_condition`), which is related to `AM08` and detects
    cases where users have used a `WHERE` clause instead of a `JOIN ... ON ...`
    clause to do their join conditions. The join condition is a form of metadata
    and should communicate to the end user how the table should be joined. By
    mixing this information into the `WHERE` clause it makes the SQL harder to
    understand.
  * `LT14` (`layout.keyword_newline`), which allows certain keywords to trigger
    line breaks in queries. Primarily this forces the main `SELECT` statement
    clauses like `WHERE`, `GROUP BY` etc. onto new lines. This rule has been
    designed to be highly configurable, but with sensible light-touch defaults.
    Check out the docs to adapt it to the conventions of your project.
  * `ST10` (`structure.constant_expression`), some SQL users include redundant
    expressions in their code (e.g. `WHERE tbl.col = tbl.col`). These conditions
    always evaluate to a constant outcome (i.e. always evaluate as `TRUE` or
    `FALSE`) as so add no functionality or meaning to the query. This rule catches
    them.
  * `ST11` (`structure.unused_join`), which detects unused joins in SQL statements,
    and is designed to catch tables that were once used, but where the column
    references have since been removed and now the table is unnecessary.

Beyond these changes, we've seen a whole host of dialect improvements to almost
*all* of the supported dialects and several bugfixes which are combined into this
release.

We also welcome **TWELVE** new contributors to the project in this release. Thanks
to all of them for their hard work 🚀🏆🚀.

## What’s Changed

* New Rule LT14: Keyword line positioning [#6213](https://github.com/sqlfluff/sqlfluff/pull/6213) [@keraion](https://github.com/keraion)
* New Rule ST11: Detect unused tables in join [#5266](https://github.com/sqlfluff/sqlfluff/pull/5266) [@danparizher](https://github.com/danparizher)
* Snowflake Create Table allow inline foreign key with on delete … [#6486](https://github.com/sqlfluff/sqlfluff/pull/6486) [@WobblyRobbly](https://github.com/WobblyRobbly)
* Fix minor linting error in CI [#6483](https://github.com/sqlfluff/sqlfluff/pull/6483) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: alter table on delete and update support [#6473](https://github.com/sqlfluff/sqlfluff/pull/6473) [@WobblyRobbly](https://github.com/WobblyRobbly)
* New Rules AM08 + CV12: Detect implicit cross joins [#6239](https://github.com/sqlfluff/sqlfluff/pull/6239) [@rogalski](https://github.com/rogalski)
* New Rule ST10: const expression checker [#6392](https://github.com/sqlfluff/sqlfluff/pull/6392) [@rogalski](https://github.com/rogalski)
* DuckDB: Support MAP data type [#6478](https://github.com/sqlfluff/sqlfluff/pull/6478) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Hive: Add 'ALTER VIEW' query grammar [#6479](https://github.com/sqlfluff/sqlfluff/pull/6479) [@mrebaker](https://github.com/mrebaker)
* Standardise json operator spacing between dialects [#6447](https://github.com/sqlfluff/sqlfluff/pull/6447) [@WittierDinosaur](https://github.com/WittierDinosaur)
* fixes #6463: Set Variable Parsing for SparkSQL and Databricks [#6464](https://github.com/sqlfluff/sqlfluff/pull/6464) [@fstg1992](https://github.com/fstg1992)
* Teradata: support REPLACE VIEW and LOCKING ... FOR ... syntax [#6467](https://github.com/sqlfluff/sqlfluff/pull/6467) [@V-D-L-P](https://github.com/V-D-L-P)
* Rule names in warnings logic [#6459](https://github.com/sqlfluff/sqlfluff/pull/6459) [@LuigiCerone](https://github.com/LuigiCerone)
* Bigquery: Support column level key definitions [#6465](https://github.com/sqlfluff/sqlfluff/pull/6465) [@keraion](https://github.com/keraion)
* Add Implicit Indents to Qualify [#6438](https://github.com/sqlfluff/sqlfluff/pull/6438) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Fix Select statement ordering [#6446](https://github.com/sqlfluff/sqlfluff/pull/6446) [@WittierDinosaur](https://github.com/WittierDinosaur)
* fixes #6457: databricks dialect alter table foo drop column bar [#6461](https://github.com/sqlfluff/sqlfluff/pull/6461) [@fstg1992](https://github.com/fstg1992)
* Switch from `appdirs` to `platformdirs` [#6399](https://github.com/sqlfluff/sqlfluff/pull/6399) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Impala: support CREATE TABLE AS SELECT [#6458](https://github.com/sqlfluff/sqlfluff/pull/6458) [@mrebaker](https://github.com/mrebaker)
* Databricks Dialect: Backticked function identifiers now parsable [#6453](https://github.com/sqlfluff/sqlfluff/pull/6453) [@fstg1992](https://github.com/fstg1992)
* Issue #6417: Leading -- MAGIC Cells don't break parsing of notebooks [#6454](https://github.com/sqlfluff/sqlfluff/pull/6454) [@fstg1992](https://github.com/fstg1992)
* Add "target_path" configuration to the dbt templater [#6423](https://github.com/sqlfluff/sqlfluff/pull/6423) [@wircho](https://github.com/wircho)
* Sparksql: Fix ordering of create table options [#6441](https://github.com/sqlfluff/sqlfluff/pull/6441) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Dialect: Impala [#6445](https://github.com/sqlfluff/sqlfluff/pull/6445) [@mrebaker](https://github.com/mrebaker)
* RF02: Allows for lambda functions in Databricks [#6444](https://github.com/sqlfluff/sqlfluff/pull/6444) [@keraion](https://github.com/keraion)
* SQLite: Support any order of VARYING/NATIVE in CHAR types [#6443](https://github.com/sqlfluff/sqlfluff/pull/6443) [@keraion](https://github.com/keraion)
* Snowflake: Allow literals in match_by_column_name [#6442](https://github.com/sqlfluff/sqlfluff/pull/6442) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Trino: Remove TemporaryTransientGrammar [#6440](https://github.com/sqlfluff/sqlfluff/pull/6440) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Mysql: Fix parsing of system variables [#6439](https://github.com/sqlfluff/sqlfluff/pull/6439) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Sparksql: Fix hint function for proper spacing [#6437](https://github.com/sqlfluff/sqlfluff/pull/6437) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Support ORDER BY boolean [#6435](https://github.com/sqlfluff/sqlfluff/pull/6435) [@WittierDinosaur](https://github.com/WittierDinosaur)
* TSQL: allow `NEXT VALUE FOR` use as expression [#6431](https://github.com/sqlfluff/sqlfluff/pull/6431) [@timz-st](https://github.com/timz-st)
* Prework for introducing mypyc [#6433](https://github.com/sqlfluff/sqlfluff/pull/6433) [@rogalski](https://github.com/rogalski)
* Fix pre-commit on main branch [#6432](https://github.com/sqlfluff/sqlfluff/pull/6432) [@rogalski](https://github.com/rogalski)
* Initial support for Starrocks dialect [#6415](https://github.com/sqlfluff/sqlfluff/pull/6415) [@maver1ck](https://github.com/maver1ck)
* Databricks: Parse Table Valued Functions [#6417](https://github.com/sqlfluff/sqlfluff/pull/6417) [@fstg1992](https://github.com/fstg1992)
* Snowflake: Support `PARTITION_TYPE` for `CREATE EXTERNAL TABLE` [#6422](https://github.com/sqlfluff/sqlfluff/pull/6422) [@ninazacharia-toast](https://github.com/ninazacharia-toast)
* Fix docs for CP04 config and add test cases [#6416](https://github.com/sqlfluff/sqlfluff/pull/6416) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix: Parse violations not being shown when run `fix` command with `--show-lint-violations` [#6382](https://github.com/sqlfluff/sqlfluff/pull/6382) [@joaopamaral](https://github.com/joaopamaral)
* RF01: refine support for dialects with dot access syntax [#6400](https://github.com/sqlfluff/sqlfluff/pull/6400) [@rogalski](https://github.com/rogalski)
* Add new `TYPE` property to Snowflake users [#6411](https://github.com/sqlfluff/sqlfluff/pull/6411) [@mroy-seedbox](https://github.com/mroy-seedbox)
* Document the config API [#6384](https://github.com/sqlfluff/sqlfluff/pull/6384) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Error handling for trying to render callable builtins #5463 [#6388](https://github.com/sqlfluff/sqlfluff/pull/6388) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SQLite : Add `CREATE VIRTUAL TABLE`  Statement [#6406](https://github.com/sqlfluff/sqlfluff/pull/6406) [@R3gardless](https://github.com/R3gardless)
* Updated README with Table Of Contents [#6407](https://github.com/sqlfluff/sqlfluff/pull/6407) [@27Jashshah](https://github.com/27Jashshah)


## New Contributors
* [@27Jashshah](https://github.com/27Jashshah) made their first contribution in [#6407](https://github.com/sqlfluff/sqlfluff/pull/6407)
* [@joaopamaral](https://github.com/joaopamaral) made their first contribution in [#6382](https://github.com/sqlfluff/sqlfluff/pull/6382)
* [@ninazacharia-toast](https://github.com/ninazacharia-toast) made their first contribution in [#6422](https://github.com/sqlfluff/sqlfluff/pull/6422)
* [@fstg1992](https://github.com/fstg1992) made their first contribution in [#6417](https://github.com/sqlfluff/sqlfluff/pull/6417)
* [@maver1ck](https://github.com/maver1ck) made their first contribution in [#6415](https://github.com/sqlfluff/sqlfluff/pull/6415)
* [@timz-st](https://github.com/timz-st) made their first contribution in [#6431](https://github.com/sqlfluff/sqlfluff/pull/6431)
* [@mrebaker](https://github.com/mrebaker) made their first contribution in [#6445](https://github.com/sqlfluff/sqlfluff/pull/6445)
* [@wircho](https://github.com/wircho) made their first contribution in [#6423](https://github.com/sqlfluff/sqlfluff/pull/6423)
* [@LuigiCerone](https://github.com/LuigiCerone) made their first contribution in [#6459](https://github.com/sqlfluff/sqlfluff/pull/6459)
* [@V-D-L-P](https://github.com/V-D-L-P) made their first contribution in [#6467](https://github.com/sqlfluff/sqlfluff/pull/6467)
* [@WobblyRobbly](https://github.com/WobblyRobbly) made their first contribution in [#6473](https://github.com/sqlfluff/sqlfluff/pull/6473)
* [@danparizher](https://github.com/danparizher) made their first contribution in [#5266](https://github.com/sqlfluff/sqlfluff/pull/5266)

## [3.2.5] - 2024-10-25

## Highlights

This release is mostly bugfixes and dialect improvements. Notably:

* Whitespace handling improvements to `LT01` & `LT02`.
* Better error messages around trying to iterate on missing jinja variables.
* Better case sensitivity for `AL09`.
* Improved handling of jinja context in inline config directives.
* Enabling `AM02` for Trino and Snowflake.
* Handling potential collisions between `ST02` & `LT01`.
* Preventing false positives in AL05 with arrays.

There's also a bunch of documentation improvements in this release, including
guides on how to troubleshoot SQLFluff and how to write custom rules. Check
out https://docs.sqlfluff.com for more details.

We also saw **five** new contributors to the project this month. Welcome to
the project, and thanks for taking the time to contribute! 🎉🏆🎉

## What’s Changed

* Guides for custom rules and for troubleshooting [#6379](https://github.com/sqlfluff/sqlfluff/pull/6379) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Documentation and small overhaul of parametrized rule test cases [#6380](https://github.com/sqlfluff/sqlfluff/pull/6380) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: add missing unreserved keyword NULLS (#5212) [#6390](https://github.com/sqlfluff/sqlfluff/pull/6390) [@simonhoerdumbonde](https://github.com/simonhoerdumbonde)
* Introducing SQLFluff Guru on Gurubase.io [#6373](https://github.com/sqlfluff/sqlfluff/pull/6373) [@kursataktas](https://github.com/kursataktas)
* Improve heuristics for inline config [#6391](https://github.com/sqlfluff/sqlfluff/pull/6391) [@rogalski](https://github.com/rogalski)
* Postgres: Handle expressions that occur in `IN` functions [#6393](https://github.com/sqlfluff/sqlfluff/pull/6393) [@keraion](https://github.com/keraion)
* Snowflake: Support bracketed lambda functions without datatypes [#6394](https://github.com/sqlfluff/sqlfluff/pull/6394) [@keraion](https://github.com/keraion)
* LT01: Add default config for `match_condition` to touch [#6395](https://github.com/sqlfluff/sqlfluff/pull/6395) [@keraion](https://github.com/keraion)
* Snowflake: Allow for additional `CONNECT BY` expressions that may use `PRIOR` [#6396](https://github.com/sqlfluff/sqlfluff/pull/6396) [@keraion](https://github.com/keraion)
* Details on debugging and setup for diff-quality [#6381](https://github.com/sqlfluff/sqlfluff/pull/6381) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix edge case in Jinja reindents [#6383](https://github.com/sqlfluff/sqlfluff/pull/6383) [@rogalski](https://github.com/rogalski)
* Support identifier clause for Databricks [#6377](https://github.com/sqlfluff/sqlfluff/pull/6377) [@PaulBurridge](https://github.com/PaulBurridge)
* Enable AM02 for snowflake and trino by default. [#6369](https://github.com/sqlfluff/sqlfluff/pull/6369) [@mchen-codaio](https://github.com/mchen-codaio)
* Postgres: Support identifiers in `ALTER DATABASE SET` [#6376](https://github.com/sqlfluff/sqlfluff/pull/6376) [@keraion](https://github.com/keraion)
* SparkSQL: Improved lexing and parsing of file literals [#6375](https://github.com/sqlfluff/sqlfluff/pull/6375) [@keraion](https://github.com/keraion)
* Fix Snowflake alter share [#6372](https://github.com/sqlfluff/sqlfluff/pull/6372) [@greg-finley](https://github.com/greg-finley)
* Resolve collision between ST02 and LT01 [#6366](https://github.com/sqlfluff/sqlfluff/pull/6366) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prevent false positives with AL05 and array functions [#6365](https://github.com/sqlfluff/sqlfluff/pull/6365) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle iteration and getting undefined jinja variables [#6364](https://github.com/sqlfluff/sqlfluff/pull/6364) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update documentation with new dialects [#6337](https://github.com/sqlfluff/sqlfluff/pull/6337) [@mchen-codaio](https://github.com/mchen-codaio)
* enable default values when creating databricks tables [#6362](https://github.com/sqlfluff/sqlfluff/pull/6362) [@VictorAtIfInsurance](https://github.com/VictorAtIfInsurance)
* Postgres :  Add `ALTER AGGREGATE` Statement [#6353](https://github.com/sqlfluff/sqlfluff/pull/6353) [@R3gardless](https://github.com/R3gardless)
* Revise AL09 (self aliasing) - stricter case sensitivity [#6333](https://github.com/sqlfluff/sqlfluff/pull/6333) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Make dbt `RelationEmulator` safely callable [#6358](https://github.com/sqlfluff/sqlfluff/pull/6358) [@mroy-seedbox](https://github.com/mroy-seedbox)

## New Contributors

* [@VictorAtIfInsurance](https://github.com/VictorAtIfInsurance) made their first contribution in [#6362](https://github.com/sqlfluff/sqlfluff/pull/6362)
* [@mchen-codaio](https://github.com/mchen-codaio) made their first contribution in [#6337](https://github.com/sqlfluff/sqlfluff/pull/6337)
* [@PaulBurridge](https://github.com/PaulBurridge) made their first contribution in [#6377](https://github.com/sqlfluff/sqlfluff/pull/6377)
* [@kursataktas](https://github.com/kursataktas) made their first contribution in [#6373](https://github.com/sqlfluff/sqlfluff/pull/6373)
* [@simonhoerdumbonde](https://github.com/simonhoerdumbonde) made their first contribution in [#6390](https://github.com/sqlfluff/sqlfluff/pull/6390)

## [3.2.4] - 2024-10-14

## Highlights

This release is almost all dialect fixes and bugfixes. Notably also, this
release brings official python 3.13 support too (although most users should
not realise any differences).

We also saw **two** new contributors to the project. Welcome
[@R3gardless](https://github.com/R3gardless)
& [@brandonschabell](https://github.com/brandonschabell)! 🎉🎉🎉

## What’s Changed

* Utilize a deepcopy of the config object when parsing files [#6344](https://github.com/sqlfluff/sqlfluff/pull/6344) [@brandonschabell](https://github.com/brandonschabell)
* Snowflake supports other literals in system functions [#6355](https://github.com/sqlfluff/sqlfluff/pull/6355) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Un-reserve CURRENT_USER [#6354](https://github.com/sqlfluff/sqlfluff/pull/6354) [@alanmcruickshank](https://github.com/alanmcruickshank)
* tsql: handle additional primary/foreign key options in constraints [#6347](https://github.com/sqlfluff/sqlfluff/pull/6347) [@keraion](https://github.com/keraion)
* Add `DROP COLUMN` support for multiple dialects [#6348](https://github.com/sqlfluff/sqlfluff/pull/6348) [@keraion](https://github.com/keraion)
* TSQL: allow `UPDATE` to be a function name [#6349](https://github.com/sqlfluff/sqlfluff/pull/6349) [@keraion](https://github.com/keraion)
* tsql: allow both on delete and on update in a `reference_constraint` [#6346](https://github.com/sqlfluff/sqlfluff/pull/6346) [@keraion](https://github.com/keraion)
* Postgres : Allow Extensions with Special Characters in Name [#6345](https://github.com/sqlfluff/sqlfluff/pull/6345) [@R3gardless](https://github.com/R3gardless)
* Fix `tox` command in test/fixtures/dialects/README.md [#6342](https://github.com/sqlfluff/sqlfluff/pull/6342) [@R3gardless](https://github.com/R3gardless)
* Revise dbt warnings when a file fails to compile [#6338](https://github.com/sqlfluff/sqlfluff/pull/6338) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Add `CREATE FOREIGN DATA WRAPPER` statement [#6335](https://github.com/sqlfluff/sqlfluff/pull/6335) [@keraion](https://github.com/keraion)
* Trino: Add some support to `json_query` functions [#6336](https://github.com/sqlfluff/sqlfluff/pull/6336) [@keraion](https://github.com/keraion)
* Handle deprecation warning of "fork" [#6332](https://github.com/sqlfluff/sqlfluff/pull/6332) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Python 3.13 support and make it default for test coverage [#6269](https://github.com/sqlfluff/sqlfluff/pull/6269) [@alanmcruickshank](https://github.com/alanmcruickshank)
* ST06 - Fix union of CTE/Subquery [#6298](https://github.com/sqlfluff/sqlfluff/pull/6298) [@rogalski](https://github.com/rogalski)
* Refactor timestamp grammar [#6331](https://github.com/sqlfluff/sqlfluff/pull/6331) [@greg-finley](https://github.com/greg-finley)

## New Contributors

* [@R3gardless](https://github.com/R3gardless) made their first contribution in [#6342](https://github.com/sqlfluff/sqlfluff/pull/6342)
* [@brandonschabell](https://github.com/brandonschabell) made their first contribution in [#6344](https://github.com/sqlfluff/sqlfluff/pull/6344)

## [3.2.3] - 2024-10-10

## Highlights

This is another release of dialect improvements and rule bugfixes. Notably:

* More robust algorithms for the indentation of Jinja template tags in `LT02`.
* The `github-annotation-native` format option now has _groups_ for each filename.

There's also a refactor of where we guides and howtos in the docs. Keep an eye
on that section going forward for more information about best practice and
troubleshooting for SQLFluff.

Even in this small PR, we've seen **two** new contributors. Welcome
[@nspcc-cm](https://github.com/nspcc-cm) & [@rogalski](https://github.com/rogalski)
to the project!

## What’s Changed

* BigQuery: Support Tuple syntax in other locations [#6328](https://github.com/sqlfluff/sqlfluff/pull/6328) [@keraion](https://github.com/keraion)
* Trino: Fix rule interactions with lambda functions [#6327](https://github.com/sqlfluff/sqlfluff/pull/6327) [@keraion](https://github.com/keraion)
* Resolve some more edge cases in LT02 [#6324](https://github.com/sqlfluff/sqlfluff/pull/6324) [@alanmcruickshank](https://github.com/alanmcruickshank)
* RF05 - fine tuning for snowflake dialect [#6297](https://github.com/sqlfluff/sqlfluff/pull/6297) [@rogalski](https://github.com/rogalski)
* Indentation: `UPDATE` and `RETURNING` clauses [#6314](https://github.com/sqlfluff/sqlfluff/pull/6314) [@keraion](https://github.com/keraion)
* Postgres: Fix lexing some JSON operators [#6323](https://github.com/sqlfluff/sqlfluff/pull/6323) [@keraion](https://github.com/keraion)
* Add support for `grant monitor on user ...` in Snowflake dialect [#6322](https://github.com/sqlfluff/sqlfluff/pull/6322) [@mroy-seedbox](https://github.com/mroy-seedbox)
* Exclude templated casts from CV11 [#6320](https://github.com/sqlfluff/sqlfluff/pull/6320) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake allow double-quoted comments [#6318](https://github.com/sqlfluff/sqlfluff/pull/6318) [@greg-finley](https://github.com/greg-finley)
* Databricks materialized view [#6319](https://github.com/sqlfluff/sqlfluff/pull/6319) [@greg-finley](https://github.com/greg-finley)
* Allow double quotes to be escaped by writing twice [#6316](https://github.com/sqlfluff/sqlfluff/pull/6316) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve an oscillation bug with LT02 [#6306](https://github.com/sqlfluff/sqlfluff/pull/6306) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Create a "Guides and Howtos" section of the docs. [#6301](https://github.com/sqlfluff/sqlfluff/pull/6301) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add groups to the `github-annotation-native` format option. [#6312](https://github.com/sqlfluff/sqlfluff/pull/6312) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Support CTEs and multiple orders of CopyOptions in COPY INTO [#6313](https://github.com/sqlfluff/sqlfluff/pull/6313) [@keraion](https://github.com/keraion)
* Allow expressions in ORDER BY for clickhouse [#6311](https://github.com/sqlfluff/sqlfluff/pull/6311) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: support temp UDFs [#6309](https://github.com/sqlfluff/sqlfluff/pull/6309) [@rogalski](https://github.com/rogalski)
* fix: tsql create function syntax corrections [#6289](https://github.com/sqlfluff/sqlfluff/pull/6289) [@nspcc-cm](https://github.com/nspcc-cm)

## New Contributors

* [@nspcc-cm](https://github.com/nspcc-cm) made their first contribution in [#6289](https://github.com/sqlfluff/sqlfluff/pull/6289)
* [@rogalski](https://github.com/rogalski) made their first contribution in [#6309](https://github.com/sqlfluff/sqlfluff/pull/6309)

## [3.2.2] - 2024-10-07

## Highlights

This is a hotfix release to resolve an issue with the JJ01 rule when running
in parallel mode.

## What’s Changed

* Hotfix for JJ01 [#6304](https://github.com/sqlfluff/sqlfluff/pull/6304) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add note on 3.0.x to main docs page. [#6302](https://github.com/sqlfluff/sqlfluff/pull/6302) [@alanmcruickshank](https://github.com/alanmcruickshank)

## [3.2.1] - 2024-10-06

## Highlights

This release is primarily housekeeping, bugfixes and dialect improvements.
More specifically:

* Resolving regressions regressions in `JJ01`, filename extension handling
  and the treatment of unfixable/unparsable files, which have been noticed
  with recent releases.
* Resolving bugs in `LT07` & `LT12` which relate to jinja whitespace control.
* More robust support for arbitrary methods on the `ref` and `source` macros
  for the dbt templater.

There's also dialect improvements for BigQuery, TSQL, MySQL, MariaDB,
Snowflake, DuckDB, Databricks, Postgres, Teradata, Exasol & Vertica.

We also saw **six** new contributors merge their first pull request as part
of this release. Welcome to the project! 🎉🏆🎉

## What’s Changed

* Postgres: Support walrus operator named arguments [#6299](https://github.com/sqlfluff/sqlfluff/pull/6299) [@keraion](https://github.com/keraion)
* TSQL: handle nested joins, RF01 better aliasing [#6300](https://github.com/sqlfluff/sqlfluff/pull/6300) [@keraion](https://github.com/keraion)
* Exclude Macros - Allow multiple paths. [#6221](https://github.com/sqlfluff/sqlfluff/pull/6221) [@culpgrant](https://github.com/culpgrant)
* Dededuplicate rule ignore docs [#6296](https://github.com/sqlfluff/sqlfluff/pull/6296) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bugfix for LT07 with consumed newlines. [#6294](https://github.com/sqlfluff/sqlfluff/pull/6294) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bugfix for LT12 with jinja whitespace consumption [#6292](https://github.com/sqlfluff/sqlfluff/pull/6292) [@alanmcruickshank](https://github.com/alanmcruickshank)
* RF02: Ignore `DECLARE` variables in BigQuery [#6295](https://github.com/sqlfluff/sqlfluff/pull/6295) [@keraion](https://github.com/keraion)
* Bugfix for JJ01 in parallel mode [#6293](https://github.com/sqlfluff/sqlfluff/pull/6293) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow arbitrary attributes & methods for `ThisEmulator` [#6254](https://github.com/sqlfluff/sqlfluff/pull/6254) [@mroy-seedbox](https://github.com/mroy-seedbox)
* RF05: Add `table_aliases` option [#6273](https://github.com/sqlfluff/sqlfluff/pull/6273) [@keraion](https://github.com/keraion)
* BigQuery: Add support for concatenating in `EXECUTE IMMEDIATE` [#6287](https://github.com/sqlfluff/sqlfluff/pull/6287) [@keraion](https://github.com/keraion)
* BigQuery: Add support for `SET` with system variables [#6288](https://github.com/sqlfluff/sqlfluff/pull/6288) [@keraion](https://github.com/keraion)
* Plugins: Migrate example plugin to `pyproject.toml` [#6286](https://github.com/sqlfluff/sqlfluff/pull/6286) [@keraion](https://github.com/keraion)
* TSQL: Add DATETRUC to date_part_function_name list [#6283](https://github.com/sqlfluff/sqlfluff/pull/6283) [@paysni](https://github.com/paysni)
* MySQL Alter table convert to character set [#6277](https://github.com/sqlfluff/sqlfluff/pull/6277) [@greg-finley](https://github.com/greg-finley)
* Remove dependency on coveralls. [#6284](https://github.com/sqlfluff/sqlfluff/pull/6284) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Test dbt Templater Plugin with dbt 1.9.0 [#6280](https://github.com/sqlfluff/sqlfluff/pull/6280) [@edgarrmondragon](https://github.com/edgarrmondragon)
* AM06: Ignore array expressions in BigQuery [#6276](https://github.com/sqlfluff/sqlfluff/pull/6276) [@keraion](https://github.com/keraion)
* Add mariadb to issue labeler [#6278](https://github.com/sqlfluff/sqlfluff/pull/6278) [@greg-finley](https://github.com/greg-finley)
* BigQuery: Add `GROUPING SETS` clause [#6275](https://github.com/sqlfluff/sqlfluff/pull/6275) [@keraion](https://github.com/keraion)
* Snowflake: Support `ARRAY` types [#6272](https://github.com/sqlfluff/sqlfluff/pull/6272) [@keraion](https://github.com/keraion)
* Move most of the config validation settings out into rule bundles. [#6262](https://github.com/sqlfluff/sqlfluff/pull/6262) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Revise warnings with fixing unfixable files. [#6257](https://github.com/sqlfluff/sqlfluff/pull/6257) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Strict mypy on `sqlfluff.core` [#6246](https://github.com/sqlfluff/sqlfluff/pull/6246) [@alanmcruickshank](https://github.com/alanmcruickshank)
* DuckDB: Add `DROP MACRO` [#6270](https://github.com/sqlfluff/sqlfluff/pull/6270) [@keraion](https://github.com/keraion)
* Added Support for Databricks SQL Notebook Cells [#6267](https://github.com/sqlfluff/sqlfluff/pull/6267) [@gabepesco](https://github.com/gabepesco)
* dbt templater `pyproject.toml` nits [#6268](https://github.com/sqlfluff/sqlfluff/pull/6268) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add UTF8 support for identifiers in Vertica dialect [#6183](https://github.com/sqlfluff/sqlfluff/pull/6183) [@troshnev](https://github.com/troshnev)
* Almost all of `util` up to strict typing [#6263](https://github.com/sqlfluff/sqlfluff/pull/6263) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update link to diff-cover docs [#6256](https://github.com/sqlfluff/sqlfluff/pull/6256) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: AL09 handle double quoted identifiers [#6249](https://github.com/sqlfluff/sqlfluff/pull/6249) [@keraion](https://github.com/keraion)
* fix: complex file extensions discovery [#6228](https://github.com/sqlfluff/sqlfluff/pull/6228) [@Clepech](https://github.com/Clepech)
* fix RF06 issue in postgres naked identifier regex [#6247](https://github.com/sqlfluff/sqlfluff/pull/6247) [@fvankrieken](https://github.com/fvankrieken)
* Strict typing for `sqlfluff.core.linter` [#6240](https://github.com/sqlfluff/sqlfluff/pull/6240) [@alanmcruickshank](https://github.com/alanmcruickshank)
* DuckDB: Fixed `DatatypeSegment` references [#6244](https://github.com/sqlfluff/sqlfluff/pull/6244) [@keraion](https://github.com/keraion)
* Postgres: Support `SET` with double quoted identifiers [#6243](https://github.com/sqlfluff/sqlfluff/pull/6243) [@keraion](https://github.com/keraion)
* Consolidate Teradata tests [#6241](https://github.com/sqlfluff/sqlfluff/pull/6241) [@greg-finley](https://github.com/greg-finley)
* RF02: Ignore alias references that are self-inner [#6242](https://github.com/sqlfluff/sqlfluff/pull/6242) [@keraion](https://github.com/keraion)
* Add additional CREATE TABLE support for Databricks [#6216](https://github.com/sqlfluff/sqlfluff/pull/6216) [@pahunter90](https://github.com/pahunter90)
* Complete the support for PIVOT in Snowflake dialect [#6217](https://github.com/sqlfluff/sqlfluff/pull/6217) [@fpsebastiam](https://github.com/fpsebastiam)
* Exasol - allow function calls in values clause [#6226](https://github.com/sqlfluff/sqlfluff/pull/6226) [@stephnan](https://github.com/stephnan)
* Snowflake: Support defining virtual columns [#6237](https://github.com/sqlfluff/sqlfluff/pull/6237) [@babak-l1](https://github.com/babak-l1)
* Teradata order of VOLATILE and MULTISET [#6233](https://github.com/sqlfluff/sqlfluff/pull/6233) [@greg-finley](https://github.com/greg-finley)
* Remove duplicate timing columns from the timing records [#6229](https://github.com/sqlfluff/sqlfluff/pull/6229) [@Tenzer](https://github.com/Tenzer)
* Fix time travel clauses in Snowflake dialect [#6230](https://github.com/sqlfluff/sqlfluff/pull/6230) [@fpsebastiam](https://github.com/fpsebastiam)


## New Contributors
* [@fpsebastiam](https://github.com/fpsebastiam) made their first contribution in [#6230](https://github.com/sqlfluff/sqlfluff/pull/6230)
* [@Tenzer](https://github.com/Tenzer) made their first contribution in [#6229](https://github.com/sqlfluff/sqlfluff/pull/6229)
* [@Clepech](https://github.com/Clepech) made their first contribution in [#6228](https://github.com/sqlfluff/sqlfluff/pull/6228)
* [@troshnev](https://github.com/troshnev) made their first contribution in [#6183](https://github.com/sqlfluff/sqlfluff/pull/6183)
* [@gabepesco](https://github.com/gabepesco) made their first contribution in [#6267](https://github.com/sqlfluff/sqlfluff/pull/6267)
* [@mroy-seedbox](https://github.com/mroy-seedbox) made their first contribution in [#6254](https://github.com/sqlfluff/sqlfluff/pull/6254)

## [3.2.0] - 2024-09-18

## Highlights

This release brings a few minor breaking changes, both for the core project
and for the dbt templater. For the main project:

* Resolving an issue with the spacing of functions (LT01), which
  involved a change to how functions are parsed. If your project relies
  on the specific parsing of functions, the bracketed arguments are now
  wrapped in a `function_contents` object. We recommend that you examine
  the new parsing structure using this new release in testing first.

* `RF06` (`references.quoting`) is now case sensitive when removing
  quotes which are detected as unnecessary. This rule has also been re-enabled
  by default for Snowflake and Postgres where it had previously been disabled
  (for the reason that in the past it hadn't been appropriately case
  sensitive). Treatment for totally case-insensitive dialects like DuckDB
  and SparkSQL have also been included. Please check the new documentation
  for this rule (which is much more explicit now), for details related to
  your dialect.

* Patterns equivalent to those from `.sqlfluffignore` can now be included
  in `.sqlfluff` and `pyproject.toml` files.

* Using the `python` templater, users now have an option to include variables
  which include a dot in the path, like `{{ foo.bar }}` using a special
  `sqlfluff` context variable.

* Significant changes under the hood to the handling of configuration files.
  Most of these should not be visible to end users, but for anyone integrating
  SQLFluff into a larger project and relying on native file loading may need
  to refactor their project for this release. Most notably here, for maintainers
  of plugins, the `ConfigLoader` class has been deprecated, and plugins should
  instead call the config loading functions directly. See the example plugin
  for details.

* Documentation, especially for dialects, has been significantly improved.
  Documentation for `CP02` (`capitalisation.identifiers`) has also been
  clarified to make it's implication for references and aliases more clear.

* During testing, to isolate the effect of specific rules, there's a new
  CLI option `--disable-noqa-except` which allows all `noqa` options to
  be ignored _except_ the ones provided in this option.

For the dbt templater:

* Support for dbt 1.1-1.3 has been removed. All have been in End of Life (EOL)
  support by dbtlabs for almost two years. They are also poorly supported by
  other projects and tools.

* The dbt templater has been migrated to use `pyproject.toml`.

* Handling of errors and exceptions raised within dbt has had an overhaul.
  Users may see a slightly different presentation of errors, but the overall
  stability should be more robust.

In addition to those changes, there have been too many dialect contributions
and bugfixes  to mention specifically. We've also seen **six** people make their
first contributions to the project as part of preparing for this release! 🎉🏆🎉.

## What’s Changed

* Handle multi-processing dbt exceptions much better. [#6138](https://github.com/sqlfluff/sqlfluff/pull/6138) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Support variables with dot in python templater [#5872](https://github.com/sqlfluff/sqlfluff/pull/5872) [@timchurch](https://github.com/timchurch)
* Add postgres normalization operator support [#6211](https://github.com/sqlfluff/sqlfluff/pull/6211) [@fnimick](https://github.com/fnimick)
* Fix patch will anchor on first buffer insertion point [#6212](https://github.com/sqlfluff/sqlfluff/pull/6212) [@keraion](https://github.com/keraion)
* Allow ignore patterns in other config files. [#6130](https://github.com/sqlfluff/sqlfluff/pull/6130) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Strict typing in `config` and `helpers`. [#6206](https://github.com/sqlfluff/sqlfluff/pull/6206) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: Support multiple options in `SET` statement [#6205](https://github.com/sqlfluff/sqlfluff/pull/6205) [@keraion](https://github.com/keraion)
* DuckDB: Support `CREATE TYPE` statement [#6204](https://github.com/sqlfluff/sqlfluff/pull/6204) [@keraion](https://github.com/keraion)
* Update Slack link [#6203](https://github.com/sqlfluff/sqlfluff/pull/6203) [@greg-finley](https://github.com/greg-finley)
* Add quoted literal checking for Snowflake TARGET_LAG in dynamic tables. [#6201](https://github.com/sqlfluff/sqlfluff/pull/6201) [@mvastarelli](https://github.com/mvastarelli)
* Databricks: Support `COMMENT ON` statement [#6196](https://github.com/sqlfluff/sqlfluff/pull/6196) [@keraion](https://github.com/keraion)
* DuckDB: Support `STRUCT` datatype [#6198](https://github.com/sqlfluff/sqlfluff/pull/6198) [@keraion](https://github.com/keraion)
* Deprecate the `ConfigLoader` [#6177](https://github.com/sqlfluff/sqlfluff/pull/6177) [@alanmcruickshank](https://github.com/alanmcruickshank)
* DuckDB: Support `CREATE MACRO`/`CREATE FUNCTION` [#6194](https://github.com/sqlfluff/sqlfluff/pull/6194) [@keraion](https://github.com/keraion)
* DuckDB: Support functions with walrus operators [#6193](https://github.com/sqlfluff/sqlfluff/pull/6193) [@keraion](https://github.com/keraion)
* Add volume syntax support for Databricks [#6179](https://github.com/sqlfluff/sqlfluff/pull/6179) [@TheCleric](https://github.com/TheCleric)
* Handle errors better in AL09 [#6186](https://github.com/sqlfluff/sqlfluff/pull/6186) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for managed locations to databricks dialect schemas [#6182](https://github.com/sqlfluff/sqlfluff/pull/6182) [@TheCleric](https://github.com/TheCleric)
* MYSQL: Create Table Optional AS [#6109](https://github.com/sqlfluff/sqlfluff/pull/6109) [@WittierDinosaur](https://github.com/WittierDinosaur)
* More dialect documentation [#6165](https://github.com/sqlfluff/sqlfluff/pull/6165) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Better documentation on how to cross reference rules and fix a few. [#6162](https://github.com/sqlfluff/sqlfluff/pull/6162) [@alanmcruickshank](https://github.com/alanmcruickshank)
* RF06: Case Sensitivity [#6173](https://github.com/sqlfluff/sqlfluff/pull/6173) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SparkSQL/Databricks: Support for `VARIANT` type [#6167](https://github.com/sqlfluff/sqlfluff/pull/6167) [@keraion](https://github.com/keraion)
* sparksql: Allow `INSERT OVERWRITE` after a CTE [#6172](https://github.com/sqlfluff/sqlfluff/pull/6172) [@keraion](https://github.com/keraion)
* postgres: Add `SET CONSTRAINTS` statement [#6171](https://github.com/sqlfluff/sqlfluff/pull/6171) [@keraion](https://github.com/keraion)
* TSQL: Fix `MERGE` without a target alias [#6170](https://github.com/sqlfluff/sqlfluff/pull/6170) [@keraion](https://github.com/keraion)
* TSQL: add `OFFSET` and `FETCH` [#6169](https://github.com/sqlfluff/sqlfluff/pull/6169) [@keraion](https://github.com/keraion)
* postgres: Add support for `SUBSCRIPTION` statements [#6168](https://github.com/sqlfluff/sqlfluff/pull/6168) [@keraion](https://github.com/keraion)
* Duckdb: Add support for list comprehensions [#6166](https://github.com/sqlfluff/sqlfluff/pull/6166) [@keraion](https://github.com/keraion)
* Update Docs and tests for CP02 [#6163](https://github.com/sqlfluff/sqlfluff/pull/6163) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Cached property in RF06 rather than DIY [#6164](https://github.com/sqlfluff/sqlfluff/pull/6164) [@alanmcruickshank](https://github.com/alanmcruickshank)
* CI: Update `util.py` for dbt templater `pyproject.toml` [#6160](https://github.com/sqlfluff/sqlfluff/pull/6160) [@keraion](https://github.com/keraion)
* Auto generate dialect docs [#6153](https://github.com/sqlfluff/sqlfluff/pull/6153) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Deprecate support for dbt 1.1-1.3 [#6159](https://github.com/sqlfluff/sqlfluff/pull/6159) [@WittierDinosaur](https://github.com/WittierDinosaur)
* ST08: Ignore `DISTINCT`s with subqueries [#6146](https://github.com/sqlfluff/sqlfluff/pull/6146) [@keraion](https://github.com/keraion)
* Duckdb: Fix Create View coverage [#6158](https://github.com/sqlfluff/sqlfluff/pull/6158) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Support Password Policies [#6154](https://github.com/sqlfluff/sqlfluff/pull/6154) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Allow negative integers in sequences [#6111](https://github.com/sqlfluff/sqlfluff/pull/6111) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Add SHOW Statement [#6110](https://github.com/sqlfluff/sqlfluff/pull/6110) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Migrate dbt templater to pyproject.toml [#6155](https://github.com/sqlfluff/sqlfluff/pull/6155) [@keraion](https://github.com/keraion)
* Snowflake: Add DEFAULT option for function parameters [#6145](https://github.com/sqlfluff/sqlfluff/pull/6145) [@keraion](https://github.com/keraion)
* Snowflake: fixes parsing for INCLUDE_METADATA in COPY INTO statement [#6150](https://github.com/sqlfluff/sqlfluff/pull/6150) [@jcrobak](https://github.com/jcrobak)
* [SNOWFLAKE] Adding support for extended constraint definitions [#6151](https://github.com/sqlfluff/sqlfluff/pull/6151) [@babak-l1](https://github.com/babak-l1)
* Snowflake: fixes parsing for PARSE_HEADER in FILE FORMAT statement [#6149](https://github.com/sqlfluff/sqlfluff/pull/6149) [@jcrobak](https://github.com/jcrobak)
* fix: avoid strip_newlines when encounter comments in inline segments [#6140](https://github.com/sqlfluff/sqlfluff/pull/6140) [@Cynthia-Cheng](https://github.com/Cynthia-Cheng)
* More robust exception handling for dbt. [#6144](https://github.com/sqlfluff/sqlfluff/pull/6144) [@alanmcruickshank](https://github.com/alanmcruickshank)
* postgres: Add `ENCRYPTED PASSWORD` option in `CREATE USER` [#6143](https://github.com/sqlfluff/sqlfluff/pull/6143) [@keraion](https://github.com/keraion)
* Fix support of INTERVAL in ClickHouse [#6112](https://github.com/sqlfluff/sqlfluff/pull/6112) [@Pavel-Strybuk](https://github.com/Pavel-Strybuk)
* Add support for Snowflake Higher-Order Functions [#6136](https://github.com/sqlfluff/sqlfluff/pull/6136) [@amardatar](https://github.com/amardatar)
* Method extraction and more robust typing in config. [#6135](https://github.com/sqlfluff/sqlfluff/pull/6135) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add missing databricks and sparksql ALTER statements [#6102](https://github.com/sqlfluff/sqlfluff/pull/6102) [@pahunter90](https://github.com/pahunter90)
* fix: program_counter move in JinjaTracer (#6121) [#6123](https://github.com/sqlfluff/sqlfluff/pull/6123) [@Cynthia-Cheng](https://github.com/Cynthia-Cheng)
* CI: allow hidden file upload for coverage files [#6139](https://github.com/sqlfluff/sqlfluff/pull/6139) [@keraion](https://github.com/keraion)
* Fix: added DOWNSTREAM keyword for TARGET_LAG on dynamic tables in Snowflake. [#6131](https://github.com/sqlfluff/sqlfluff/pull/6131) [@mvastarelli](https://github.com/mvastarelli)
* Trino Dialect: update ARRAY type handling [#6127](https://github.com/sqlfluff/sqlfluff/pull/6127) [@kirkhansen](https://github.com/kirkhansen)
* Split apart config module [#6128](https://github.com/sqlfluff/sqlfluff/pull/6128) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add option for allowing only a subset of rules for noqa [#6115](https://github.com/sqlfluff/sqlfluff/pull/6115) [@keraion](https://github.com/keraion)
* TSQL: Allow for empty catch block in try-catch [#6116](https://github.com/sqlfluff/sqlfluff/pull/6116) [@keraion](https://github.com/keraion)
* Change evaluation order of literals before column refs in bracketed, delimited expressions [#6117](https://github.com/sqlfluff/sqlfluff/pull/6117) [@keraion](https://github.com/keraion)
* Fix spacing rules for functions [#5809](https://github.com/sqlfluff/sqlfluff/pull/5809) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Add conflict_clause to unique table constraint [#6106](https://github.com/sqlfluff/sqlfluff/pull/6106) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Support Raise Function [#6108](https://github.com/sqlfluff/sqlfluff/pull/6108) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Create Trigger WHEN optionally bracketed [#6107](https://github.com/sqlfluff/sqlfluff/pull/6107) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Added `INTERVAL`s to Frame Clause [#6105](https://github.com/sqlfluff/sqlfluff/pull/6105) [@keraion](https://github.com/keraion)
* Postgres: Add `IS UNKNOWN`  [#6094](https://github.com/sqlfluff/sqlfluff/pull/6094) [@keraion](https://github.com/keraion)
* RF02: Handle subquery column qualification [#6091](https://github.com/sqlfluff/sqlfluff/pull/6091) [@keraion](https://github.com/keraion)
* tsql: Allow leading dots in table references [#6093](https://github.com/sqlfluff/sqlfluff/pull/6093) [@keraion](https://github.com/keraion)


## New Contributors
* [@mvastarelli](https://github.com/mvastarelli) made their first contribution in [#6131](https://github.com/sqlfluff/sqlfluff/pull/6131)
* [@Cynthia-Cheng](https://github.com/Cynthia-Cheng) made their first contribution in [#6123](https://github.com/sqlfluff/sqlfluff/pull/6123)
* [@pahunter90](https://github.com/pahunter90) made their first contribution in [#6102](https://github.com/sqlfluff/sqlfluff/pull/6102)
* [@amardatar](https://github.com/amardatar) made their first contribution in [#6136](https://github.com/sqlfluff/sqlfluff/pull/6136)
* [@jcrobak](https://github.com/jcrobak) made their first contribution in [#6149](https://github.com/sqlfluff/sqlfluff/pull/6149)
* [@babak-l1](https://github.com/babak-l1) made their first contribution in [#6151](https://github.com/sqlfluff/sqlfluff/pull/6151)

## [3.1.1] - 2024-08-20

## Highlights

This release brings a bumper lot of bugfixes, dialect improvements and other
minor improvements across the board. Most notably:

* A rework of the structure of the docs. **NOTE**: This does change the url
  of some docs pages, but to prevent future moves, we've also provided
  permalinks to most important pages and rules. See the `conf.py` file in
  the `docs` folder for a full list of permalinks.
* Solving rule conflicts between LT02 & LT02.
* Bugfixes to AM07, CV11, ST03, ST05 & RF03,
* Removes some redundant dependencies in for the dbt templater (which haven't
  been required for some time, but have been included in the install dependencies).
  Specifically: `markupsafe`, `ruamel.yaml`, `pydantic` & `rich`.
* And too many dialect improvements to summarise!

We've also seen **eleven** new contributors to the project! Thanks to all of them
for taking the time to contribute. 🎉🎉🏆🎉🎉

## What’s Changed

* dbt Templater: Increase `dbt deps` test fixture timeout [#6088](https://github.com/sqlfluff/sqlfluff/pull/6088) [@keraion](https://github.com/keraion)
* SparkSQL + Databricks: Add support for raw string literals [#6089](https://github.com/sqlfluff/sqlfluff/pull/6089) [@D-to-the-K](https://github.com/D-to-the-K)
* fixes #4855 - Add DECLARE statement in snowflake dialect [#6059](https://github.com/sqlfluff/sqlfluff/pull/6059) [@YungChunLu](https://github.com/YungChunLu)
* Adding CTE to mysql views [#6077](https://github.com/sqlfluff/sqlfluff/pull/6077) [@gone](https://github.com/gone)
* Rationalise config discovery routines. [#6080](https://github.com/sqlfluff/sqlfluff/pull/6080) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix(dialect-trino): Trino ROW datatype definition in queries [#6085](https://github.com/sqlfluff/sqlfluff/pull/6085) [@bonisb](https://github.com/bonisb)
* Databricks: Add support for GROUP BY ALL [#6082](https://github.com/sqlfluff/sqlfluff/pull/6082) [@D-to-the-K](https://github.com/D-to-the-K)
* fix(clickhouse): add support for tuple() and ENGINE MergeTree [#6079](https://github.com/sqlfluff/sqlfluff/pull/6079) [@ogirardot](https://github.com/ogirardot)
* Add perma-links for rules [#6066](https://github.com/sqlfluff/sqlfluff/pull/6066) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix(clickhouse): add support for rename statement [#6073](https://github.com/sqlfluff/sqlfluff/pull/6073) [@ogirardot](https://github.com/ogirardot)
* fix(clickhouse): add support for INTO OUTFILE and supported FORMATs [#6065](https://github.com/sqlfluff/sqlfluff/pull/6065) [@ogirardot](https://github.com/ogirardot)
* LT04: Fix indentation conflict with LT02 [#6068](https://github.com/sqlfluff/sqlfluff/pull/6068) [@keraion](https://github.com/keraion)
* pre-commit: Disable progress bar [#6069](https://github.com/sqlfluff/sqlfluff/pull/6069) [@keraion](https://github.com/keraion)
* feat(clickhouse): add support for decimal(x,y), decimal32(x) and match [#6063](https://github.com/sqlfluff/sqlfluff/pull/6063) [@ogirardot](https://github.com/ogirardot)
* Big docs refactor. [#6052](https://github.com/sqlfluff/sqlfluff/pull/6052) [@alanmcruickshank](https://github.com/alanmcruickshank)
* ST05: Handle set statement's subsequent queries [#6062](https://github.com/sqlfluff/sqlfluff/pull/6062) [@keraion](https://github.com/keraion)
* fix(clickhouse): add support for limit by and bracketed format [#6061](https://github.com/sqlfluff/sqlfluff/pull/6061) [@ogirardot](https://github.com/ogirardot)
* fix(clickhouse): add support for DateTime64(precision, tz) and Tuples() [#6060](https://github.com/sqlfluff/sqlfluff/pull/6060) [@ogirardot](https://github.com/ogirardot)
* Copy statement postgres v9 compatibility support [#5181](https://github.com/sqlfluff/sqlfluff/pull/5181) [@Fullcure3](https://github.com/Fullcure3)
* Run dbt tests in py312 by default [#5861](https://github.com/sqlfluff/sqlfluff/pull/5861) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Extract path discovery routines from config and linter. [#6057](https://github.com/sqlfluff/sqlfluff/pull/6057) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: Added SET TRANSACTION parsing [#5781](https://github.com/sqlfluff/sqlfluff/pull/5781) [@Xemptuous](https://github.com/Xemptuous)
* Support declare or replace variable statement for Databricks dialect [#6054](https://github.com/sqlfluff/sqlfluff/pull/6054) [@urosstan-db](https://github.com/urosstan-db)
* Exclude Macros from a path provided [#6031](https://github.com/sqlfluff/sqlfluff/pull/6031) [@culpgrant](https://github.com/culpgrant)
* ST03: Detect CTE usage in nested `WITH` clauses [#6017](https://github.com/sqlfluff/sqlfluff/pull/6017) [@keraion](https://github.com/keraion)
* TRINO: support FILTER after WITHIN GROUP agg expression [#6056](https://github.com/sqlfluff/sqlfluff/pull/6056) [@rileymcdowell](https://github.com/rileymcdowell)
* Fix/snowflake double quotes [#5727](https://github.com/sqlfluff/sqlfluff/pull/5727) [@Starstruckk](https://github.com/Starstruckk)
* bq_table_function : Added functionality to parse table functionsin BigQuery [#5480](https://github.com/sqlfluff/sqlfluff/pull/5480) [@moh-lch](https://github.com/moh-lch)
* Fix Athena Partitioned By format for iceberg tables [#5399](https://github.com/sqlfluff/sqlfluff/pull/5399) [@jverhoeks](https://github.com/jverhoeks)
* fix: redshift dialect, EXTENSION added [#6025](https://github.com/sqlfluff/sqlfluff/pull/6025) [@rafalbog](https://github.com/rafalbog)
* Fix ignored inline rule overrides (#5697) [#6010](https://github.com/sqlfluff/sqlfluff/pull/6010) [@alesbukovsky](https://github.com/alesbukovsky)
* Update the docs on RF03 [#6051](https://github.com/sqlfluff/sqlfluff/pull/6051) [@alanmcruickshank](https://github.com/alanmcruickshank)
* RF03: Fixed some subquery reference scenarios [#6046](https://github.com/sqlfluff/sqlfluff/pull/6046) [@keraion](https://github.com/keraion)
* CV11: Remove rogue print statement [#6047](https://github.com/sqlfluff/sqlfluff/pull/6047) [@keraion](https://github.com/keraion)
* Snowflake: fixes parsing for AGGREGATE in CREATE FUNCTION statement [#6049](https://github.com/sqlfluff/sqlfluff/pull/6049) [@hawle](https://github.com/hawle)
* Snowflake:adds optional IF NOT EXISTS to ADD COLUMN [#6050](https://github.com/sqlfluff/sqlfluff/pull/6050) [@hawle](https://github.com/hawle)
* Replace types-pkg-resources with types-setuptools [#6039](https://github.com/sqlfluff/sqlfluff/pull/6039) [@keraion](https://github.com/keraion)
* Remove old deps for dbt templater [#6028](https://github.com/sqlfluff/sqlfluff/pull/6028) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Added GENERATED AS IDENTITY support to DataBricks dialect [#6004](https://github.com/sqlfluff/sqlfluff/pull/6004) [@nicolb2305](https://github.com/nicolb2305)
* Add support for Clickhouse ORDER BY WITH FILL [#6018](https://github.com/sqlfluff/sqlfluff/pull/6018) [@snikch](https://github.com/snikch)
* Parse API example [#6021](https://github.com/sqlfluff/sqlfluff/pull/6021) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add additional dateparts from DATEPART() [#6012](https://github.com/sqlfluff/sqlfluff/pull/6012) [@yorickbouma](https://github.com/yorickbouma)
* MariaDB: Add support for GROUP BY ... ASC/DESC and GROUP BY ... WITH ROLLUP [#6009](https://github.com/sqlfluff/sqlfluff/pull/6009) [@pprkut](https://github.com/pprkut)
* AM07: Handle set expressions with bracketed selects [#6005](https://github.com/sqlfluff/sqlfluff/pull/6005) [@keraion](https://github.com/keraion)
* MariaDB: Add support for DELETE/INSERT/REPLACE ... RETURNING [#6008](https://github.com/sqlfluff/sqlfluff/pull/6008) [@pprkut](https://github.com/pprkut)
* MariaDB: Add mariadb specific syntax for generated columns [#6007](https://github.com/sqlfluff/sqlfluff/pull/6007) [@pprkut](https://github.com/pprkut)
* Snowflake: fixes drop column if exists parsing rules [#5999](https://github.com/sqlfluff/sqlfluff/pull/5999) [@hawle](https://github.com/hawle)
* Fix TSQL Post Table Expr intrepreted as function [#6001](https://github.com/sqlfluff/sqlfluff/pull/6001) [@ulixius9](https://github.com/ulixius9)


## New Contributors
* [@yorickbouma](https://github.com/yorickbouma) made their first contribution in [#6012](https://github.com/sqlfluff/sqlfluff/pull/6012)
* [@snikch](https://github.com/snikch) made their first contribution in [#6018](https://github.com/sqlfluff/sqlfluff/pull/6018)
* [@nicolb2305](https://github.com/nicolb2305) made their first contribution in [#6004](https://github.com/sqlfluff/sqlfluff/pull/6004)
* [@alesbukovsky](https://github.com/alesbukovsky) made their first contribution in [#6010](https://github.com/sqlfluff/sqlfluff/pull/6010)
* [@rafalbog](https://github.com/rafalbog) made their first contribution in [#6025](https://github.com/sqlfluff/sqlfluff/pull/6025)
* [@jverhoeks](https://github.com/jverhoeks) made their first contribution in [#5399](https://github.com/sqlfluff/sqlfluff/pull/5399)
* [@moh-lch](https://github.com/moh-lch) made their first contribution in [#5480](https://github.com/sqlfluff/sqlfluff/pull/5480)
* [@Starstruckk](https://github.com/Starstruckk) made their first contribution in [#5727](https://github.com/sqlfluff/sqlfluff/pull/5727)
* [@culpgrant](https://github.com/culpgrant) made their first contribution in [#6031](https://github.com/sqlfluff/sqlfluff/pull/6031)
* [@urosstan-db](https://github.com/urosstan-db) made their first contribution in [#6054](https://github.com/sqlfluff/sqlfluff/pull/6054)
* [@ogirardot](https://github.com/ogirardot) made their first contribution in [#6060](https://github.com/sqlfluff/sqlfluff/pull/6060)
* [@D-to-the-K](https://github.com/D-to-the-K) made their first contribution in [#6082](https://github.com/sqlfluff/sqlfluff/pull/6082)
* [@bonisb](https://github.com/bonisb) made their first contribution in [#6085](https://github.com/sqlfluff/sqlfluff/pull/6085)
* [@gone](https://github.com/gone) made their first contribution in [#6077](https://github.com/sqlfluff/sqlfluff/pull/6077)
* [@YungChunLu](https://github.com/YungChunLu) made their first contribution in [#6059](https://github.com/sqlfluff/sqlfluff/pull/6059)

## [3.1.0] - 2024-07-03

## Highlights

This minor release has two breaking changes:
 - The addition of camelCase in the extended capitalisation policy. This change removes the ability to
autodetect PascalCase, from now on PascalCase, and camelCase must be explicitly set in the config if desired.
 - The detection method for sqlfluff config has changed. It should now be more consistent, regardless of how deep if the directory
structure you run the command from.

This release also brings in support for the MariaDB dialect. As well as this, there are many bugfixes,
and dialect improvements.

Thanks also to the **twelve** new contributors whose work was included
in this release! 🎉🎉🏆🎉🎉

## What’s Changed

* Snowflake: alter procedure & function updates [#5997](https://github.com/sqlfluff/sqlfluff/pull/5997) [@hawle](https://github.com/hawle)
* Snowflake: fix connect by prior selects [#5996](https://github.com/sqlfluff/sqlfluff/pull/5996) [@hawle](https://github.com/hawle)
* Snowflake: adds EVENT TABLE support [#5995](https://github.com/sqlfluff/sqlfluff/pull/5995) [@hawle](https://github.com/hawle)
* Feature/MariaDB dialect [#5856](https://github.com/sqlfluff/sqlfluff/pull/5856) [@Xemptuous](https://github.com/Xemptuous)
* Postgres: Fix multiline concat for special literals [#5965](https://github.com/sqlfluff/sqlfluff/pull/5965) [@keraion](https://github.com/keraion)
* ST05: Evaluate nested queries as a whole [#5990](https://github.com/sqlfluff/sqlfluff/pull/5990) [@keraion](https://github.com/keraion)
* Naïve multi-variant jinja linting [#5822](https://github.com/sqlfluff/sqlfluff/pull/5822) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update Snowflake Unpivot Dialect to INCLUDE/EXCLUDE NULLs [#5961](https://github.com/sqlfluff/sqlfluff/pull/5961) [@danatmercury](https://github.com/danatmercury)
* Snowflake: Adds parsing fixes for external access integrations in create procedure and function [#5986](https://github.com/sqlfluff/sqlfluff/pull/5986) [@hawle](https://github.com/hawle)
* Select Analysis: Don't recursively crawl merge subselects [#5981](https://github.com/sqlfluff/sqlfluff/pull/5981) [@keraion](https://github.com/keraion)
* Parent dir config search [#5958](https://github.com/sqlfluff/sqlfluff/pull/5958) [@j-svensmark](https://github.com/j-svensmark)
* Enable AM02 for bigquery, clickhouse, databricks, db2 [#5979](https://github.com/sqlfluff/sqlfluff/pull/5979) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add COMMENT ON support to Trino dialect [#5984](https://github.com/sqlfluff/sqlfluff/pull/5984) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: fix scriptless stored procedure parsing [#5982](https://github.com/sqlfluff/sqlfluff/pull/5982) [@hawle](https://github.com/hawle)
* Add support for custom JinjaTracer implementations [#5937](https://github.com/sqlfluff/sqlfluff/pull/5937) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* MySQL: Fix variable handlings inside expressions [#5967](https://github.com/sqlfluff/sqlfluff/pull/5967) [@kzosabe](https://github.com/kzosabe)
* Allow anonymous PIVOTs in Databricks [#5968](https://github.com/sqlfluff/sqlfluff/pull/5968) [@TheCleric](https://github.com/TheCleric)
* Rebreak: Fix meta dedent segment order [#5972](https://github.com/sqlfluff/sqlfluff/pull/5972) [@keraion](https://github.com/keraion)
* Update athena dialect for CTAS [#5974](https://github.com/sqlfluff/sqlfluff/pull/5974) [@KulykDmytro](https://github.com/KulykDmytro)
* fix(dialect-trino): Support Grouping Sets [#5970](https://github.com/sqlfluff/sqlfluff/pull/5970) [@eskabetxe](https://github.com/eskabetxe)
* BigQuery: Support various DROP statements [#5966](https://github.com/sqlfluff/sqlfluff/pull/5966) [@kzosabe](https://github.com/kzosabe)
* AL07: Fix self-referencing table aliases [#5963](https://github.com/sqlfluff/sqlfluff/pull/5963) [@keraion](https://github.com/keraion)
* Clickhouse 'create view' support [#5910](https://github.com/sqlfluff/sqlfluff/pull/5910) [@DimaSamodurov](https://github.com/DimaSamodurov)
* Capitalisation: Add camelCase [#5777](https://github.com/sqlfluff/sqlfluff/pull/5777) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Exasol: Use ANSI value_clause to handle insert_stmts correctly [#5959](https://github.com/sqlfluff/sqlfluff/pull/5959) [@stephnan](https://github.com/stephnan)
* Support quoted psql parameters with `placeholder` templater [#5880](https://github.com/sqlfluff/sqlfluff/pull/5880) [@fvankrieken](https://github.com/fvankrieken)
* Don't indent invisible template slices [#5938](https://github.com/sqlfluff/sqlfluff/pull/5938) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* 5944: Add support for databricks named parameters [#5946](https://github.com/sqlfluff/sqlfluff/pull/5946) [@TheCleric](https://github.com/TheCleric)
* Add support for Databricks TRACK HISTORY [#5948](https://github.com/sqlfluff/sqlfluff/pull/5948) [@TheCleric](https://github.com/TheCleric)
* BigQuery: Support various ALTER statements [#5943](https://github.com/sqlfluff/sqlfluff/pull/5943) [@kzosabe](https://github.com/kzosabe)
* ClickHouse query-level SETTINGS support [#5941](https://github.com/sqlfluff/sqlfluff/pull/5941) [@pheepa](https://github.com/pheepa)
* MySQL: Add support for generated columns [#5939](https://github.com/sqlfluff/sqlfluff/pull/5939) [@pprkut](https://github.com/pprkut)
* Exasol: add REGEXP_LIKE [#5936](https://github.com/sqlfluff/sqlfluff/pull/5936) [@stephnan](https://github.com/stephnan)
* SQLite: Over clause support for window functions [#5935](https://github.com/sqlfluff/sqlfluff/pull/5935) [@atishay](https://github.com/atishay)
* T-SQL: Parameter assignment in SELECT vs alias [#5934](https://github.com/sqlfluff/sqlfluff/pull/5934) [@drjwelch](https://github.com/drjwelch)
* SQLite: Add named parameters support [#5914](https://github.com/sqlfluff/sqlfluff/pull/5914) [@atishay](https://github.com/atishay)
* SQLite: Support with key as a column name (as needed by json_each) [#5918](https://github.com/sqlfluff/sqlfluff/pull/5918) [@atishay](https://github.com/atishay)
* Add loader_search_path setting to Jinja templater [#5930](https://github.com/sqlfluff/sqlfluff/pull/5930) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SQLite: Add support for JSON functions. Fixes #5896 [#5917](https://github.com/sqlfluff/sqlfluff/pull/5917) [@atishay](https://github.com/atishay)
* dbt Templater: Suppress dbt 1.8 log messages [#5907](https://github.com/sqlfluff/sqlfluff/pull/5907) [@keraion](https://github.com/keraion)
* Clarify docs around subdir handling when loading macros [#5924](https://github.com/sqlfluff/sqlfluff/pull/5924) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* fix: add missing comma in Snowflake file types list [#5923](https://github.com/sqlfluff/sqlfluff/pull/5923) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* SQLite: Specialize create view with support for temporary views. [#5919](https://github.com/sqlfluff/sqlfluff/pull/5919) [@atishay](https://github.com/atishay)
* BigQuery: Fix array type parsing [#5912](https://github.com/sqlfluff/sqlfluff/pull/5912) [@kzosabe](https://github.com/kzosabe)
* BigQuery: Support unimplemented alter table and view statements [#5911](https://github.com/sqlfluff/sqlfluff/pull/5911) [@kzosabe](https://github.com/kzosabe)

## New Contributors

* [@atishay](https://github.com/atishay) made their first contribution in [#5919](https://github.com/sqlfluff/sqlfluff/pull/5919)
* [@drjwelch](https://github.com/drjwelch) made their first contribution in [#5934](https://github.com/sqlfluff/sqlfluff/pull/5934)
* [@stephnan](https://github.com/stephnan) made their first contribution in [#5936](https://github.com/sqlfluff/sqlfluff/pull/5936)
* [@pprkut](https://github.com/pprkut) made their first contribution in [#5939](https://github.com/sqlfluff/sqlfluff/pull/5939)
* [@pheepa](https://github.com/pheepa) made their first contribution in [#5941](https://github.com/sqlfluff/sqlfluff/pull/5941)
* [@TheCleric](https://github.com/TheCleric) made their first contribution in [#5948](https://github.com/sqlfluff/sqlfluff/pull/5948)
* [@fvankrieken](https://github.com/fvankrieken) made their first contribution in [#5880](https://github.com/sqlfluff/sqlfluff/pull/5880)
* [@DimaSamodurov](https://github.com/DimaSamodurov) made their first contribution in [#5910](https://github.com/sqlfluff/sqlfluff/pull/5910)
* [@eskabetxe](https://github.com/eskabetxe) made their first contribution in [#5970](https://github.com/sqlfluff/sqlfluff/pull/5970)
* [@hawle](https://github.com/hawle) made their first contribution in [#5982](https://github.com/sqlfluff/sqlfluff/pull/5982)
* [@danatmercury](https://github.com/danatmercury) made their first contribution in [#5961](https://github.com/sqlfluff/sqlfluff/pull/5961)
* [@Xemptuous](https://github.com/Xemptuous) made their first contribution in [#5856](https://github.com/sqlfluff/sqlfluff/pull/5856)

## [3.0.7] - 2024-05-23

## Highlights

This is primarily a fix for compatibility with dbt 1.8+. Beyond
that it also brings several dialect improvements to SQLite, Bigquery,
MySQL, Oracle & Clickhouse.

Thanks also to the **five** new contributors whose work was included
in this release! 🎉🎉🏆🎉🎉

## What’s Changed

* Add more minor features and fixes to sqlite dialect [#5894](https://github.com/sqlfluff/sqlfluff/pull/5894) [@Enduriel](https://github.com/Enduriel)
* Fix Clickhouse identifiers format [#5890](https://github.com/sqlfluff/sqlfluff/pull/5890) [@Pavel-Strybuk](https://github.com/Pavel-Strybuk)
* Add full support for on conflict clause in SQLite [#5888](https://github.com/sqlfluff/sqlfluff/pull/5888) [@Enduriel](https://github.com/Enduriel)
* dbt Templater Plugin: dbt 1.8 support [#5892](https://github.com/sqlfluff/sqlfluff/pull/5892) [@keraion](https://github.com/keraion)
* Added support for oracle materialized view [#5883](https://github.com/sqlfluff/sqlfluff/pull/5883) [@harshsoni2024](https://github.com/harshsoni2024)
* BigQuery: Support ALTER TABLE ADD KEY statements [#5881](https://github.com/sqlfluff/sqlfluff/pull/5881) [@kzosabe](https://github.com/kzosabe)
* MySQL: Support DIV and MOD operators [#5879](https://github.com/sqlfluff/sqlfluff/pull/5879) [@kzosabe](https://github.com/kzosabe)
* Update documentation to include all templaters [#5873](https://github.com/sqlfluff/sqlfluff/pull/5873) [@timchurch](https://github.com/timchurch)
* MySQL: Define date part function names [#5874](https://github.com/sqlfluff/sqlfluff/pull/5874) [@kzosabe](https://github.com/kzosabe)
* Remove typing_extensions requirement [#5860](https://github.com/sqlfluff/sqlfluff/pull/5860) [@qarkai](https://github.com/qarkai)
* BigQuery: Fix EXPORT DATA statement [#5859](https://github.com/sqlfluff/sqlfluff/pull/5859) [@kzosabe](https://github.com/kzosabe)
* BigQuery: Support CREATE INDEX statements [#5858](https://github.com/sqlfluff/sqlfluff/pull/5858) [@kzosabe](https://github.com/kzosabe)

## New Contributors

* [@qarkai](https://github.com/qarkai) made their first contribution in [#5860](https://github.com/sqlfluff/sqlfluff/pull/5860)
* [@timchurch](https://github.com/timchurch) made their first contribution in [#5873](https://github.com/sqlfluff/sqlfluff/pull/5873)
* [@harshsoni2024](https://github.com/harshsoni2024) made their first contribution in [#5883](https://github.com/sqlfluff/sqlfluff/pull/5883)
* [@Enduriel](https://github.com/Enduriel) made their first contribution in [#5888](https://github.com/sqlfluff/sqlfluff/pull/5888)
* [@Pavel-Strybuk](https://github.com/Pavel-Strybuk) made their first contribution in [#5890](https://github.com/sqlfluff/sqlfluff/pull/5890)

## [3.0.6] - 2024-05-06

## Highlights

This release primarily fixes an issue introduced by the recent dbt 1.7.14 release,
and better support for dbt 1.7+. It also includes a range of dialect improvements
and CLI refinements.

This release also includes the groundwork for linting the unrendered sections of
Jinja templates. More documentation on this will be released in due course when
it's ready for beta testing.

Thanks also to [@padraic00](https://github.com/padraic00) &
[@burhanyasar](https://github.com/burhanyasar) who made their first contributions
in this release. 🎉🎉🏆🎉🎉

## What’s Changed

* [fix_clickhouse] Temporary Table Create AS SELECT [#5843](https://github.com/sqlfluff/sqlfluff/pull/5843) [@konnectr](https://github.com/konnectr)
* Bugfix: ST02 - Compare entire condition expression [#5850](https://github.com/sqlfluff/sqlfluff/pull/5850) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Clichouse prewhere [#5849](https://github.com/sqlfluff/sqlfluff/pull/5849) [@konnectr](https://github.com/konnectr)
* BigQuery: Support missing DROP statements [#5848](https://github.com/sqlfluff/sqlfluff/pull/5848) [@kzosabe](https://github.com/kzosabe)
* BigQuery: various CREATE statements [#5846](https://github.com/sqlfluff/sqlfluff/pull/5846) [@greg-finley](https://github.com/greg-finley)
* BigQuery Alter Schema [#5835](https://github.com/sqlfluff/sqlfluff/pull/5835) [@greg-finley](https://github.com/greg-finley)
* Snowflake execute immediate from [#5836](https://github.com/sqlfluff/sqlfluff/pull/5836) [@greg-finley](https://github.com/greg-finley)
* Support dbt 1.7 [#5842](https://github.com/sqlfluff/sqlfluff/pull/5842) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Create extension cascade [#5834](https://github.com/sqlfluff/sqlfluff/pull/5834) [@greg-finley](https://github.com/greg-finley)
* Postgres: Add Support for PostGIS operators [#5830](https://github.com/sqlfluff/sqlfluff/pull/5830) [@burhanyasar](https://github.com/burhanyasar)
* Db2: Support additional CREATE INDEX options [#5827](https://github.com/sqlfluff/sqlfluff/pull/5827) [@keraion](https://github.com/keraion)
* Allow to align all siblings when respacing [#5826](https://github.com/sqlfluff/sqlfluff/pull/5826) [@borchero](https://github.com/borchero)
* BigQuery: Support EXECUTE IMMEDIATE [#5820](https://github.com/sqlfluff/sqlfluff/pull/5820) [@keraion](https://github.com/keraion)
* BigQuery: Support CREATE ROW ACCESS POLICY statement [#5821](https://github.com/sqlfluff/sqlfluff/pull/5821) [@kzosabe](https://github.com/kzosabe)
* Fix Jinja variant location correction [#5814](https://github.com/sqlfluff/sqlfluff/pull/5814) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Test cases for linter fails. [#5815](https://github.com/sqlfluff/sqlfluff/pull/5815) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: Support nested BEGIN, Fix CREATE PROCEDURE OPTIONS [#5816](https://github.com/sqlfluff/sqlfluff/pull/5816) [@keraion](https://github.com/keraion)
* Bring multiple jinja variants through to the parser. [#5794](https://github.com/sqlfluff/sqlfluff/pull/5794) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix placeholder labelling [#5813](https://github.com/sqlfluff/sqlfluff/pull/5813) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Tighten up the return from .process() [#5810](https://github.com/sqlfluff/sqlfluff/pull/5810) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: Support CREATE MATERIALIZED VIEW AS REPLICA OF [#5811](https://github.com/sqlfluff/sqlfluff/pull/5811) [@kzosabe](https://github.com/kzosabe)
* BigQuery: Support OPTIONS in CREATE FUNCTION statement [#5812](https://github.com/sqlfluff/sqlfluff/pull/5812) [@kzosabe](https://github.com/kzosabe)
* TSQL: fix `ALTER TABLE ... SWITCH PARTITION` [#5807](https://github.com/sqlfluff/sqlfluff/pull/5807) [@keen85](https://github.com/keen85)
* SparkSQL: Add functions that use UNIT keywords [#5806](https://github.com/sqlfluff/sqlfluff/pull/5806) [@keraion](https://github.com/keraion)
* CLI: Add `--stdin-filename` option [#5805](https://github.com/sqlfluff/sqlfluff/pull/5805) [@keraion](https://github.com/keraion)
* TSQL: parse `CREATE/ALTER/DROP MASTER KEY` [#5802](https://github.com/sqlfluff/sqlfluff/pull/5802) [@keen85](https://github.com/keen85)
* Jinja Variant Configuration [#5785](https://github.com/sqlfluff/sqlfluff/pull/5785) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Small refactor in jinja templater [#5786](https://github.com/sqlfluff/sqlfluff/pull/5786) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: Support FOR SYSTEM_TIME AS OF in CREATE TABLE CLONE statement [#5798](https://github.com/sqlfluff/sqlfluff/pull/5798) [@kzosabe](https://github.com/kzosabe)
* TSQL: support for `CREATE/ALTER PARTITION FUNCTION/SCHEME` [#5793](https://github.com/sqlfluff/sqlfluff/pull/5793) [@keen85](https://github.com/keen85)
* BigQuery: Support DEFAULT COLLATE segment [#5790](https://github.com/sqlfluff/sqlfluff/pull/5790) [@kzosabe](https://github.com/kzosabe)
* TSQL: support computed columns [#5792](https://github.com/sqlfluff/sqlfluff/pull/5792) [@keen85](https://github.com/keen85)
* Simplify one of the lexer methods [#5788](https://github.com/sqlfluff/sqlfluff/pull/5788) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Improve light colour highlight [#5784](https://github.com/sqlfluff/sqlfluff/pull/5784) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SparkSQL: Support TIMESTAMP_LTZ and TIMESTAMP_NTZ types [#5783](https://github.com/sqlfluff/sqlfluff/pull/5783) [@padraic00](https://github.com/padraic00)

## New Contributors

* [@padraic00](https://github.com/padraic00) made their first contribution in [#5783](https://github.com/sqlfluff/sqlfluff/pull/5783)
* [@burhanyasar](https://github.com/burhanyasar) made their first contribution in [#5830](https://github.com/sqlfluff/sqlfluff/pull/5830)

## [3.0.5] - 2024-04-19

## Highlights

This release contains one larger change, which is a big upgrade to case sensitivity in
the alias use rules. Also allowing the customisation of how SQLFluff uses case sensitivity
in rules like AL05. Beyond that, this also includes a handful of dialect improvements.

Thanks especially to [@olshak](https://github.com/olshak), [@MarkPaulin](https://github.com/MarkPaulin),
[@mhoogendoorn](https://github.com/mhoogendoorn) & [@kawashiro](https://github.com/kawashiro)
who made their first contributions in this release! 🚀

## What’s Changed

* BigQuery: Support CREATE SNAPSHOT TABLE statement [#5779](https://github.com/sqlfluff/sqlfluff/pull/5779) [@kzosabe](https://github.com/kzosabe)
* Upgrades to release actions. [#5774](https://github.com/sqlfluff/sqlfluff/pull/5774) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Improve Snowflake syntax support [#5770](https://github.com/sqlfluff/sqlfluff/pull/5770) [@kawashiro](https://github.com/kawashiro)
* TSQL: allow 'OR ALTER' on 'CREATE TRIGGER' [#5772](https://github.com/sqlfluff/sqlfluff/pull/5772) [@mhoogendoorn](https://github.com/mhoogendoorn)
* Enhancement: Improved Identifiers - casefolding, quoted values, and basic escaping [#5726](https://github.com/sqlfluff/sqlfluff/pull/5726) [@keraion](https://github.com/keraion)
* TSQL: Fix bare functions in default constraints [#5771](https://github.com/sqlfluff/sqlfluff/pull/5771) [@MarkPaulin](https://github.com/MarkPaulin)
* MySQL: Fix parsing 'ALTER TABLE ts ADD COLUMN modified_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP;' (#5766) [#5767](https://github.com/sqlfluff/sqlfluff/pull/5767) [@olshak](https://github.com/olshak)


## New Contributors
* [@olshak](https://github.com/olshak) made their first contribution in [#5767](https://github.com/sqlfluff/sqlfluff/pull/5767)
* [@MarkPaulin](https://github.com/MarkPaulin) made their first contribution in [#5771](https://github.com/sqlfluff/sqlfluff/pull/5771)
* [@mhoogendoorn](https://github.com/mhoogendoorn) made their first contribution in [#5772](https://github.com/sqlfluff/sqlfluff/pull/5772)
* [@kawashiro](https://github.com/kawashiro) made their first contribution in [#5770](https://github.com/sqlfluff/sqlfluff/pull/5770)

## [3.0.4] - 2024-04-07

## Highlights

This is a standard bugfix release bringing a bunch of dialect improvements and
bugfixes. Almost every dialect sees some improvements and it also includes
quality of life improvements to the CLI, pre-commit hooks, docs and several
rules.

Thanks also to the **eight** new contributors whose first contributions are
included in this release. 🎉🎉🏆🎉🎉

## What’s Changed

* TSQL: Move PROPERTY to unreserved [#5759](https://github.com/sqlfluff/sqlfluff/pull/5759) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Mysql: Add Character Set Literals [#5755](https://github.com/sqlfluff/sqlfluff/pull/5755) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Support ASOF Joins [#5756](https://github.com/sqlfluff/sqlfluff/pull/5756) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Mysql: Support scoped function calls [#5757](https://github.com/sqlfluff/sqlfluff/pull/5757) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Support pgvector vector type [#5758](https://github.com/sqlfluff/sqlfluff/pull/5758) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Support RETURNING Clause [#5760](https://github.com/sqlfluff/sqlfluff/pull/5760) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Allow return control structures in atomic functions [#5761](https://github.com/sqlfluff/sqlfluff/pull/5761) [@WittierDinosaur](https://github.com/WittierDinosaur)
* ST04: Retain comments when flattening `CASE` [#5753](https://github.com/sqlfluff/sqlfluff/pull/5753) [@keraion](https://github.com/keraion)
* dbt templater: Raise UserError when using stdin [#5752](https://github.com/sqlfluff/sqlfluff/pull/5752) [@keraion](https://github.com/keraion)
* SQLite: Add `GLOB`, `MATCH`. Improved `REGEXP` [#5745](https://github.com/sqlfluff/sqlfluff/pull/5745) [@keraion](https://github.com/keraion)
* Databricks: Fix Aliases for Join-like objects [#5748](https://github.com/sqlfluff/sqlfluff/pull/5748) [@keraion](https://github.com/keraion)
* Add missing README ref, and issues labels [#5741](https://github.com/sqlfluff/sqlfluff/pull/5741) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Qual: Add pre-commit to CI [#5730](https://github.com/sqlfluff/sqlfluff/pull/5730) [@mdeweerd](https://github.com/mdeweerd)
* Added support for 'greater/less than or equal' on ANSI CASE statement [#5728](https://github.com/sqlfluff/sqlfluff/pull/5728) [@IliyanKostov9](https://github.com/IliyanKostov9)
* Remove `--force` flag from pre-commit hook definition [#5739](https://github.com/sqlfluff/sqlfluff/pull/5739) [@borchero](https://github.com/borchero)
* adding snake_case to CP01 extended_capitalisation_policy [#5736](https://github.com/sqlfluff/sqlfluff/pull/5736) [@alecsgonz](https://github.com/alecsgonz)
* ST04: Ignore simplifying `CASE`s with different expressions [#5735](https://github.com/sqlfluff/sqlfluff/pull/5735) [@keraion](https://github.com/keraion)
* Fix #5724 mysql: Allow Line comments without space after -- [#5731](https://github.com/sqlfluff/sqlfluff/pull/5731) [@mdeweerd](https://github.com/mdeweerd)
* Fix spelling [#5729](https://github.com/sqlfluff/sqlfluff/pull/5729) [@mdeweerd](https://github.com/mdeweerd)
* Fix implementation for view_column_name_list in BigQuery's CREATE VIEW [#5738](https://github.com/sqlfluff/sqlfluff/pull/5738) [@kzosabe](https://github.com/kzosabe)
* CLI: Suppress tracebacks on render/fix/format [#5734](https://github.com/sqlfluff/sqlfluff/pull/5734) [@keraion](https://github.com/keraion)
* Clickhouse: add parsing for select except clause [#5725](https://github.com/sqlfluff/sqlfluff/pull/5725) [@tojahech](https://github.com/tojahech)
* Add array type support to Trino dialect [#5722](https://github.com/sqlfluff/sqlfluff/pull/5722) [@kirkhansen](https://github.com/kirkhansen)
* Fix/snowflake unparsable tag in create stmt [#5720](https://github.com/sqlfluff/sqlfluff/pull/5720) [@mariq41](https://github.com/mariq41)
* Fix/snowflake ext storage [#5714](https://github.com/sqlfluff/sqlfluff/pull/5714) [@mariq41](https://github.com/mariq41)
* Clickhouse: add parsing for "distinct on" syntax [#5716](https://github.com/sqlfluff/sqlfluff/pull/5716) [@tojahech](https://github.com/tojahech)
* added refresh mode init on create table statement [#5715](https://github.com/sqlfluff/sqlfluff/pull/5715) [@IliyanKostov9](https://github.com/IliyanKostov9)
* added `ifNotExistsGrammar` to Snowflake procedure [#5709](https://github.com/sqlfluff/sqlfluff/pull/5709) [@IliyanKostov9](https://github.com/IliyanKostov9)
* Trino: 'TIMESTAMP(p)' no longer triggers LT01 [#5711](https://github.com/sqlfluff/sqlfluff/pull/5711) [@rileymcdowell](https://github.com/rileymcdowell)
* Snowflake: add support for streamlit [#5692](https://github.com/sqlfluff/sqlfluff/pull/5692) [@vgw-chriskruger](https://github.com/vgw-chriskruger)

## New Contributors

* [@vgw-chriskruger](https://github.com/vgw-chriskruger) made their first contribution in [#5692](https://github.com/sqlfluff/sqlfluff/pull/5692)
* [@IliyanKostov9](https://github.com/IliyanKostov9) made their first contribution in [#5709](https://github.com/sqlfluff/sqlfluff/pull/5709)
* [@tojahech](https://github.com/tojahech) made their first contribution in [#5716](https://github.com/sqlfluff/sqlfluff/pull/5716)
* [@mariq41](https://github.com/mariq41) made their first contribution in [#5714](https://github.com/sqlfluff/sqlfluff/pull/5714)
* [@kirkhansen](https://github.com/kirkhansen) made their first contribution in [#5722](https://github.com/sqlfluff/sqlfluff/pull/5722)
* [@kzosabe](https://github.com/kzosabe) made their first contribution in [#5738](https://github.com/sqlfluff/sqlfluff/pull/5738)
* [@mdeweerd](https://github.com/mdeweerd) made their first contribution in [#5729](https://github.com/sqlfluff/sqlfluff/pull/5729)
* [@alecsgonz](https://github.com/alecsgonz) made their first contribution in [#5736](https://github.com/sqlfluff/sqlfluff/pull/5736)

## [3.0.3] - 2024-03-22

## Highlights

This is a standard minor release fixing a set of dialect issues with Trino, BigQuery,
Vertica and Snowflake.

Thanks to [@maegan-canva](https://github.com/maegan-canva),
[@rileymcdowell](https://github.com/rileymcdowell) &
[@paysni](https://github.com/paysni) who made their first contributions in this release.

## What’s Changed

* [TSQL] Create columnstore indexes [#5708](https://github.com/sqlfluff/sqlfluff/pull/5708) [@paysni](https://github.com/paysni)
* [Vertica] fix gaps for some datatypes, complex alias support, fix group by for DDL [#5691](https://github.com/sqlfluff/sqlfluff/pull/5691) [@PolitePp](https://github.com/PolitePp)
* BigQuery: Unreserve KEY keyword [#5703](https://github.com/sqlfluff/sqlfluff/pull/5703) [@greg-finley](https://github.com/greg-finley)
* Trino: Add INTEGER synonym of INT [#5702](https://github.com/sqlfluff/sqlfluff/pull/5702) [@rileymcdowell](https://github.com/rileymcdowell)
* Snowflake shouldn't reserve DO as a keyword. [#5699](https://github.com/sqlfluff/sqlfluff/pull/5699) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow use of STREAM in snowflake CHANGES clause [#5698](https://github.com/sqlfluff/sqlfluff/pull/5698) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Trino: Parse regexp_replace with lambda func [#5683](https://github.com/sqlfluff/sqlfluff/pull/5683) [@rileymcdowell](https://github.com/rileymcdowell)
* Documentation update: Remove reference to alias' default config being "consistent" [#5689](https://github.com/sqlfluff/sqlfluff/pull/5689) [@maegan-canva](https://github.com/maegan-canva)

## New Contributors
* [@maegan-canva](https://github.com/maegan-canva) made their first contribution in [#5689](https://github.com/sqlfluff/sqlfluff/pull/5689)
* [@rileymcdowell](https://github.com/rileymcdowell) made their first contribution in [#5683](https://github.com/sqlfluff/sqlfluff/pull/5683)
* [@paysni](https://github.com/paysni) made their first contribution in [#5708](https://github.com/sqlfluff/sqlfluff/pull/5708)

## [3.0.2] - 2024-03-17

## Highlights

This is primarily another hotfix release for 3.0.0. Specifically making sure the
deprecation warnings for `-f/--force` go to `stderr` rather than `stdout`. It also
includes two dialect improvements, one for Snowflake and one for T-SQL.

## What’s Changed

* Snowflake: Support External Volumes [#5684](https://github.com/sqlfluff/sqlfluff/pull/5684) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL: Support Reconfigure [#5685](https://github.com/sqlfluff/sqlfluff/pull/5685) [@WittierDinosaur](https://github.com/WittierDinosaur)
* CLI: Make `--force` deprecation print on stderr [#5681](https://github.com/sqlfluff/sqlfluff/pull/5681) [@keraion](https://github.com/keraion)

## [3.0.1] - 2024-03-13

## Highlights

This minor release is a hotfix to resolve a bug introduced affecting CLI exit codes
in the 3.0.0 release.

## What’s Changed

* Fix 5673 [#5676](https://github.com/sqlfluff/sqlfluff/pull/5676) [@alanmcruickshank](https://github.com/alanmcruickshank)

## [3.0.0] - 2024-03-12

## Highlights

This release brings several breaking changes to previous releases. Most notably:

* It drops support for python 3.7, which reached end of life in June 2023.

* It migrates to `pyproject.toml` rather than `setup.cfg` as the python
  packaging configuration file (although keeping `setuptools` as the default backend).

* The serialised output for `sqlfluff lint` (and the corresponding API methods)
  now contains more information about the span of linting issues, initial
  proposed fixes and several statistics which were previously only accessible via
  csv export. Beside the *new* fields, the original fields of `line_pos` and
  `line_no` have been renamed to `start_line_pos` and `start_line_no`, to
  distinguish them from the new fields starting `end_*`.

* The default `annotation_level` set by the `--annotation-level`
  option on the `sqlfluff lint` command has been changed from `notice`
  to `warning`, to better distinguish linting errors from warnings, which
  always now have the level of `notice`. This is only relevant when using
  the `github-annotation` or `github-annotation-native` formats.

* A change in the default behaviour for `convention.not_equals`. The new default
  is to be `consistent`, which is slightly more relaxed than the original
  behaviour.

* The `--force` option has been deprecated on `sqlfluff fix` as that option is
  now the default behaviour. This is to enable significant reductions in memory
  overhead when linting large projects.

* The long since deprecated `--disable_progress_bar` option has been removed
  (which was replaced by the kabab-case `--disable-progress-bar` more than a
  year ago).

* Plugins are now loaded progressively, and with error handling. If a plugin
  fails to load, SQLFluff will now continue onward and try to run regardless
  while also showing a more helpful error message.

On top of these changes, there have a been a whole host of dialect improvements
and additions, in particular the inclusion of a`vertica` dialect for the
first time. There's also:

* A new rule (`aliasing.self_alias.column`) which prevents aliasing a column as itself.

* A change to disables AL01 (`aliasing.table`) by default for Oracle.

* A change to allow AL05 to allow aliasing for a `VALUES` clause.

For more specifics please take a look at the
[release notes](https://docs.sqlfluff.com/en/latest/releasenotes.html).

Thanks to the community for patience during the release cycle for 3.0.0, which
has taken a little longer than expected. Thanks also to the **TWENTY SEVEN** new
contributors whose changes are included in this release. 🎉🎉🏆🎉🎉

## What’s Changed

* Progressively load plugins [#5661](https://github.com/sqlfluff/sqlfluff/pull/5661) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: AL05, ignore aliases in values clause [#5669](https://github.com/sqlfluff/sqlfluff/pull/5669) [@keraion](https://github.com/keraion)
* Add Postgres CREATE FOREIGN TABLE statement [#5657](https://github.com/sqlfluff/sqlfluff/pull/5657) [@edpft](https://github.com/edpft)
* Lexer: Handle escaped curly brace slices from the python templater [#5666](https://github.com/sqlfluff/sqlfluff/pull/5666) [@keraion](https://github.com/keraion)
* [CI]: Update pre-commit hook versions [#5665](https://github.com/sqlfluff/sqlfluff/pull/5665) [@keraion](https://github.com/keraion)
* Resolves #5624: Snowflake unparsable unset table options [#5664](https://github.com/sqlfluff/sqlfluff/pull/5664) [@andychannery](https://github.com/andychannery)
* Revert Ruff Changes [#5662](https://github.com/sqlfluff/sqlfluff/pull/5662) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Complete the memory overhead work on cli fix [#5653](https://github.com/sqlfluff/sqlfluff/pull/5653) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #5647: Snowflake unparsable variant access after cast [#5658](https://github.com/sqlfluff/sqlfluff/pull/5658) [@andychannery](https://github.com/andychannery)
* BQ PK and FK [#5654](https://github.com/sqlfluff/sqlfluff/pull/5654) [@OTooleMichael](https://github.com/OTooleMichael)
* Prep version 3.0.0a6 [#5652](https://github.com/sqlfluff/sqlfluff/pull/5652) [@github-actions](https://github.com/github-actions)
* Add Support for Databricks `CREATE FUNCTION` Syntax in SparkSQL Parser [#5615](https://github.com/sqlfluff/sqlfluff/pull/5615) [@mitchellvanrijkom](https://github.com/mitchellvanrijkom)
* Swap fix `--force` for `--check` [#5650](https://github.com/sqlfluff/sqlfluff/pull/5650) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove `DeprecatedOption` [#5649](https://github.com/sqlfluff/sqlfluff/pull/5649) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve broken loop limit test [#5651](https://github.com/sqlfluff/sqlfluff/pull/5651) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Move NOTIFY to non-reserved words [#5645](https://github.com/sqlfluff/sqlfluff/pull/5645) [@greg-finley](https://github.com/greg-finley)
* BigQuery: GROUP BY ALL [#5646](https://github.com/sqlfluff/sqlfluff/pull/5646) [@greg-finley](https://github.com/greg-finley)
* chore: use pre-calculated `_code_indices` in `BaseSegment::raw_segmen… [#5644](https://github.com/sqlfluff/sqlfluff/pull/5644) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Fix Snowflake Semistructured identifier parsing regex-expression [#5635](https://github.com/sqlfluff/sqlfluff/pull/5635) [@DannyMor](https://github.com/DannyMor)
* Postgres: Update ReferentialActionGrammar to support sets of columns [#5628](https://github.com/sqlfluff/sqlfluff/pull/5628) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add syntax for masking policy force [#5629](https://github.com/sqlfluff/sqlfluff/pull/5629) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Allow nested block comments [#5630](https://github.com/sqlfluff/sqlfluff/pull/5630) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Add Create, Alter, Drop Statistics [#5631](https://github.com/sqlfluff/sqlfluff/pull/5631) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL Fix relative sql filepath lexer [#5632](https://github.com/sqlfluff/sqlfluff/pull/5632) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Tech Debt: Replace some sequences with their Ref equivalents [#5633](https://github.com/sqlfluff/sqlfluff/pull/5633) [@WittierDinosaur](https://github.com/WittierDinosaur)
* ANSI/MYSQL: Support Create Role If Not Exists [#5634](https://github.com/sqlfluff/sqlfluff/pull/5634) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add Vertica dialect [#5640](https://github.com/sqlfluff/sqlfluff/pull/5640) [@PolitePp](https://github.com/PolitePp)
* Add Support for Snowflake Materialised View and Column Masking Policy [#5637](https://github.com/sqlfluff/sqlfluff/pull/5637) [@ulixius9](https://github.com/ulixius9)
* [snowflake dialect] support ALTER TABLE ... ADD COLUMN IF NOT EXISTS [#5621](https://github.com/sqlfluff/sqlfluff/pull/5621) [@gshen7](https://github.com/gshen7)
* SQLite: Make `DISTINCT FROM` optional; SQLite/TSQL/Exasol: Nothing'd `NanLiteralSegment` [#5620](https://github.com/sqlfluff/sqlfluff/pull/5620) [@keraion](https://github.com/keraion)
* Upgrade greenplum dialect [#5546](https://github.com/sqlfluff/sqlfluff/pull/5546) [@kkozhakin](https://github.com/kkozhakin)
* Oracle: parse length qualifier in types [#5613](https://github.com/sqlfluff/sqlfluff/pull/5613) [@Jefffrey](https://github.com/Jefffrey)
* Multiple Dialects: Fix handling of nested sets expressions [#5606](https://github.com/sqlfluff/sqlfluff/pull/5606) [@keraion](https://github.com/keraion)
* DB2: Add labeled durations and special registers [#5612](https://github.com/sqlfluff/sqlfluff/pull/5612) [@keraion](https://github.com/keraion)
* Sparksql: Fix `LATERAL VIEW` following `JOIN`; `CLUSTER|SORT|DISTRIBUTE BY` or `QUALIFY` without `FROM` [#5602](https://github.com/sqlfluff/sqlfluff/pull/5602) [@keraion](https://github.com/keraion)
* File helpers and config test parameterisation. [#5579](https://github.com/sqlfluff/sqlfluff/pull/5579) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Memory overhead optimisations during linting [#5585](https://github.com/sqlfluff/sqlfluff/pull/5585) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix: multiple columns foreign key constraint (#5592) [#5594](https://github.com/sqlfluff/sqlfluff/pull/5594) [@maoxingda](https://github.com/maoxingda)
* [CI] Add `no_implicit_reexport` mypy check [#5509](https://github.com/sqlfluff/sqlfluff/pull/5509) [@Koyaani](https://github.com/Koyaani)
* Prep version 3.0.0a5 [#5512](https://github.com/sqlfluff/sqlfluff/pull/5512) [@github-actions](https://github.com/github-actions)
* Add support & test for postgres alter policy with multiple clauses [#5577](https://github.com/sqlfluff/sqlfluff/pull/5577) [@fnimick](https://github.com/fnimick)
* Update github actions to latest versions [#5584](https://github.com/sqlfluff/sqlfluff/pull/5584) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allows using dbt cross project ref in jinja templater [#5574](https://github.com/sqlfluff/sqlfluff/pull/5574) [@alangner](https://github.com/alangner)
* Improve support for Jinja templater plugins with custom tags [#5543](https://github.com/sqlfluff/sqlfluff/pull/5543) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Databricks: fix `EXCEPT` with qualified column reference [#5557](https://github.com/sqlfluff/sqlfluff/pull/5557) [@keraion](https://github.com/keraion)
* Stricter recommended config for not_equals convention [#5580](https://github.com/sqlfluff/sqlfluff/pull/5580) [@alanmcruickshank](https://github.com/alanmcruickshank)
* CV01: Add options for ANSI and consistent style. [#5539](https://github.com/sqlfluff/sqlfluff/pull/5539) [@keraion](https://github.com/keraion)
* DuckDB: Fix `REPLACE` after `EXCLUDE`. Fix AL03 linting for wildcard like expression. [#5556](https://github.com/sqlfluff/sqlfluff/pull/5556) [@keraion](https://github.com/keraion)
* Clickhouse: Add `GLOBAL JOIN`, `GLOBAL IN`, and `PASTE JOIN` [#5560](https://github.com/sqlfluff/sqlfluff/pull/5560) [@keraion](https://github.com/keraion)
* [Docs] Use extended policy for identifier capitalisation in starter config [#5562](https://github.com/sqlfluff/sqlfluff/pull/5562) [@j-svensmark](https://github.com/j-svensmark)
* Build: linting black 24.1.0 rules update [#5573](https://github.com/sqlfluff/sqlfluff/pull/5573) [@keraion](https://github.com/keraion)
* Snowflake: Updating Snowflake dialect to pass acceptable RLS policy objects [#5559](https://github.com/sqlfluff/sqlfluff/pull/5559) [@k1drobot](https://github.com/k1drobot)
* Redshift Syntax: ALTER APPEND [#5545](https://github.com/sqlfluff/sqlfluff/pull/5545) [@OTooleMichael](https://github.com/OTooleMichael)
* DuckDB: Add ANTI, SEMI, ASOF, and POSITIONAL joins [#5544](https://github.com/sqlfluff/sqlfluff/pull/5544) [@keraion](https://github.com/keraion)
* MySQL: fix FIRST keyword in ALTER ADD/MODIFY [#5537](https://github.com/sqlfluff/sqlfluff/pull/5537) [@archer62](https://github.com/archer62)
* Postgres/DB2/Oracle: Fix comma join `LATERAL`. [#5533](https://github.com/sqlfluff/sqlfluff/pull/5533) [@keraion](https://github.com/keraion)
* Add new Rule AL09: Avoid Self Alias [#5528](https://github.com/sqlfluff/sqlfluff/pull/5528) [@aayushr7](https://github.com/aayushr7)
* Rule AL01: disabled for Oracle dialect [#5517](https://github.com/sqlfluff/sqlfluff/pull/5517) [@keraion](https://github.com/keraion)
* Postgres ALTER EXTENSION support: dialect & tests [#5527](https://github.com/sqlfluff/sqlfluff/pull/5527) [@remy-gohiring](https://github.com/remy-gohiring)
* SparkSQL: Add `UNPIVOT` syntax. Fix `TABLESAMPLE` aliases. [#5524](https://github.com/sqlfluff/sqlfluff/pull/5524) [@keraion](https://github.com/keraion)
* DuckDB: Added support for `PIVOT` and `UNPIVOT` [#5514](https://github.com/sqlfluff/sqlfluff/pull/5514) [@keraion](https://github.com/keraion)
* Fix parse error databricks window function starts with order by [#5493](https://github.com/sqlfluff/sqlfluff/pull/5493) [@snkekorfus](https://github.com/snkekorfus)
* Hive: allow UDTF to return multiple column aliases in SELECT [#5495](https://github.com/sqlfluff/sqlfluff/pull/5495) [@reata](https://github.com/reata)
* DB2: Add support for `DECLARE GLOBAL TEMPORARY TABLES`, `OFFSET`, `CALL`, and non-bracketed `VALUES` [#5508](https://github.com/sqlfluff/sqlfluff/pull/5508) [@keraion](https://github.com/keraion)
* DuckDB: Add CREATE OR REPLACE TABLE syntax [#5511](https://github.com/sqlfluff/sqlfluff/pull/5511) [@keraion](https://github.com/keraion)
* TSQL: Top and Distinct in same query [#5491](https://github.com/sqlfluff/sqlfluff/pull/5491) [@greg-finley](https://github.com/greg-finley)
* [Spark/Databricks] Fix: make COLUMNS in APPLY CHANGES INTO optional [#5498](https://github.com/sqlfluff/sqlfluff/pull/5498) [@rocwang](https://github.com/rocwang)
* SparkSQL: exclamation mark as logical not [#5500](https://github.com/sqlfluff/sqlfluff/pull/5500) [@reata](https://github.com/reata)
* SparkSQL: allow value in set_statement to be Java class name [#5504](https://github.com/sqlfluff/sqlfluff/pull/5504) [@reata](https://github.com/reata)
* SparkSQL: allow distribute/sort/cluster by at end of set operation [#5502](https://github.com/sqlfluff/sqlfluff/pull/5502) [@reata](https://github.com/reata)
* [CI] Add a few more mypy checks [#5505](https://github.com/sqlfluff/sqlfluff/pull/5505) [@Koyaani](https://github.com/Koyaani)
* Snowflake dialect: Add support for DATABASE ROLE in GRANT/REVOKE [#5490](https://github.com/sqlfluff/sqlfluff/pull/5490) [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta)
* DuckDB: Qualify and From-First [#5485](https://github.com/sqlfluff/sqlfluff/pull/5485) [@keraion](https://github.com/keraion)
* MySql: create table: allow null/not null in any position [#5473](https://github.com/sqlfluff/sqlfluff/pull/5473) [@archer62](https://github.com/archer62)
* Snowflake dialect: Support for CREATE DATABASE ROLE [#5475](https://github.com/sqlfluff/sqlfluff/pull/5475) [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta)
* Clickhouse Dialect - Support BackQuoted Identifiers [#5457](https://github.com/sqlfluff/sqlfluff/pull/5457) [@kaiyannameighu](https://github.com/kaiyannameighu)
* Change Color.lightgrey to have a white background - dark theme friendly [#5458](https://github.com/sqlfluff/sqlfluff/pull/5458) [@ryaminal](https://github.com/ryaminal)
* Fix indentation for single cube clause [#5462](https://github.com/sqlfluff/sqlfluff/pull/5462) [@tunetheweb](https://github.com/tunetheweb)
* Prep version 3.0.0a4 [#5455](https://github.com/sqlfluff/sqlfluff/pull/5455) [@github-actions](https://github.com/github-actions)
* Build out rule and fix serialisation [#5364](https://github.com/sqlfluff/sqlfluff/pull/5364) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add warning about github actions annotations limit [#5450](https://github.com/sqlfluff/sqlfluff/pull/5450) [@alanmcruickshank](https://github.com/alanmcruickshank)
* chore: remove unused line initialization in ParseContext [#5448](https://github.com/sqlfluff/sqlfluff/pull/5448) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Refine CLI testing fixture [#5446](https://github.com/sqlfluff/sqlfluff/pull/5446) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update black linting [#5447](https://github.com/sqlfluff/sqlfluff/pull/5447) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prep version 3.0.0a3 [#5444](https://github.com/sqlfluff/sqlfluff/pull/5444) [@github-actions](https://github.com/github-actions)
* fix assertion in `test__api__lint_string_specific_exclude_single` [#5437](https://github.com/sqlfluff/sqlfluff/pull/5437) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Databricks CLUSTER BY and OPTIMIZE [#5436](https://github.com/sqlfluff/sqlfluff/pull/5436) [@greg-finley](https://github.com/greg-finley)
* TSQL: ON DELETE NO ACTION [#5434](https://github.com/sqlfluff/sqlfluff/pull/5434) [@greg-finley](https://github.com/greg-finley)
* Snowflake dynamic table [#5435](https://github.com/sqlfluff/sqlfluff/pull/5435) [@greg-finley](https://github.com/greg-finley)
* Support parsing CONSTRAINT definitions when creating Delta Live Tables in SparkSQL/Databricks [#5438](https://github.com/sqlfluff/sqlfluff/pull/5438) [@rocwang](https://github.com/rocwang)
* adds few fixes for databricks/sparksql [#5431](https://github.com/sqlfluff/sqlfluff/pull/5431) [@markbaas](https://github.com/markbaas)
* TSQL: CREATE USER {FOR|FROM} LOGIN [#5426](https://github.com/sqlfluff/sqlfluff/pull/5426) [@greg-finley](https://github.com/greg-finley)
* Snowflake Create table order/noorder [#5421](https://github.com/sqlfluff/sqlfluff/pull/5421) [@greg-finley](https://github.com/greg-finley)
* Simplify Snowflake regexes [#5419](https://github.com/sqlfluff/sqlfluff/pull/5419) [@greg-finley](https://github.com/greg-finley)
* Permit .* after each tbl_name in multi-table delete syntax [#5408](https://github.com/sqlfluff/sqlfluff/pull/5408) [@yoichi](https://github.com/yoichi)
* Fix snowflake add search optimization grant [#5412](https://github.com/sqlfluff/sqlfluff/pull/5412) [@jongracecox](https://github.com/jongracecox)
* ANSI: Allow combination of UNION clause and WITH clause [#5413](https://github.com/sqlfluff/sqlfluff/pull/5413) [@yoichi](https://github.com/yoichi)
* SQLite: Allow block comments to be terminated by end of input [#5400](https://github.com/sqlfluff/sqlfluff/pull/5400) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Update publish github action to use kebab case [#5392](https://github.com/sqlfluff/sqlfluff/pull/5392) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prep version 3.0.0a2 [#5391](https://github.com/sqlfluff/sqlfluff/pull/5391) [@github-actions](https://github.com/github-actions)
* Update publish actions and Dockerfile. [#5390](https://github.com/sqlfluff/sqlfluff/pull/5390) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prep version 3.0.0a1 [#5381](https://github.com/sqlfluff/sqlfluff/pull/5381) [@github-actions](https://github.com/github-actions)
* Move the rest of pytest over to `pyproject.toml` [#5383](https://github.com/sqlfluff/sqlfluff/pull/5383) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Move doc8 over to pyproject [#5385](https://github.com/sqlfluff/sqlfluff/pull/5385) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove exceptions for typing stubs that now exist. [#5382](https://github.com/sqlfluff/sqlfluff/pull/5382) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Migrate to `pyproject.toml` for the core project. [#5373](https://github.com/sqlfluff/sqlfluff/pull/5373) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix the snippet from a pyproject.toml in configuration.rst [#5378](https://github.com/sqlfluff/sqlfluff/pull/5378) [@ishiis](https://github.com/ishiis)
* Snowflake: Support AlterNetworkPolicy Statements [#5377](https://github.com/sqlfluff/sqlfluff/pull/5377) [@WittierDinosaur](https://github.com/WittierDinosaur)
* postgres: add support for bodies of "language sql" functions [#5376](https://github.com/sqlfluff/sqlfluff/pull/5376) [@65278](https://github.com/65278)
* Add support for SET NAMES statement in MySQL [#5374](https://github.com/sqlfluff/sqlfluff/pull/5374) [@joaostorrer](https://github.com/joaostorrer)
* Fix GRANT ALL PRIVILEGES statement in MySQL [#5375](https://github.com/sqlfluff/sqlfluff/pull/5375) [@joaostorrer](https://github.com/joaostorrer)
* Another extraction of fixing logic. [#5365](https://github.com/sqlfluff/sqlfluff/pull/5365) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove root requirements.txt [#5372](https://github.com/sqlfluff/sqlfluff/pull/5372) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Drop support of python 3.7 [#5288](https://github.com/sqlfluff/sqlfluff/pull/5288) [@zhongjiajie](https://github.com/zhongjiajie)
* API configuration documentation [#5369](https://github.com/sqlfluff/sqlfluff/pull/5369) [@golergka](https://github.com/golergka)
* add listagg extras support in trino dialect [#5368](https://github.com/sqlfluff/sqlfluff/pull/5368) [@wjhrdy](https://github.com/wjhrdy)
* Allow ignoring of comments from indentation entirely #3311 [#5363](https://github.com/sqlfluff/sqlfluff/pull/5363) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Trino: Support Analyze statements [#5361](https://github.com/sqlfluff/sqlfluff/pull/5361) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Resolve #5327 (logging to stdout) [#5362](https://github.com/sqlfluff/sqlfluff/pull/5362) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@edpft](https://github.com/edpft) made their first contribution in [#5657](https://github.com/sqlfluff/sqlfluff/pull/5657)
* [@maoxingda](https://github.com/maoxingda) made their first contribution in [#5594](https://github.com/sqlfluff/sqlfluff/pull/5594)
* [@Jefffrey](https://github.com/Jefffrey) made their first contribution in [#5613](https://github.com/sqlfluff/sqlfluff/pull/5613)
* [@kkozhakin](https://github.com/kkozhakin) made their first contribution in [#5546](https://github.com/sqlfluff/sqlfluff/pull/5546)
* [@gshen7](https://github.com/gshen7) made their first contribution in [#5621](https://github.com/sqlfluff/sqlfluff/pull/5621)
* [@PolitePp](https://github.com/PolitePp) made their first contribution in [#5640](https://github.com/sqlfluff/sqlfluff/pull/5640)
* [@DannyMor](https://github.com/DannyMor) made their first contribution in [#5635](https://github.com/sqlfluff/sqlfluff/pull/5635)
* [@mitchellvanrijkom](https://github.com/mitchellvanrijkom) made their first contribution in [#5615](https://github.com/sqlfluff/sqlfluff/pull/5615)
* [@ryaminal](https://github.com/ryaminal) made their first contribution in [#5458](https://github.com/sqlfluff/sqlfluff/pull/5458)
* [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta) made their first contribution in [#5475](https://github.com/sqlfluff/sqlfluff/pull/5475)
* [@archer62](https://github.com/archer62) made their first contribution in [#5473](https://github.com/sqlfluff/sqlfluff/pull/5473)
* [@keraion](https://github.com/keraion) made their first contribution in [#5485](https://github.com/sqlfluff/sqlfluff/pull/5485)
* [@Koyaani](https://github.com/Koyaani) made their first contribution in [#5505](https://github.com/sqlfluff/sqlfluff/pull/5505)
* [@snkekorfus](https://github.com/snkekorfus) made their first contribution in [#5493](https://github.com/sqlfluff/sqlfluff/pull/5493)
* [@remy-gohiring](https://github.com/remy-gohiring) made their first contribution in [#5527](https://github.com/sqlfluff/sqlfluff/pull/5527)
* [@aayushr7](https://github.com/aayushr7) made their first contribution in [#5528](https://github.com/sqlfluff/sqlfluff/pull/5528)
* [@k1drobot](https://github.com/k1drobot) made their first contribution in [#5559](https://github.com/sqlfluff/sqlfluff/pull/5559)
* [@alangner](https://github.com/alangner) made their first contribution in [#5574](https://github.com/sqlfluff/sqlfluff/pull/5574)
* [@fnimick](https://github.com/fnimick) made their first contribution in [#5577](https://github.com/sqlfluff/sqlfluff/pull/5577)
* [@jongracecox](https://github.com/jongracecox) made their first contribution in [#5412](https://github.com/sqlfluff/sqlfluff/pull/5412)
* [@markbaas](https://github.com/markbaas) made their first contribution in [#5431](https://github.com/sqlfluff/sqlfluff/pull/5431)
* [@rocwang](https://github.com/rocwang) made their first contribution in [#5438](https://github.com/sqlfluff/sqlfluff/pull/5438)
* [@gvozdvmozgu](https://github.com/gvozdvmozgu) made their first contribution in [#5437](https://github.com/sqlfluff/sqlfluff/pull/5437)
* [@wjhrdy](https://github.com/wjhrdy) made their first contribution in [#5368](https://github.com/sqlfluff/sqlfluff/pull/5368)
* [@golergka](https://github.com/golergka) made their first contribution in [#5369](https://github.com/sqlfluff/sqlfluff/pull/5369)
* [@65278](https://github.com/65278) made their first contribution in [#5376](https://github.com/sqlfluff/sqlfluff/pull/5376)
* [@ishiis](https://github.com/ishiis) made their first contribution in [#5378](https://github.com/sqlfluff/sqlfluff/pull/5378)

## [3.0.0a6] - 2024-03-05

## Highlights

This introduces some memory optimisations in the linting operation which
prevent a major cause of crashes when linting large projects. As part of that
we've also deprecated the `--force` option on `sqlfluff fix` and made that
the default behaviour (the associated memory optimisations will come shortly).

This also removes the long since deprecated `--disable_progress_bar` option
(which was replaced by the kabab-case `--disable-progress-bar` more than a
year ago).

On top of that this release also introduces the `vertica` dialect for the
first time, and a whole host of bugfixes and improvements to other dialects.

This release should be considered a release candidate for the final `3.0.0`
release which will follow shortly in the next few days unless any other
major issues are found.

Thanks particularly to the **seven** new contributors we saw in this release 🏆🎉.

## What’s Changed

* Add Support for Databricks `CREATE FUNCTION` Syntax in SparkSQL Parser [#5615](https://github.com/sqlfluff/sqlfluff/pull/5615) [@mitchellvanrijkom](https://github.com/mitchellvanrijkom)
* Swap fix `--force` for `--check` [#5650](https://github.com/sqlfluff/sqlfluff/pull/5650) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove `DeprecatedOption` [#5649](https://github.com/sqlfluff/sqlfluff/pull/5649) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve broken loop limit test [#5651](https://github.com/sqlfluff/sqlfluff/pull/5651) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Move NOTIFY to non-reserved words [#5645](https://github.com/sqlfluff/sqlfluff/pull/5645) [@greg-finley](https://github.com/greg-finley)
* BigQuery: GROUP BY ALL [#5646](https://github.com/sqlfluff/sqlfluff/pull/5646) [@greg-finley](https://github.com/greg-finley)
* chore: use pre-calculated `_code_indices` in `BaseSegment::raw_segmen… [#5644](https://github.com/sqlfluff/sqlfluff/pull/5644) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Fix Snowflake Semistructured identifier parsing regex-expression [#5635](https://github.com/sqlfluff/sqlfluff/pull/5635) [@DannyMor](https://github.com/DannyMor)
* Postgres: Update ReferentialActionGrammar to support sets of columns [#5628](https://github.com/sqlfluff/sqlfluff/pull/5628) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add syntax for masking policy force [#5629](https://github.com/sqlfluff/sqlfluff/pull/5629) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Allow nested block comments [#5630](https://github.com/sqlfluff/sqlfluff/pull/5630) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Add Create, Alter, Drop Statistics [#5631](https://github.com/sqlfluff/sqlfluff/pull/5631) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL Fix relative sql filepath lexer [#5632](https://github.com/sqlfluff/sqlfluff/pull/5632) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Tech Debt: Replace some sequences with their Ref equivalents [#5633](https://github.com/sqlfluff/sqlfluff/pull/5633) [@WittierDinosaur](https://github.com/WittierDinosaur)
* ANSI/MYSQL: Support Create Role If Not Exists [#5634](https://github.com/sqlfluff/sqlfluff/pull/5634) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add Vertica dialect [#5640](https://github.com/sqlfluff/sqlfluff/pull/5640) [@PolitePp](https://github.com/PolitePp)
* Add Support for Snowflake Materialised View and Column Masking Policy [#5637](https://github.com/sqlfluff/sqlfluff/pull/5637) [@ulixius9](https://github.com/ulixius9)
* [snowflake dialect] support ALTER TABLE ... ADD COLUMN IF NOT EXISTS [#5621](https://github.com/sqlfluff/sqlfluff/pull/5621) [@gshen7](https://github.com/gshen7)
* SQLite: Make `DISTINCT FROM` optional; SQLite/TSQL/Exasol: Nothing'd `NanLiteralSegment` [#5620](https://github.com/sqlfluff/sqlfluff/pull/5620) [@keraion](https://github.com/keraion)
* Upgrade greenplum dialect [#5546](https://github.com/sqlfluff/sqlfluff/pull/5546) [@kkozhakin](https://github.com/kkozhakin)
* Oracle: parse length qualifier in types [#5613](https://github.com/sqlfluff/sqlfluff/pull/5613) [@Jefffrey](https://github.com/Jefffrey)
* Multiple Dialects: Fix handling of nested sets expressions [#5606](https://github.com/sqlfluff/sqlfluff/pull/5606) [@keraion](https://github.com/keraion)
* DB2: Add labeled durations and special registers [#5612](https://github.com/sqlfluff/sqlfluff/pull/5612) [@keraion](https://github.com/keraion)
* Sparksql: Fix `LATERAL VIEW` following `JOIN`; `CLUSTER|SORT|DISTRIBUTE BY` or `QUALIFY` without `FROM` [#5602](https://github.com/sqlfluff/sqlfluff/pull/5602) [@keraion](https://github.com/keraion)
* File helpers and config test parameterisation. [#5579](https://github.com/sqlfluff/sqlfluff/pull/5579) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Memory overhead optimisations during linting [#5585](https://github.com/sqlfluff/sqlfluff/pull/5585) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix: multiple columns foreign key constraint (#5592) [#5594](https://github.com/sqlfluff/sqlfluff/pull/5594) [@maoxingda](https://github.com/maoxingda)
* [CI] Add `no_implicit_reexport` mypy check [#5509](https://github.com/sqlfluff/sqlfluff/pull/5509) [@Koyaani](https://github.com/Koyaani)

## New Contributors
* [@maoxingda](https://github.com/maoxingda) made their first contribution in [#5594](https://github.com/sqlfluff/sqlfluff/pull/5594)
* [@Jefffrey](https://github.com/Jefffrey) made their first contribution in [#5613](https://github.com/sqlfluff/sqlfluff/pull/5613)
* [@kkozhakin](https://github.com/kkozhakin) made their first contribution in [#5546](https://github.com/sqlfluff/sqlfluff/pull/5546)
* [@gshen7](https://github.com/gshen7) made their first contribution in [#5621](https://github.com/sqlfluff/sqlfluff/pull/5621)
* [@PolitePp](https://github.com/PolitePp) made their first contribution in [#5640](https://github.com/sqlfluff/sqlfluff/pull/5640)
* [@DannyMor](https://github.com/DannyMor) made their first contribution in [#5635](https://github.com/sqlfluff/sqlfluff/pull/5635)
* [@mitchellvanrijkom](https://github.com/mitchellvanrijkom) made their first contribution in [#5615](https://github.com/sqlfluff/sqlfluff/pull/5615)

## [3.0.0a5] - 2024-01-30

## Highlights

This release primarily brings through a large set of dialect improvements and
bugfixes from over the holiday period. Notably also:

* A change in the default behaviour for `convention.not_equals`. The new default
  is to be `consistent`, which is slightly more relaxed than the original
  behaviour.
* A new rule (`aliasing.self_alias.column`) which prevents aliasing a column
  as itself.
* Disables `AL01` (`aliasing.table`) by default for Oracle.

This release also saw **ELEVEN** new contributors in this release 🎉🎉🏆🏆🎉🎉.
Great to see so many new people getting involved with the project. Thank You 🙏.

## What’s Changed

* Add support & test for postgres alter policy with multiple clauses [#5577](https://github.com/sqlfluff/sqlfluff/pull/5577) [@fnimick](https://github.com/fnimick)
* Update github actions to latest versions [#5584](https://github.com/sqlfluff/sqlfluff/pull/5584) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allows using dbt cross project ref in jinja templater [#5574](https://github.com/sqlfluff/sqlfluff/pull/5574) [@alangner](https://github.com/alangner)
* Improve support for Jinja templater plugins with custom tags [#5543](https://github.com/sqlfluff/sqlfluff/pull/5543) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Databricks: fix `EXCEPT` with qualified column reference [#5557](https://github.com/sqlfluff/sqlfluff/pull/5557) [@keraion](https://github.com/keraion)
* Stricter recommended config for not_equals convention [#5580](https://github.com/sqlfluff/sqlfluff/pull/5580) [@alanmcruickshank](https://github.com/alanmcruickshank)
* CV01: Add options for ANSI and consistent style. [#5539](https://github.com/sqlfluff/sqlfluff/pull/5539) [@keraion](https://github.com/keraion)
* DuckDB: Fix `REPLACE` after `EXCLUDE`. Fix AL03 linting for wildcard like expression. [#5556](https://github.com/sqlfluff/sqlfluff/pull/5556) [@keraion](https://github.com/keraion)
* Clickhouse: Add `GLOBAL JOIN`, `GLOBAL IN`, and `PASTE JOIN` [#5560](https://github.com/sqlfluff/sqlfluff/pull/5560) [@keraion](https://github.com/keraion)
* [Docs] Use extended policy for identifier capitalisation in starter config [#5562](https://github.com/sqlfluff/sqlfluff/pull/5562) [@j-svensmark](https://github.com/j-svensmark)
* Build: linting black 24.1.0 rules update [#5573](https://github.com/sqlfluff/sqlfluff/pull/5573) [@keraion](https://github.com/keraion)
* Snowflake: Updating Snowflake dialect to pass acceptable RLS policy objects [#5559](https://github.com/sqlfluff/sqlfluff/pull/5559) [@k1drobot](https://github.com/k1drobot)
* Redshift Syntax: ALTER APPEND [#5545](https://github.com/sqlfluff/sqlfluff/pull/5545) [@OTooleMichael](https://github.com/OTooleMichael)
* DuckDB: Add ANTI, SEMI, ASOF, and POSITIONAL joins [#5544](https://github.com/sqlfluff/sqlfluff/pull/5544) [@keraion](https://github.com/keraion)
* MySQL: fix FIRST keyword in ALTER ADD/MODIFY [#5537](https://github.com/sqlfluff/sqlfluff/pull/5537) [@archer62](https://github.com/archer62)
* Postgres/DB2/Oracle: Fix comma join `LATERAL`. [#5533](https://github.com/sqlfluff/sqlfluff/pull/5533) [@keraion](https://github.com/keraion)
* Add new Rule AL09: Avoid Self Alias [#5528](https://github.com/sqlfluff/sqlfluff/pull/5528) [@aayushr7](https://github.com/aayushr7)
* Rule AL01: disabled for Oracle dialect [#5517](https://github.com/sqlfluff/sqlfluff/pull/5517) [@keraion](https://github.com/keraion)
* Postgres ALTER EXTENSION support: dialect & tests [#5527](https://github.com/sqlfluff/sqlfluff/pull/5527) [@remy-gohiring](https://github.com/remy-gohiring)
* SparkSQL: Add `UNPIVOT` syntax. Fix `TABLESAMPLE` aliases. [#5524](https://github.com/sqlfluff/sqlfluff/pull/5524) [@keraion](https://github.com/keraion)
* DuckDB: Added support for `PIVOT` and `UNPIVOT` [#5514](https://github.com/sqlfluff/sqlfluff/pull/5514) [@keraion](https://github.com/keraion)
* Fix parse error databricks window function starts with order by [#5493](https://github.com/sqlfluff/sqlfluff/pull/5493) [@snkekorfus](https://github.com/snkekorfus)
* Hive: allow UDTF to return multiple column aliases in SELECT [#5495](https://github.com/sqlfluff/sqlfluff/pull/5495) [@reata](https://github.com/reata)
* DB2: Add support for `DECLARE GLOBAL TEMPORARY TABLES`, `OFFSET`, `CALL`, and non-bracketed `VALUES` [#5508](https://github.com/sqlfluff/sqlfluff/pull/5508) [@keraion](https://github.com/keraion)
* DuckDB: Add CREATE OR REPLACE TABLE syntax [#5511](https://github.com/sqlfluff/sqlfluff/pull/5511) [@keraion](https://github.com/keraion)
* TSQL: Top and Distinct in same query [#5491](https://github.com/sqlfluff/sqlfluff/pull/5491) [@greg-finley](https://github.com/greg-finley)
* [Spark/Databricks] Fix: make COLUMNS in APPLY CHANGES INTO optional [#5498](https://github.com/sqlfluff/sqlfluff/pull/5498) [@rocwang](https://github.com/rocwang)
* SparkSQL: exclamation mark as logical not [#5500](https://github.com/sqlfluff/sqlfluff/pull/5500) [@reata](https://github.com/reata)
* SparkSQL: allow value in set_statement to be Java class name [#5504](https://github.com/sqlfluff/sqlfluff/pull/5504) [@reata](https://github.com/reata)
* SparkSQL: allow distribute/sort/cluster by at end of set operation [#5502](https://github.com/sqlfluff/sqlfluff/pull/5502) [@reata](https://github.com/reata)
* [CI] Add a few more mypy checks [#5505](https://github.com/sqlfluff/sqlfluff/pull/5505) [@Koyaani](https://github.com/Koyaani)
* Snowflake dialect: Add support for DATABASE ROLE in GRANT/REVOKE [#5490](https://github.com/sqlfluff/sqlfluff/pull/5490) [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta)
* DuckDB: Qualify and From-First [#5485](https://github.com/sqlfluff/sqlfluff/pull/5485) [@keraion](https://github.com/keraion)
* MySql: create table: allow null/not null in any position [#5473](https://github.com/sqlfluff/sqlfluff/pull/5473) [@archer62](https://github.com/archer62)
* Snowflake dialect: Support for CREATE DATABASE ROLE [#5475](https://github.com/sqlfluff/sqlfluff/pull/5475) [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta)
* Clickhouse Dialect - Support BackQuoted Identifiers [#5457](https://github.com/sqlfluff/sqlfluff/pull/5457) [@kaiyannameighu](https://github.com/kaiyannameighu)
* Change Color.lightgrey to have a white background - dark theme friendly [#5458](https://github.com/sqlfluff/sqlfluff/pull/5458) [@ryaminal](https://github.com/ryaminal)
* Fix indentation for single cube clause [#5462](https://github.com/sqlfluff/sqlfluff/pull/5462) [@tunetheweb](https://github.com/tunetheweb)

## New Contributors
* [@ryaminal](https://github.com/ryaminal) made their first contribution in [#5458](https://github.com/sqlfluff/sqlfluff/pull/5458)
* [@sfc-gh-dgupta](https://github.com/sfc-gh-dgupta) made their first contribution in [#5475](https://github.com/sqlfluff/sqlfluff/pull/5475)
* [@archer62](https://github.com/archer62) made their first contribution in [#5473](https://github.com/sqlfluff/sqlfluff/pull/5473)
* [@keraion](https://github.com/keraion) made their first contribution in [#5485](https://github.com/sqlfluff/sqlfluff/pull/5485)
* [@Koyaani](https://github.com/Koyaani) made their first contribution in [#5505](https://github.com/sqlfluff/sqlfluff/pull/5505)
* [@snkekorfus](https://github.com/snkekorfus) made their first contribution in [#5493](https://github.com/sqlfluff/sqlfluff/pull/5493)
* [@remy-gohiring](https://github.com/remy-gohiring) made their first contribution in [#5527](https://github.com/sqlfluff/sqlfluff/pull/5527)
* [@aayushr7](https://github.com/aayushr7) made their first contribution in [#5528](https://github.com/sqlfluff/sqlfluff/pull/5528)
* [@k1drobot](https://github.com/k1drobot) made their first contribution in [#5559](https://github.com/sqlfluff/sqlfluff/pull/5559)
* [@alangner](https://github.com/alangner) made their first contribution in [#5574](https://github.com/sqlfluff/sqlfluff/pull/5574)
* [@fnimick](https://github.com/fnimick) made their first contribution in [#5577](https://github.com/sqlfluff/sqlfluff/pull/5577)

## [3.0.0a4] - 2023-12-05

## Highlights

This release makes a breaking change to the serialized output of the
CLI (and by extension, any of the serialized outputs of the API).

* The serialised output for `sqlfluff lint` now contains more information
  about the span of linting issues and initial proposed fixes. Beside the *new*
  fields, the original fields of `line_pos` and `line_no` have been
  renamed to `start_line_pos` and `start_line_no`, to distinguish
  them from the new fields starting `end_*`.

* The default `annotation_level` set by the `--annotation-level`
  option on the `sqlfluff lint` command has been changed from `notice`
  to `warning`, to better distinguish linting errors from warnings, which
  always now have the level of `notice`. This is only relevant when using
  the `github-annotation` or `github-annotation-native` formats.

## What’s Changed

* Build out rule and fix serialisation [#5364](https://github.com/sqlfluff/sqlfluff/pull/5364) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add warning about github actions annotations limit [#5450](https://github.com/sqlfluff/sqlfluff/pull/5450) [@alanmcruickshank](https://github.com/alanmcruickshank)
* chore: remove unused line initialization in ParseContext [#5448](https://github.com/sqlfluff/sqlfluff/pull/5448) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Refine CLI testing fixture [#5446](https://github.com/sqlfluff/sqlfluff/pull/5446) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update black linting [#5447](https://github.com/sqlfluff/sqlfluff/pull/5447) [@alanmcruickshank](https://github.com/alanmcruickshank)

## [3.0.0a3] - 2023-11-29

## Highlights

This brings no further _breaking_ changes on top of `3.0.0a2`, but instead
releases a few of the more minor fixes flowing through while other breaking
changes are staged in. In particular there are a few dialect improvements
for Snowflake, TSQL, SQLite and Databricks alongsids a few further
improvements to deployment scripts off the back of earlier changes for `3.x`.

## What’s Changed

* fix assertion in `test__api__lint_string_specific_exclude_single` [#5437](https://github.com/sqlfluff/sqlfluff/pull/5437) [@gvozdvmozgu](https://github.com/gvozdvmozgu)
* Databricks CLUSTER BY and OPTIMIZE [#5436](https://github.com/sqlfluff/sqlfluff/pull/5436) [@greg-finley](https://github.com/greg-finley)
* TSQL: ON DELETE NO ACTION [#5434](https://github.com/sqlfluff/sqlfluff/pull/5434) [@greg-finley](https://github.com/greg-finley)
* Snowflake dynamic table [#5435](https://github.com/sqlfluff/sqlfluff/pull/5435) [@greg-finley](https://github.com/greg-finley)
* Support parsing CONSTRAINT definitions when creating Delta Live Tables in SparkSQL/Databricks [#5438](https://github.com/sqlfluff/sqlfluff/pull/5438) [@rocwang](https://github.com/rocwang)
* adds few fixes for databricks/sparksql [#5431](https://github.com/sqlfluff/sqlfluff/pull/5431) [@markbaas](https://github.com/markbaas)
* TSQL: CREATE USER {FOR|FROM} LOGIN [#5426](https://github.com/sqlfluff/sqlfluff/pull/5426) [@greg-finley](https://github.com/greg-finley)
* Snowflake Create table order/noorder [#5421](https://github.com/sqlfluff/sqlfluff/pull/5421) [@greg-finley](https://github.com/greg-finley)
* Simplify Snowflake regexes [#5419](https://github.com/sqlfluff/sqlfluff/pull/5419) [@greg-finley](https://github.com/greg-finley)
* Permit .* after each tbl_name in multi-table delete syntax [#5408](https://github.com/sqlfluff/sqlfluff/pull/5408) [@yoichi](https://github.com/yoichi)
* Fix snowflake add search optimization grant [#5412](https://github.com/sqlfluff/sqlfluff/pull/5412) [@jongracecox](https://github.com/jongracecox)
* ANSI: Allow combination of UNION clause and WITH clause [#5413](https://github.com/sqlfluff/sqlfluff/pull/5413) [@yoichi](https://github.com/yoichi)
* SQLite: Allow block comments to be terminated by end of input [#5400](https://github.com/sqlfluff/sqlfluff/pull/5400) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Update publish github action to use kebab case [#5392](https://github.com/sqlfluff/sqlfluff/pull/5392) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@jongracecox](https://github.com/jongracecox) made their first contribution in [#5412](https://github.com/sqlfluff/sqlfluff/pull/5412)
* [@markbaas](https://github.com/markbaas) made their first contribution in [#5431](https://github.com/sqlfluff/sqlfluff/pull/5431)
* [@rocwang](https://github.com/rocwang) made their first contribution in [#5438](https://github.com/sqlfluff/sqlfluff/pull/5438)
* [@gvozdvmozgu](https://github.com/gvozdvmozgu) made their first contribution in [#5437](https://github.com/sqlfluff/sqlfluff/pull/5437)

## [3.0.0a2] - 2023-11-09

## Highlights

The initial 3.0.0a1 release failed to build a docker image, this resolves
that issue.

## What’s Changed

* Update publish actions and Dockerfile. [#5390](https://github.com/sqlfluff/sqlfluff/pull/5390) [@alanmcruickshank](https://github.com/alanmcruickshank)


## [3.0.0a1] - 2023-11-08

## Highlights

This release makes a couple of potentially breaking changes:

* It drops support for python 3.7, which reached end of life in June 2023.

* It migrates to `pyproject.toml` rather than `setup.cfg` as the python
  packaging configuration file (although keeping `setuptools` as the default backend).

Further breaking changes may be made as part of the full 3.0.0 release, but this
alpha release is designed to test the new packaging changes for any issues before
releasing a stable version.

## What’s Changed

* Move the rest of pytest over to `pyproject.toml` [#5383](https://github.com/sqlfluff/sqlfluff/pull/5383) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Move doc8 over to pyproject [#5385](https://github.com/sqlfluff/sqlfluff/pull/5385) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove exceptions for typing stubs that now exist. [#5382](https://github.com/sqlfluff/sqlfluff/pull/5382) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Migrate to `pyproject.toml` for the core project. [#5373](https://github.com/sqlfluff/sqlfluff/pull/5373) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix the snippet from a pyproject.toml in configuration.rst [#5378](https://github.com/sqlfluff/sqlfluff/pull/5378) [@ishiis](https://github.com/ishiis)
* Snowflake: Support AlterNetworkPolicy Statements [#5377](https://github.com/sqlfluff/sqlfluff/pull/5377) [@WittierDinosaur](https://github.com/WittierDinosaur)
* postgres: add support for bodies of "language sql" functions [#5376](https://github.com/sqlfluff/sqlfluff/pull/5376) [@65278](https://github.com/65278)
* Add support for SET NAMES statement in MySQL [#5374](https://github.com/sqlfluff/sqlfluff/pull/5374) [@joaostorrer](https://github.com/joaostorrer)
* Fix GRANT ALL PRIVILEGES statement in MySQL [#5375](https://github.com/sqlfluff/sqlfluff/pull/5375) [@joaostorrer](https://github.com/joaostorrer)
* Another extraction of fixing logic. [#5365](https://github.com/sqlfluff/sqlfluff/pull/5365) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove root requirements.txt [#5372](https://github.com/sqlfluff/sqlfluff/pull/5372) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Drop support of python 3.7 [#5288](https://github.com/sqlfluff/sqlfluff/pull/5288) [@zhongjiajie](https://github.com/zhongjiajie)
* API configuration documentation [#5369](https://github.com/sqlfluff/sqlfluff/pull/5369) [@golergka](https://github.com/golergka)
* add listagg extras support in trino dialect [#5368](https://github.com/sqlfluff/sqlfluff/pull/5368) [@wjhrdy](https://github.com/wjhrdy)
* Allow ignoring of comments from indentation entirely #3311 [#5363](https://github.com/sqlfluff/sqlfluff/pull/5363) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Trino: Support Analyze statements [#5361](https://github.com/sqlfluff/sqlfluff/pull/5361) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Resolve #5327 (logging to stdout) [#5362](https://github.com/sqlfluff/sqlfluff/pull/5362) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@wjhrdy](https://github.com/wjhrdy) made their first contribution in [#5368](https://github.com/sqlfluff/sqlfluff/pull/5368)
* [@golergka](https://github.com/golergka) made their first contribution in [#5369](https://github.com/sqlfluff/sqlfluff/pull/5369)
* [@65278](https://github.com/65278) made their first contribution in [#5376](https://github.com/sqlfluff/sqlfluff/pull/5376)
* [@ishiis](https://github.com/ishiis) made their first contribution in [#5378](https://github.com/sqlfluff/sqlfluff/pull/5378)

## [2.3.5] - 2023-10-27

## Highlights

This is a fairly minor release, primarily bugfixes and dialect improvements.

For python API users, there's the addition of a public method on the `FluffConfig`
object allowing the construction of a config object from multiple strings to
mimic the effect of nested config files in the CLI.

This release also includes a selection of internal refactoring and reorganisation
to support future development work.

This also sees the first contributions by [@ShubhamJagtap2000](https://github.com/ShubhamJagtap2000)
& [@kang8](https://github.com/kang8), particularly notable in that both were
contributions to SQLFluff documentation! 🎉🎉🏆🎉🎉

## What’s Changed

* One (very) small typing improvements [#5355](https://github.com/sqlfluff/sqlfluff/pull/5355) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Unpick dependencies between modules in `sqlfluff.core` [#5348](https://github.com/sqlfluff/sqlfluff/pull/5348) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve SparkSQL re-parsing issue + test validation in test suite. [#5351](https://github.com/sqlfluff/sqlfluff/pull/5351) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Support ALTER MASKING POLICY [#5350](https://github.com/sqlfluff/sqlfluff/pull/5350) [@jmks](https://github.com/jmks)
* Add a public API for nesting config strings. [#5349](https://github.com/sqlfluff/sqlfluff/pull/5349) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update handling of dbt compilation errors [#5345](https://github.com/sqlfluff/sqlfluff/pull/5345) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake - Extend Column Default Constraint [#5343](https://github.com/sqlfluff/sqlfluff/pull/5343) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix the dbt anchor link in the realworld documentation [#5341](https://github.com/sqlfluff/sqlfluff/pull/5341) [@kang8](https://github.com/kang8)
* Update README.md [#5340](https://github.com/sqlfluff/sqlfluff/pull/5340) [@ShubhamJagtap2000](https://github.com/ShubhamJagtap2000)
* Logic to render variants of Jinja templates for more coverage. [#5339](https://github.com/sqlfluff/sqlfluff/pull/5339) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Templater slicing refactoring of `RawFileSlice` [#5338](https://github.com/sqlfluff/sqlfluff/pull/5338) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: Support multiple statements in the `BEGIN..EXCEPTION..END` [#5322](https://github.com/sqlfluff/sqlfluff/pull/5322) [@abdel](https://github.com/abdel)
* Remove codecov traces [#5337](https://github.com/sqlfluff/sqlfluff/pull/5337) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@ShubhamJagtap2000](https://github.com/ShubhamJagtap2000) made their first contribution in [#5340](https://github.com/sqlfluff/sqlfluff/pull/5340)
* [@kang8](https://github.com/kang8) made their first contribution in [#5341](https://github.com/sqlfluff/sqlfluff/pull/5341)

## [2.3.4] - 2023-10-17

## Highlights

This is a fairly small bugfix release, mostly to resolve a bug introduced
in 2.3.3 with commas and LT09. This also includes a couple of additional
small performance improvements and some dialect improvements for Oracle,
BigQuery and MySQL.

Thanks in particular to [@bonnal-enzo](https://github.com/bonnal-enzo) who
made their first contribution as part of this release 🎉🎉🏆🎉🎉.

## What’s Changed

* Commas fix in LT09 [#5335](https://github.com/sqlfluff/sqlfluff/pull/5335) [@alanmcruickshank](https://github.com/alanmcruickshank)
* UUID Comparisons [#5332](https://github.com/sqlfluff/sqlfluff/pull/5332) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Two depth map performance improvements [#5333](https://github.com/sqlfluff/sqlfluff/pull/5333) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Stash parent idx with parent reference [#5331](https://github.com/sqlfluff/sqlfluff/pull/5331) [@alanmcruickshank](https://github.com/alanmcruickshank)
* `Set` to `FrozenSet` in segment class_types [#5334](https://github.com/sqlfluff/sqlfluff/pull/5334) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for ANY_VALUE( _ HAVING MIN/MAX _ ) to BigQuery dialect [#5321](https://github.com/sqlfluff/sqlfluff/pull/5321) [@bonnal-enzo](https://github.com/bonnal-enzo)
* Fix parsing error when using quoted slash in Oracle [#5323](https://github.com/sqlfluff/sqlfluff/pull/5323) [@joaostorrer](https://github.com/joaostorrer)
* Add support for functions and procedures calls via database link in Oracle [#5326](https://github.com/sqlfluff/sqlfluff/pull/5326) [@joaostorrer](https://github.com/joaostorrer)
* Fix parsing error with table name '_' in MySQL [#5324](https://github.com/sqlfluff/sqlfluff/pull/5324) [@joaostorrer](https://github.com/joaostorrer)

## New Contributors

* [@bonnal-enzo](https://github.com/bonnal-enzo) made their first contribution in [#5321](https://github.com/sqlfluff/sqlfluff/pull/5321)

## [2.3.3] - 2023-10-13

## Highlights

There's a *lot* in this release. Most of it is under the covers and so shouldn't
cause any breaking changes for most users. If your use case depends on some of the
internals of SQLFluff, you may find some breaking changes. The bigger changes are:

- Python 3.12 support is now official (although older releases may also work as
  only a few changes were required for full 3.12 support).
- We've done a significant re-write of the parsing engine to remove some unnecessary
  segment manipulation and get us closer to "single pass" parsing. This changes the
  internal API being used on any `.match()` methods, and also removes the
  `parse_grammar` attribute on any dialect segments. We are not aware of any 3rd party
  libraries which rely on these APIs however and so have not triggered a more major
  release. These lead to significant performance improvements during parsing.
- Standardisation of terminators in the parser, and the introduction of the `ParseMode`
  option has enabled the removal of the `StartsWith`, `GreedyUntil` and
  `EphemeralSegment` parser classes.
- Several validation checks have been revised in this release, which should both
  improve performance (by reducing duplication), but also be more effective in
  preventing the application of any fixes which would result in unparsable files.

Alongside the big things this also includes a host of bugfixes, dialect improvements
and CI/testing improvements.

This release also sees a bumper crop of new contributors, thanks to
[@dehume](https://github.com/dehume), [@andychannery](https://github.com/andychannery),
[@Kylea650](https://github.com/Kylea650), [@robin-alphasophia](https://github.com/robin-alphasophia),
[@jtbg](https://github.com/jtbg), [@r-petit](https://github.com/r-petit),
[@bpfaust](https://github.com/bpfaust) & [@freewaydev](https://github.com/freewaydev)
who all made the first contributions in this release! 🎉🎉🎉

## What’s Changed

* Oracle space between alias and column reference [#5313](https://github.com/sqlfluff/sqlfluff/pull/5313) [@joaostorrer](https://github.com/joaostorrer)
* Don't apply LT05 on templated rebreak locations #5096 [#5318](https://github.com/sqlfluff/sqlfluff/pull/5318) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Disable JJ01 unless jinja active [#5319](https://github.com/sqlfluff/sqlfluff/pull/5319) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Cache the `BaseSegment` hash in reflow [#5320](https://github.com/sqlfluff/sqlfluff/pull/5320) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Better error reporting for invalid macros [#5317](https://github.com/sqlfluff/sqlfluff/pull/5317) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for begin atomic functions in Postgres [#5316](https://github.com/sqlfluff/sqlfluff/pull/5316) [@joaostorrer](https://github.com/joaostorrer)
* Fix parsing when statement uses plus_sign_join and function in Oracle [#5315](https://github.com/sqlfluff/sqlfluff/pull/5315) [@joaostorrer](https://github.com/joaostorrer)
* Update rule docs with correct config [#5314](https://github.com/sqlfluff/sqlfluff/pull/5314) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #5258. More robust algorithm for multiline fix. [#5309](https://github.com/sqlfluff/sqlfluff/pull/5309) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: Add support for `BEGIN..EXCEPTION...END` block [#5307](https://github.com/sqlfluff/sqlfluff/pull/5307) [@abdel](https://github.com/abdel)
* Refine placement of metas around templated blocks [#5294](https://github.com/sqlfluff/sqlfluff/pull/5294) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Extend ruff checking to docstring rules [#5302](https://github.com/sqlfluff/sqlfluff/pull/5302) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix for strange TSQL bugs [#5306](https://github.com/sqlfluff/sqlfluff/pull/5306) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Staging PR for #5282 [#5305](https://github.com/sqlfluff/sqlfluff/pull/5305) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve some strange whitespace indentation behaviour [#5292](https://github.com/sqlfluff/sqlfluff/pull/5292) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Simplify `_process_lint_result` [#5304](https://github.com/sqlfluff/sqlfluff/pull/5304) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Performance improvement on segment comparison [#5303](https://github.com/sqlfluff/sqlfluff/pull/5303) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Refactor LT09 [#5299](https://github.com/sqlfluff/sqlfluff/pull/5299) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Change drop function to allow DropBehaviourGrammar with space after function name [#5295](https://github.com/sqlfluff/sqlfluff/pull/5295) [@joaostorrer](https://github.com/joaostorrer)
* Resolve click import options on autocomplete [#5293](https://github.com/sqlfluff/sqlfluff/pull/5293) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Updated docstrings with missing args/returns/etc info, added missing docstrings, minor formatting fixes. [#5278](https://github.com/sqlfluff/sqlfluff/pull/5278) [@freewaydev](https://github.com/freewaydev)
* Use ruff rule I replace isort [#5289](https://github.com/sqlfluff/sqlfluff/pull/5289) [@zhongjiajie](https://github.com/zhongjiajie)
* Snowflake: Parse ALTER DATABASE statement [#5284](https://github.com/sqlfluff/sqlfluff/pull/5284) [@jmks](https://github.com/jmks)
* Snowflake: Parse ALTER ACCOUNT statements [#5283](https://github.com/sqlfluff/sqlfluff/pull/5283) [@jmks](https://github.com/jmks)
* Snowflake: create AlterProcedureStatementSegment [#5291](https://github.com/sqlfluff/sqlfluff/pull/5291) [@moreaupascal56](https://github.com/moreaupascal56)
* Rewrite of matching interface [#5230](https://github.com/sqlfluff/sqlfluff/pull/5230) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Follow noqa in block comments [#5133](https://github.com/sqlfluff/sqlfluff/pull/5133) [@daviewales](https://github.com/daviewales)
* Fix insert on conflict with function in Postgres [#5286](https://github.com/sqlfluff/sqlfluff/pull/5286) [@joaostorrer](https://github.com/joaostorrer)
* Add support for Pivot and Unpivot clauses in Oracle [#5285](https://github.com/sqlfluff/sqlfluff/pull/5285) [@joaostorrer](https://github.com/joaostorrer)
* Adding "create table as" for greenplum dialect [#5173](https://github.com/sqlfluff/sqlfluff/pull/5173) [@bpfaust](https://github.com/bpfaust)
* Update CI to python 3.12 [#5267](https://github.com/sqlfluff/sqlfluff/pull/5267) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Add CreateResourceMonitorStatementSegment & AlterResourceMonitorStatementSegment [#5272](https://github.com/sqlfluff/sqlfluff/pull/5272) [@moreaupascal56](https://github.com/moreaupascal56)
* [TSQL] Add create fulltext index statement segment class [#5274](https://github.com/sqlfluff/sqlfluff/pull/5274) [@r-petit](https://github.com/r-petit)
* Snowflake: Add CreateSequenceStatementSegment & AlterSequenceStatementSegment [#5270](https://github.com/sqlfluff/sqlfluff/pull/5270) [@moreaupascal56](https://github.com/moreaupascal56)
* Add CommaSegment to AlterWarehouseStatementSegment SET clause [#5268](https://github.com/sqlfluff/sqlfluff/pull/5268) [@moreaupascal56](https://github.com/moreaupascal56)
* Snowflake: Parse EXECUTE IMMEDIATE clause [#5275](https://github.com/sqlfluff/sqlfluff/pull/5275) [@jmks](https://github.com/jmks)
* TSQL: Add missing `HISTORY_RETENTION_PERIOD` sequence to the table option segment [#5273](https://github.com/sqlfluff/sqlfluff/pull/5273) [@r-petit](https://github.com/r-petit)
* Snowflake: Fix ScalingPolicy and WarehouseType Refs in WarehouseObjectProperties and use ObjectReferenceSegment in AlterWarehouseStatementSegment [#5264](https://github.com/sqlfluff/sqlfluff/pull/5264) [@moreaupascal56](https://github.com/moreaupascal56)
* Finish the removal of `GreedyUntil` [#5263](https://github.com/sqlfluff/sqlfluff/pull/5263) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for date operations with intervals in Oracle [#5262](https://github.com/sqlfluff/sqlfluff/pull/5262) [@joaostorrer](https://github.com/joaostorrer)
* Change RawSegment `type` to `instance_types` [#5253](https://github.com/sqlfluff/sqlfluff/pull/5253) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Revise MatchableType -> Matchable [#5252](https://github.com/sqlfluff/sqlfluff/pull/5252) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Unnest fixing and re-address validation triggers [#5249](https://github.com/sqlfluff/sqlfluff/pull/5249) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolves #5174: Snowflake alter table constraint [#5247](https://github.com/sqlfluff/sqlfluff/pull/5247) [@andychannery](https://github.com/andychannery)
* Bring together the generic segments [#5243](https://github.com/sqlfluff/sqlfluff/pull/5243) [@alanmcruickshank](https://github.com/alanmcruickshank)
* minor: update docs with correct link to airflow ds_filter [#5244](https://github.com/sqlfluff/sqlfluff/pull/5244) [@jtbg](https://github.com/jtbg)
* #5245 - Snowflake dialect: Adds support for variable definitions in scripting blocks [#5246](https://github.com/sqlfluff/sqlfluff/pull/5246) [@robin-alphasophia](https://github.com/robin-alphasophia)
* Introduce "word" segment [#5234](https://github.com/sqlfluff/sqlfluff/pull/5234) [@alanmcruickshank](https://github.com/alanmcruickshank)
* #5239 Added (basic) support for properly linted Snowflake scripting [#5242](https://github.com/sqlfluff/sqlfluff/pull/5242) [@robin-alphasophia](https://github.com/robin-alphasophia)
* Allow Snowflake pipe integration to be a quoted or unquoted [#5241](https://github.com/sqlfluff/sqlfluff/pull/5241) [@Kylea650](https://github.com/Kylea650)
* Fix LT01 alignment regression #4023 [#5238](https://github.com/sqlfluff/sqlfluff/pull/5238) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for oracle non ansi joins [#5231](https://github.com/sqlfluff/sqlfluff/pull/5231) [@joaostorrer](https://github.com/joaostorrer)
* add azure_storage_queue and quoted providers [#5236](https://github.com/sqlfluff/sqlfluff/pull/5236) [@Kylea650](https://github.com/Kylea650)
* Set type automatically within the lexer. [#5232](https://github.com/sqlfluff/sqlfluff/pull/5232) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #5225: Snowflake unparsable select replace [#5227](https://github.com/sqlfluff/sqlfluff/pull/5227) [@andychannery](https://github.com/andychannery)
* Spark Accessor Grammars [#5226](https://github.com/sqlfluff/sqlfluff/pull/5226) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Test Script Timing [#5228](https://github.com/sqlfluff/sqlfluff/pull/5228) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Unify lexer names and types for brackets [#5229](https://github.com/sqlfluff/sqlfluff/pull/5229) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #3176: Snowflake unparsable array casting [#5224](https://github.com/sqlfluff/sqlfluff/pull/5224) [@andychannery](https://github.com/andychannery)
* BigQuery system time syntax [#5220](https://github.com/sqlfluff/sqlfluff/pull/5220) [@greg-finley](https://github.com/greg-finley)
* Parser test nits [#5217](https://github.com/sqlfluff/sqlfluff/pull/5217) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove `parse_grammar` [#5189](https://github.com/sqlfluff/sqlfluff/pull/5189) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Revise segment whitespace validation [#5194](https://github.com/sqlfluff/sqlfluff/pull/5194) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for bpchar datatype in postgres [#5215](https://github.com/sqlfluff/sqlfluff/pull/5215) [@joaostorrer](https://github.com/joaostorrer)
* Resolve #5203: `BaseSegment.copy()` isolation [#5206](https://github.com/sqlfluff/sqlfluff/pull/5206) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update Materialize Syntax [#5210](https://github.com/sqlfluff/sqlfluff/pull/5210) [@dehume](https://github.com/dehume)
* Validate fix parsing based on match_grammar [#5196](https://github.com/sqlfluff/sqlfluff/pull/5196) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Position assertions in BaseSegment [#5209](https://github.com/sqlfluff/sqlfluff/pull/5209) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL bracketed column constraint [#5208](https://github.com/sqlfluff/sqlfluff/pull/5208) [@greg-finley](https://github.com/greg-finley)
* Dialect spacing & quoting issues [#5205](https://github.com/sqlfluff/sqlfluff/pull/5205) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update comment workflow again [#5201](https://github.com/sqlfluff/sqlfluff/pull/5201) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Stash PR Number and hydrate later [#5200](https://github.com/sqlfluff/sqlfluff/pull/5200) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix API issues in github comment action [#5199](https://github.com/sqlfluff/sqlfluff/pull/5199) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Consistency check in root parse [#5191](https://github.com/sqlfluff/sqlfluff/pull/5191) [@alanmcruickshank](https://github.com/alanmcruickshank)
* PR Comment action [#5192](https://github.com/sqlfluff/sqlfluff/pull/5192) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Cache python dependencies in GHA [#5193](https://github.com/sqlfluff/sqlfluff/pull/5193) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for create server, create user mapping and import foreign schema in postgres [#5185](https://github.com/sqlfluff/sqlfluff/pull/5185) [@joaostorrer](https://github.com/joaostorrer)
* Terminators on `Anything()` + Strip _most_ of the other `parse_grammar` [#5186](https://github.com/sqlfluff/sqlfluff/pull/5186) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Parse modes for `AnyNumberOf` [#5187](https://github.com/sqlfluff/sqlfluff/pull/5187) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Introduce `parse_mode` and remove `StartsWith` & `EphemeralSegment`. [#5167](https://github.com/sqlfluff/sqlfluff/pull/5167) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@dehume](https://github.com/dehume) made their first contribution in [#5210](https://github.com/sqlfluff/sqlfluff/pull/5210)
* [@andychannery](https://github.com/andychannery) made their first contribution in [#5224](https://github.com/sqlfluff/sqlfluff/pull/5224)
* [@Kylea650](https://github.com/Kylea650) made their first contribution in [#5236](https://github.com/sqlfluff/sqlfluff/pull/5236)
* [@robin-alphasophia](https://github.com/robin-alphasophia) made their first contribution in [#5242](https://github.com/sqlfluff/sqlfluff/pull/5242)
* [@jtbg](https://github.com/jtbg) made their first contribution in [#5244](https://github.com/sqlfluff/sqlfluff/pull/5244)
* [@r-petit](https://github.com/r-petit) made their first contribution in [#5273](https://github.com/sqlfluff/sqlfluff/pull/5273)
* [@bpfaust](https://github.com/bpfaust) made their first contribution in [#5173](https://github.com/sqlfluff/sqlfluff/pull/5173)
* [@freewaydev](https://github.com/freewaydev) made their first contribution in [#5278](https://github.com/sqlfluff/sqlfluff/pull/5278)
* [@abdel](https://github.com/abdel) made their first contribution in [#5307](https://github.com/sqlfluff/sqlfluff/pull/5307)

## [2.3.2] - 2023-09-10

## Highlights

Much of this release is internal optimisations and refactoring. We're in the
process of upgrading some quite old code in the parser, most of which should
not be visible to end users (apart from perhaps some performance improvements!).

This release also allows missing template variables in the placeholder templater
to be automatically filled with the name of the variable rather than raising
an error (see: [#5101](https://github.com/sqlfluff/sqlfluff/pull/5101)).

Beyond that this includes some dialect improvements for DuckDB, SparkSQL,
Snowflake, Redshift & Postgres.

Thanks particularly to [@shyaginuma](https://github.com/shyaginuma), [@Fullcure3](https://github.com/Fullcure3),
[@adilkhanekt](https://github.com/adilkhanekt) & [@pilou-komoot](https://github.com/pilou-komoot)
who made their first contributions as part of this release. 🎉🎉🎉

## What’s Changed

* Allow not specifying parameters names when using placeholder templater [#5101](https://github.com/sqlfluff/sqlfluff/pull/5101) [@shyaginuma](https://github.com/shyaginuma)
* Update coverage job to run in the right conditions [#5183](https://github.com/sqlfluff/sqlfluff/pull/5183) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Duckdb: UNION BY NAME [#5176](https://github.com/sqlfluff/sqlfluff/pull/5176) [@greg-finley](https://github.com/greg-finley)
* Output coverage report direct to PR [#5180](https://github.com/sqlfluff/sqlfluff/pull/5180) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Upgrades to the parse fixture generation script [#5182](https://github.com/sqlfluff/sqlfluff/pull/5182) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Refactor of Sequence match [#5177](https://github.com/sqlfluff/sqlfluff/pull/5177) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Simplify Greedy Match [#5178](https://github.com/sqlfluff/sqlfluff/pull/5178) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Quality of life improvements on parse fixture script [#5179](https://github.com/sqlfluff/sqlfluff/pull/5179) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Lift and shift matching algorithms [#5170](https://github.com/sqlfluff/sqlfluff/pull/5170) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Capitalise boolean values in example configs, for consistency [#5175](https://github.com/sqlfluff/sqlfluff/pull/5175) [@pilou-komoot](https://github.com/pilou-komoot)
* Pull terminator setting up into the base grammar [#5172](https://github.com/sqlfluff/sqlfluff/pull/5172) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Flip the if in sequence and un-nest [#5171](https://github.com/sqlfluff/sqlfluff/pull/5171) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SparkSQL: Support CACHE TABLE without query [#5165](https://github.com/sqlfluff/sqlfluff/pull/5165) [@reata](https://github.com/reata)
* Remove configurable `enforce_whitespace_preceding_terminator` [#5162](https://github.com/sqlfluff/sqlfluff/pull/5162) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adding optional sequence block for columns parsing in Snowflake external tables [#5157](https://github.com/sqlfluff/sqlfluff/pull/5157) [@adilkhanekt](https://github.com/adilkhanekt)
* SparkSQL: Support ALTER TABLE SET LOCATION without partition spec [#5168](https://github.com/sqlfluff/sqlfluff/pull/5168) [@reata](https://github.com/reata)
* Tighten terminators on `Delimited` [#5161](https://github.com/sqlfluff/sqlfluff/pull/5161) [@alanmcruickshank](https://github.com/alanmcruickshank)
* `terminator` > `terminators` on StartsWith [#5152](https://github.com/sqlfluff/sqlfluff/pull/5152) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Redshift: Support SELECT INTO [#5159](https://github.com/sqlfluff/sqlfluff/pull/5159) [@reata](https://github.com/reata)
* Duckdb: Integer division [#5154](https://github.com/sqlfluff/sqlfluff/pull/5154) [@greg-finley](https://github.com/greg-finley)
* `terminator` > `terminators` on Delimited grammar [#5150](https://github.com/sqlfluff/sqlfluff/pull/5150) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Tests for unparsable sections [#5149](https://github.com/sqlfluff/sqlfluff/pull/5149) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Un-nest the delimited match method [#5147](https://github.com/sqlfluff/sqlfluff/pull/5147) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Grammar .copy() assert no unexpected kwargs [#5148](https://github.com/sqlfluff/sqlfluff/pull/5148) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: CLUSTER [#5146](https://github.com/sqlfluff/sqlfluff/pull/5146) [@greg-finley](https://github.com/greg-finley)
* Postgres alter policy [#5138](https://github.com/sqlfluff/sqlfluff/pull/5138) [@Fullcure3](https://github.com/Fullcure3)


## New Contributors
* [@Fullcure3](https://github.com/Fullcure3) made their first contribution in [#5138](https://github.com/sqlfluff/sqlfluff/pull/5138)
* [@adilkhanekt](https://github.com/adilkhanekt) made their first contribution in [#5157](https://github.com/sqlfluff/sqlfluff/pull/5157)
* [@pilou-komoot](https://github.com/pilou-komoot) made their first contribution in [#5175](https://github.com/sqlfluff/sqlfluff/pull/5175)
* [@shyaginuma](https://github.com/shyaginuma) made their first contribution in [#5101](https://github.com/sqlfluff/sqlfluff/pull/5101)

## [2.3.1] - 2023-08-29

## Highlights

This release is primarily a performance release, with most major changes
aimed at the linting and fixing phases of operation. Most of the longest
duration rules (excepting the layout rules) should see noticeable speed
improvements.

Alongside those changes, there are a selection of bugfixes and dialect
improvements for Oracle, PostgreSQL, Snowflake & TSQL.

## What’s Changed

* Postgres: Update returning with alias [#5137](https://github.com/sqlfluff/sqlfluff/pull/5137) [@greg-finley](https://github.com/greg-finley)
* Reduce copying on  _position_segments (improves `fix`) [#5119](https://github.com/sqlfluff/sqlfluff/pull/5119) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Import rationalisation [#5135](https://github.com/sqlfluff/sqlfluff/pull/5135) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Select Crawler Refactor: Part 3 [#5115](https://github.com/sqlfluff/sqlfluff/pull/5115) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for comparison operators with space in Oracle [#5132](https://github.com/sqlfluff/sqlfluff/pull/5132) [@joaostorrer](https://github.com/joaostorrer)
* Snowflake support for bracketed query after `EXCEPT` [#5126](https://github.com/sqlfluff/sqlfluff/pull/5126) [@ulixius9](https://github.com/ulixius9)
* Treatment of null literals. #5099 [#5125](https://github.com/sqlfluff/sqlfluff/pull/5125) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow double-quoted parameters in create procedure [#5131](https://github.com/sqlfluff/sqlfluff/pull/5131) [@greg-finley](https://github.com/greg-finley)
* Fix coverage & mypy [#5134](https://github.com/sqlfluff/sqlfluff/pull/5134) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Ensure Unparsable can be given position. [#5117](https://github.com/sqlfluff/sqlfluff/pull/5117) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Reduce copying in LintFix instantiation [#5118](https://github.com/sqlfluff/sqlfluff/pull/5118) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Optimise crawl behaviour of JJ01 [#5116](https://github.com/sqlfluff/sqlfluff/pull/5116) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Simplify rules with improvement to SegmentSeeker [#5113](https://github.com/sqlfluff/sqlfluff/pull/5113) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Refactor AM07 [#5112](https://github.com/sqlfluff/sqlfluff/pull/5112) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Select Crawler Refactor: Part 2 [#5110](https://github.com/sqlfluff/sqlfluff/pull/5110) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support to Hierarchical Queries in Oracle [#5108](https://github.com/sqlfluff/sqlfluff/pull/5108) [@joaostorrer](https://github.com/joaostorrer)
* ✅ Strict MyPy for sqlfluff.core.parser [#5107](https://github.com/sqlfluff/sqlfluff/pull/5107) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Free up pydocstyle again [#5109](https://github.com/sqlfluff/sqlfluff/pull/5109) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Allow CREATE TABLE INHERITS with no new columns [#5100](https://github.com/sqlfluff/sqlfluff/pull/5100) [@greg-finley](https://github.com/greg-finley)
* Strict mypy in parser.segments [#5094](https://github.com/sqlfluff/sqlfluff/pull/5094) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Select Crawler Refactor: Part 1 [#5104](https://github.com/sqlfluff/sqlfluff/pull/5104) [@alanmcruickshank](https://github.com/alanmcruickshank)
* RF01 & recursive_crawl improvements [#5102](https://github.com/sqlfluff/sqlfluff/pull/5102) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix new more restrictive tox [#5103](https://github.com/sqlfluff/sqlfluff/pull/5103) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Make Day as Non Reserved Keyword [#5062](https://github.com/sqlfluff/sqlfluff/pull/5062) [@ulixius9](https://github.com/ulixius9)

## [2.3.0] - 2023-08-14

## Highlights

This release brings one new dialect, two new rules and some changes to the CLI:
- We now support the [trino](https://trino.io/) dialect. This is a first version of
  support, so do post any issues on GitHub in the usual way. This was also the first
  contribution to the project from [@efung](https://github.com/efung) 🏆.
- `ST09` / `structure.join_condition_order`: Which checks whether tables referenced
  in `JOIN` clauses are referenced in the order of their definition. By default
  this means that in the `ON` clause, the column referencing the table in the
  `FROM` clause should come before the column referencing the table in the `JOIN`
  clause (e.g. `... FROM a JOIN b on a.c = b.c`). This rule was also the first
  contribution to the project from [@thibonacci](https://github.com/thibonacci) 🏆.
- `AL08` / `aliasing.unique.column`: Which checks that column aliases and names
  are not repeated within the same `SELECT` clause. This is normally an error
  as it implies the same column has been imported twice, or that two expressions
  have been given the same alias.
- The `--profiler` option on `sqlfluff parse` has been removed. It was only
  present on the `parse` command and not `lint` or `fix`, and it is just as simple
  to invoke the python `cProfiler` directly.
- The `--recurse` cli option and `sqlfluff.recurse` configuration option have
  both been removed. They both existed purely for debugging the parser, and were
  never used in a production setting. The improvement in other debugging messages
  when unparsable sections are found means that this option is no longer necessary.

Along side these more significant changes this also includes:
- Performance optimisations for `AL04`, `AL05`, `AM04`, `RF01` & `ST05` which
  cumulatively may save up to 30% on the total time spend in the linting phase
  for some projects.
- Dialect improvements for Oracle & TSQL.

## What’s Changed

* Remove IdentitySet [#5093](https://github.com/sqlfluff/sqlfluff/pull/5093) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Stricter typing in smaller sqlfluff.core.parser [#5088](https://github.com/sqlfluff/sqlfluff/pull/5088) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Preliminary support of Trino dialect [#4913](https://github.com/sqlfluff/sqlfluff/pull/4913) [@efung](https://github.com/efung)
* Rename ST09 [#5091](https://github.com/sqlfluff/sqlfluff/pull/5091) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: Fix Clustered Index asc/desc [#5090](https://github.com/sqlfluff/sqlfluff/pull/5090) [@greg-finley](https://github.com/greg-finley)
* Parent references and more efficient path_to [#5076](https://github.com/sqlfluff/sqlfluff/pull/5076) [@alanmcruickshank](https://github.com/alanmcruickshank)
* New Rule: AL08 - column aliases must be unique [#5079](https://github.com/sqlfluff/sqlfluff/pull/5079) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for fetch first row(s) only in Oracle [#5089](https://github.com/sqlfluff/sqlfluff/pull/5089) [@joaostorrer](https://github.com/joaostorrer)
* Fix bug around quoted identifiers for ST09 [#5087](https://github.com/sqlfluff/sqlfluff/pull/5087) [@thibonacci](https://github.com/thibonacci)
* Add strict typing to the templating tracer [#5085](https://github.com/sqlfluff/sqlfluff/pull/5085) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remove recurse config [#5065](https://github.com/sqlfluff/sqlfluff/pull/5065) [@alanmcruickshank](https://github.com/alanmcruickshank)
* ✅ Strictly type dialect [#5067](https://github.com/sqlfluff/sqlfluff/pull/5067) [@pwildenhain](https://github.com/pwildenhain)
* Add new rule ST09: Joins should list the table referenced earlier (default)/later first [#4974](https://github.com/sqlfluff/sqlfluff/pull/4974) [@thibonacci](https://github.com/thibonacci)
* Remove the internal cProfiler option [#5081](https://github.com/sqlfluff/sqlfluff/pull/5081) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Optimisation on select analysis [#5082](https://github.com/sqlfluff/sqlfluff/pull/5082) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@thibonacci](https://github.com/thibonacci) made their first contribution in [#4974](https://github.com/sqlfluff/sqlfluff/pull/4974)
* [@efung](https://github.com/efung) made their first contribution in [#4913](https://github.com/sqlfluff/sqlfluff/pull/4913)

## [2.2.1] - 2023-08-09

## Highlights

This is primarily a bugfix release for 2.2.0 which introduced
a bug in the `exit_code` returned by linting commands which ignored errors
while setting `processes > 1`.

In addition to that this release introduces bugfixes for:
- Errors raised by two specific `dbt` exceptions.
- Issues with unwanted logging output when using `-f yaml` or `-f json`
  alongside the `dbt` templater.

This also introduces dialect improvements for Oracle and for `LIMIT` clauses.

Thanks also to [@adityapat3l](https://github.com/adityapat3l) who made their
first contribution as part of this release! 🎉🎉🎉

## What’s Changed

* Split apart the grammar tests [#5078](https://github.com/sqlfluff/sqlfluff/pull/5078) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve pickling of errors #5066 [#5074](https://github.com/sqlfluff/sqlfluff/pull/5074) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Better context based tracking [#5064](https://github.com/sqlfluff/sqlfluff/pull/5064) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fixing limit handling for bracketed arithmathic operations [#5068](https://github.com/sqlfluff/sqlfluff/pull/5068) [@adityapat3l](https://github.com/adityapat3l)
* Never run in multiprocessing mode with only 1 file. [#5071](https://github.com/sqlfluff/sqlfluff/pull/5071) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add dbt 1.6 tests [#5073](https://github.com/sqlfluff/sqlfluff/pull/5073) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle two kinds of dbt errors more gracefully [#5072](https://github.com/sqlfluff/sqlfluff/pull/5072) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Try to silence dbt logging #5054 [#5070](https://github.com/sqlfluff/sqlfluff/pull/5070) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Move `_prune_options` within `_longest_trimmed_match`. [#5063](https://github.com/sqlfluff/sqlfluff/pull/5063) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix issue 4998 - Add backup and auto refresh grammar to redshift materialized view [#5060](https://github.com/sqlfluff/sqlfluff/pull/5060) [@adityapat3l](https://github.com/adityapat3l)
* Add mypy strict typing for sqlfluff.core.rules [#5048](https://github.com/sqlfluff/sqlfluff/pull/5048) [@pwildenhain](https://github.com/pwildenhain)
* :arrow_up: Bump mypy version in pre-commit [#5055](https://github.com/sqlfluff/sqlfluff/pull/5055) [@pwildenhain](https://github.com/pwildenhain)
* Add SQL Plus bind variable support (Oracle) [#5053](https://github.com/sqlfluff/sqlfluff/pull/5053) [@joaostorrer](https://github.com/joaostorrer)

## New Contributors

* [@adityapat3l](https://github.com/adityapat3l) made their first contribution in [#5060](https://github.com/sqlfluff/sqlfluff/pull/5060)

## [2.2.0] - 2023-08-04

## Highlights

This release changes some of the interfaces between SQLFluff core and
our plugin ecosystem. The only *breaking* change is in the interface
between SQLFluff and *templater* plugins (which are not common in the
ecosystem, hence why this is only a minor and not a major release).

For all plugins, we also recommend a different structure for their
imports (especially for rule plugins which are more common in the
ecosystem) - for performance and stability reasons. Some users had
been experiencing very long import times with previous releases as
a result of the layout of plugin imports. Users with affected plugins
will begin to see a warning from this release onward, which can be
resolved for their plugin by updating to a new version of that plugin
which follows the guidelines.

For more details (especially if you're a plugin maintainer) see our
[release notes](https://docs.sqlfluff.com/en/latest/releasenotes.html).

Additionally this release includes:
- Some internal performance gains which may cumulatively save
  roughly 10% of the time spent in the parsing phase of larger files.
- Improvements to the Simple API, including the ability to pass in
  a `FluffConfig` object directly, and better support for parsing
  config files directly from strings (see
  [the included example](examples/05_simple_api_config.py)).
- A bugfix for `AM06`.
- A new `--warn-unused-ignores` CLI option (and corresponding config
  setting) to allow warnings to be shown if any `noqa` comments in
  SQL files are unused.
- Improvements to Redshift, Oracle, Clickhouse, Materialize &
  MySQL dialects.
- A selection of internal improvements, documentation and type hints.

Thanks also to [@kaiyannameighu](https://github.com/kaiyannameighu),
[@josef-v](https://github.com/josef-v),
[@aglebov](https://github.com/aglebov) &
[@joaostorrer](https://github.com/joaostorrer) who made their first
contributions as part of this release! 🎉🎉🎉

## What’s Changed

* Mypy: Ephemeral + Tuple Return on .parse() [#5044](https://github.com/sqlfluff/sqlfluff/pull/5044) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support to oracle's global and private temporary tables [#5039](https://github.com/sqlfluff/sqlfluff/pull/5039) [@joaostorrer](https://github.com/joaostorrer)
* Redshift-dialect: Support GRANT USAGE ON DATASHARE [#5007](https://github.com/sqlfluff/sqlfluff/pull/5007) [@josef-v](https://github.com/josef-v)
* :white_check_mark: Add strict typing for errors module [#5047](https://github.com/sqlfluff/sqlfluff/pull/5047) [@pwildenhain](https://github.com/pwildenhain)
* Less copying in the ParseContext [#5046](https://github.com/sqlfluff/sqlfluff/pull/5046) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adding support to use `ADD COLUMN IF NOT EXISTS` syntax on `ALTER TABLE` [#5035](https://github.com/sqlfluff/sqlfluff/pull/5035) [@wfelipew](https://github.com/wfelipew)
* Closes #4815 [#5042](https://github.com/sqlfluff/sqlfluff/pull/5042) [@joaostorrer](https://github.com/joaostorrer)
* Fix for multiprocessing warnings. [#5032](https://github.com/sqlfluff/sqlfluff/pull/5032) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Mypy gain: Remove unnecessary tuple construction in MatchResult [#5045](https://github.com/sqlfluff/sqlfluff/pull/5045) [@alanmcruickshank](https://github.com/alanmcruickshank)
* mypy strict in config [#5036](https://github.com/sqlfluff/sqlfluff/pull/5036) [@pwildenhain](https://github.com/pwildenhain)
* strict mypy: match_wrapper & match_logging [#5033](https://github.com/sqlfluff/sqlfluff/pull/5033) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MyPy on errors, helpers, markers & context + remove ParseContext.denylist [#5030](https://github.com/sqlfluff/sqlfluff/pull/5030) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Warn on unused `noqa` directives [#5029](https://github.com/sqlfluff/sqlfluff/pull/5029) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Even more mypy strict [#5023](https://github.com/sqlfluff/sqlfluff/pull/5023) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Handle windows paths better in config files. [#5022](https://github.com/sqlfluff/sqlfluff/pull/5022) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix for parsing of Oracle functions with named arguments [#5027](https://github.com/sqlfluff/sqlfluff/pull/5027) [@joaostorrer](https://github.com/joaostorrer)
* DOC: Fix .sqlfluff example in Getting Started [#5026](https://github.com/sqlfluff/sqlfluff/pull/5026) [@aglebov](https://github.com/aglebov)
* Fix: Add exception to the warning & config for the BaseRule. [#5025](https://github.com/sqlfluff/sqlfluff/pull/5025) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Move from `make_template` to `render_func` in jinja and dbt [#4942](https://github.com/sqlfluff/sqlfluff/pull/4942) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Streamline imports to reduce initial load times #4917 [#5020](https://github.com/sqlfluff/sqlfluff/pull/5020) [@alanmcruickshank](https://github.com/alanmcruickshank)
* More mypy strict [#5019](https://github.com/sqlfluff/sqlfluff/pull/5019) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Simple API config and examples [#5018](https://github.com/sqlfluff/sqlfluff/pull/5018) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix some new linting issues [#5021](https://github.com/sqlfluff/sqlfluff/pull/5021) [@alanmcruickshank](https://github.com/alanmcruickshank)
* A step towards mypy strict [#5014](https://github.com/sqlfluff/sqlfluff/pull/5014) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Materialize: Make RETURNING a reserved keyword [#5017](https://github.com/sqlfluff/sqlfluff/pull/5017) [@bobbyiliev](https://github.com/bobbyiliev)
* Config from string and load default_config as resource [#5012](https://github.com/sqlfluff/sqlfluff/pull/5012) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Documentation for the test suite (#2180) [#5011](https://github.com/sqlfluff/sqlfluff/pull/5011) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support to oracle's listagg function [#4999](https://github.com/sqlfluff/sqlfluff/pull/4999) [@joaostorrer](https://github.com/joaostorrer)
* Assorted typehints [#5013](https://github.com/sqlfluff/sqlfluff/pull/5013) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Refactor: Extract noqa methods and tests. [#5010](https://github.com/sqlfluff/sqlfluff/pull/5010) [@alanmcruickshank](https://github.com/alanmcruickshank)
* AM06 to ignore aggregate ORDER BY clauses [#5008](https://github.com/sqlfluff/sqlfluff/pull/5008) [@tunetheweb](https://github.com/tunetheweb)
* Bugfix: Treat Function name properly in grants [#5006](https://github.com/sqlfluff/sqlfluff/pull/5006) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Redshift: Add Qualify Clause [#5002](https://github.com/sqlfluff/sqlfluff/pull/5002) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Clickhouse Dialect - Support Dollar Quoted Literals [#5003](https://github.com/sqlfluff/sqlfluff/pull/5003) [@kaiyannameighu](https://github.com/kaiyannameighu)


## New Contributors
* [@kaiyannameighu](https://github.com/kaiyannameighu) made their first contribution in [#5003](https://github.com/sqlfluff/sqlfluff/pull/5003)
* [@joaostorrer](https://github.com/joaostorrer) made their first contribution in [#4999](https://github.com/sqlfluff/sqlfluff/pull/4999)
* [@aglebov](https://github.com/aglebov) made their first contribution in [#5026](https://github.com/sqlfluff/sqlfluff/pull/5026)
* [@josef-v](https://github.com/josef-v) made their first contribution in [#5007](https://github.com/sqlfluff/sqlfluff/pull/5007)

## [2.1.4] - 2023-07-25

## Highlights

This release brings some meaningful performance improvements to the parsing of
complex SQL statements. In files with deeply nested expressions, we have seen
up to a 50% reduction on time spent in the parsing phase. These changes are all
internal optimisations and have minimal implications for the parser. In a few
isolated cases they did highlight inconsistencies in the parsing of literals
and so if your use case relies on the specific structure of literal and
expression parsing you may find some small differences in how some expressions
are parsed.

Additionally this release brings new validation steps to configuration.
Layout configuration is now validated on load (and so users with invalid
layout configurations may see some of these being caught now) and inline
configuration statements in files are also now validated for both their
layout rules and for any removed or deprecated settings.

On top of both we've seen dialect improvements to Databricks, PostgreSQL,
BigQuery, Snowflake & Athena.

## What’s Changed

* Databricks set time zone [#5000](https://github.com/sqlfluff/sqlfluff/pull/5000) [@greg-finley](https://github.com/greg-finley)
* Terminator inheritance [#4981](https://github.com/sqlfluff/sqlfluff/pull/4981) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Reduce copying in the parse phase [#4988](https://github.com/sqlfluff/sqlfluff/pull/4988) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Validate layout configs #4578 [#4997](https://github.com/sqlfluff/sqlfluff/pull/4997) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix handling of keywords for roles in ALTER ROLE statement [#4994](https://github.com/sqlfluff/sqlfluff/pull/4994) [@anzelpwj](https://github.com/anzelpwj)
* BigQuery: fixes parse error on some literals with data type and quoted [#4992](https://github.com/sqlfluff/sqlfluff/pull/4992) [@yoichi](https://github.com/yoichi)
* Correct Snowflake `CROSS JOIN` syntax [#4996](https://github.com/sqlfluff/sqlfluff/pull/4996) [@tunetheweb](https://github.com/tunetheweb)
* Remove broken 'fork me' banner from docs [#4989](https://github.com/sqlfluff/sqlfluff/pull/4989) [@greg-finley](https://github.com/greg-finley)
* feat: support athena optional WITH ORDINALITY post UNNEST function [#4991](https://github.com/sqlfluff/sqlfluff/pull/4991) [@reata](https://github.com/reata)

## [2.1.3] - 2023-07-19

## Highlights

This release is a fairly standard incremental release. Highlights include bugfixes
to `RF05` and dialect improvements to Snowflake, Teradata, MySQL, TSQL, SparkSQL & Postgres.

Internally, the last few weeks have brought several improvements to developer tooling.

We've also moved over to GitHub sponsorships - so if you previously used the old
flattr link, you can find our new profile page at https://github.com/sponsors/sqlfluff.

## What’s Changed

* Add the which dbt flag to DbtConfigArgs with default as "compile" [#4982](https://github.com/sqlfluff/sqlfluff/pull/4982) [@moreaupascal56](https://github.com/moreaupascal56)
* feat: support tsql COPY INTO [#4985](https://github.com/sqlfluff/sqlfluff/pull/4985) [@reata](https://github.com/reata)
* fix: sparksql lateral view parse tree for multiple column alias [#4980](https://github.com/sqlfluff/sqlfluff/pull/4980) [@reata](https://github.com/reata)
* Revert "Ignore click mypy issues" [#4967](https://github.com/sqlfluff/sqlfluff/pull/4967) [@greg-finley](https://github.com/greg-finley)
* Snowflake: Parse column named cross [#4975](https://github.com/sqlfluff/sqlfluff/pull/4975) [@greg-finley](https://github.com/greg-finley)
* Snowflake: Group by all [#4976](https://github.com/sqlfluff/sqlfluff/pull/4976) [@greg-finley](https://github.com/greg-finley)
* Update funding yaml to use github sponsors [#4973](https://github.com/sqlfluff/sqlfluff/pull/4973) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Added DEL keyword [#4962](https://github.com/sqlfluff/sqlfluff/pull/4962) [@dflem97](https://github.com/dflem97)
* Remove mypy ignores [#4972](https://github.com/sqlfluff/sqlfluff/pull/4972) [@greg-finley](https://github.com/greg-finley)
* Allow running one rule test locally [#4963](https://github.com/sqlfluff/sqlfluff/pull/4963) [@greg-finley](https://github.com/greg-finley)
* Postgres support underscore array data type syntax [#4959](https://github.com/sqlfluff/sqlfluff/pull/4959) [@greg-finley](https://github.com/greg-finley)
* Bump issue-labeler [#4958](https://github.com/sqlfluff/sqlfluff/pull/4958) [@greg-finley](https://github.com/greg-finley)
* Standardize test fixture names [#4955](https://github.com/sqlfluff/sqlfluff/pull/4955) [@greg-finley](https://github.com/greg-finley)
* RF05 BigQuery empty identifier bug [#4953](https://github.com/sqlfluff/sqlfluff/pull/4953) [@keitherskine](https://github.com/keitherskine)
* New GitHub issue labeler library [#4952](https://github.com/sqlfluff/sqlfluff/pull/4952) [@greg-finley](https://github.com/greg-finley)
* Ignore click mypy issues [#4954](https://github.com/sqlfluff/sqlfluff/pull/4954) [@greg-finley](https://github.com/greg-finley)
* MySQL: Rename index [#4950](https://github.com/sqlfluff/sqlfluff/pull/4950) [@greg-finley](https://github.com/greg-finley)
* Adding support to ALTER TABLE with RENAME COLUMN on MySQL dialect [#4948](https://github.com/sqlfluff/sqlfluff/pull/4948) [@jrballot](https://github.com/jrballot)


## New Contributors
* [@jrballot](https://github.com/jrballot) made their first contribution in [#4948](https://github.com/sqlfluff/sqlfluff/pull/4948)
* [@keitherskine](https://github.com/keitherskine) made their first contribution in [#4953](https://github.com/sqlfluff/sqlfluff/pull/4953)
* [@reata](https://github.com/reata) made their first contribution in [#4980](https://github.com/sqlfluff/sqlfluff/pull/4980)

## [2.1.2] - 2023-07-03

## Highlights

This release resolves compatibility issues with a set of `dbt-core` versions.
- `dbt-core` 1.5.2 onwards is now properly supported.
- support for `dbt-core` 1.1 to 1.4 has now been re-enabled after
  support had to be abandoned a few releases ago.

NOTE: We cannot guarantee that SQLFluff will always continue to remain
compatible with all dbt versions, particularly as the folks at dbt-labs
have often backported breaking changes to their internal APIs to previous
versions of `dbt-core`. This release does at least bring more extensive
internal testing to catch when this does occur to allow our community
to react.

This release fixes also resolves a potential security issue for when
using external libraries (and the `library_path` config setting),
and also contains various dialect improvements.

## What’s Changed

* docs(templater): Add documentation for `SQLFLUFF_JINJA_FILTERS` [#4932](https://github.com/sqlfluff/sqlfluff/pull/4932) [@dmohns](https://github.com/dmohns)
* Re-enable dbt 1.1 & 1.2 [#4944](https://github.com/sqlfluff/sqlfluff/pull/4944) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Re-enable dbt 1.4 & 1.3 [#4941](https://github.com/sqlfluff/sqlfluff/pull/4941) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix compatibility with dbt 1.5.2+ [#4939](https://github.com/sqlfluff/sqlfluff/pull/4939) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Security option for library path [#4925](https://github.com/sqlfluff/sqlfluff/pull/4925) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove extra code escapes from release notes docs [#4921](https://github.com/sqlfluff/sqlfluff/pull/4921) [@tunetheweb](https://github.com/tunetheweb)
* Postgres frame_clause quoted interval [#4915](https://github.com/sqlfluff/sqlfluff/pull/4915) [@greg-finley](https://github.com/greg-finley)
* Snowflake: CREATE TAG [#4914](https://github.com/sqlfluff/sqlfluff/pull/4914) [@greg-finley](https://github.com/greg-finley)
* TSQL: support for `DROP EXTERNAL TABLE` [#4919](https://github.com/sqlfluff/sqlfluff/pull/4919) [@keen85](https://github.com/keen85)
* fix(dialect-clickhouse): Support create database [#4620](https://github.com/sqlfluff/sqlfluff/pull/4620) [@germainlefebvre4](https://github.com/germainlefebvre4)
* Snowflake: Actualize the CreateProcedureStatementSegment and CreateFunctionStatementSegment [#4908](https://github.com/sqlfluff/sqlfluff/pull/4908) [@moreaupascal56](https://github.com/moreaupascal56)
* Oracle: Add support for `$` and `#`  in identifier [#4903](https://github.com/sqlfluff/sqlfluff/pull/4903) [@ulixius9](https://github.com/ulixius9)
* docs(templater): Refactor templater configuration docs [#4835](https://github.com/sqlfluff/sqlfluff/pull/4835) [@dmohns](https://github.com/dmohns)
* Handle brackets in from clause with joins [#4890](https://github.com/sqlfluff/sqlfluff/pull/4890) [@ulixius9](https://github.com/ulixius9)
* Postgres: Add support for dollar literal & mark collation as non-reserved [#4883](https://github.com/sqlfluff/sqlfluff/pull/4883) [@ulixius9](https://github.com/ulixius9)
* MySQL: ON UPDATE NOW [#4898](https://github.com/sqlfluff/sqlfluff/pull/4898) [@greg-finley](https://github.com/greg-finley)
* Support ROLLUP/CUBE in AM06 [#4892](https://github.com/sqlfluff/sqlfluff/pull/4892) [@tunetheweb](https://github.com/tunetheweb)

## [2.1.1] - 2023-05-25

## Highlights

This releases fixes a compatibility issue with the latest version of dbt. It also ships various dialect improvements.

## What’s Changed

* profiles dir env var or default [#4886](https://github.com/sqlfluff/sqlfluff/pull/4886) [@JasonGluck](https://github.com/JasonGluck)
* Bigquery: Allow empty `struct` in `TO_JSON` [#4879](https://github.com/sqlfluff/sqlfluff/pull/4879) [@dimitris-flyr](https://github.com/dimitris-flyr)
* Set type of ARRAY function for BigQuery [#4880](https://github.com/sqlfluff/sqlfluff/pull/4880) [@tunetheweb](https://github.com/tunetheweb)
* Full athena SHOW coverage [#4876](https://github.com/sqlfluff/sqlfluff/pull/4876) [@dogversioning](https://github.com/dogversioning)
* Sparksql add star support in multiparameter functions [#4874](https://github.com/sqlfluff/sqlfluff/pull/4874) [@spex66](https://github.com/spex66)
* Oracle create view with EDITIONING & FORCE [#4872](https://github.com/sqlfluff/sqlfluff/pull/4872) [@ulixius9](https://github.com/ulixius9)
* Fixes pip installation link on Getting Started [#4867](https://github.com/sqlfluff/sqlfluff/pull/4867) [@segoldma](https://github.com/segoldma)
* Athena: add "weird" test cases for `group by` [#4869](https://github.com/sqlfluff/sqlfluff/pull/4869) [@KulykDmytro](https://github.com/KulykDmytro)
* Athena: add support for `CUBE` `ROLLUP` `GROUPING SETS` [#4862](https://github.com/sqlfluff/sqlfluff/pull/4862) [@KulykDmytro](https://github.com/KulykDmytro)
* Add show tables/views to athena [#4854](https://github.com/sqlfluff/sqlfluff/pull/4854) [@dogversioning](https://github.com/dogversioning)
* Adding support for NOCOPY and INSTANT algorithm on CREATE INDEX on MySQL dialect [#4865](https://github.com/sqlfluff/sqlfluff/pull/4865) [@wfelipew](https://github.com/wfelipew)
* Add link to Trino keywords (Athena v3) [#4858](https://github.com/sqlfluff/sqlfluff/pull/4858) [@KulykDmytro](https://github.com/KulykDmytro)
* TSQL: Create Role Authorization [#4852](https://github.com/sqlfluff/sqlfluff/pull/4852) [@greg-finley](https://github.com/greg-finley)
* TSQL: DEADLOCK_PRIORITY [#4853](https://github.com/sqlfluff/sqlfluff/pull/4853) [@greg-finley](https://github.com/greg-finley)
* fix(dialect-clickhouse): Support SYSTEM queries [#4625](https://github.com/sqlfluff/sqlfluff/pull/4625) [@germainlefebvre4](https://github.com/germainlefebvre4)
* Fix #4807: LT02 & LT12 issues with empty files. [#4834](https://github.com/sqlfluff/sqlfluff/pull/4834) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Sqlite: COLLATE column constraint [#4845](https://github.com/sqlfluff/sqlfluff/pull/4845) [@greg-finley](https://github.com/greg-finley)
* Hive: Support REGEXP and IREGEXP [#4846](https://github.com/sqlfluff/sqlfluff/pull/4846) [@greg-finley](https://github.com/greg-finley)

## New Contributors

* [@dogversioning](https://github.com/dogversioning) made their first contribution in [#4854](https://github.com/sqlfluff/sqlfluff/pull/4854)
* [@segoldma](https://github.com/segoldma) made their first contribution in [#4867](https://github.com/sqlfluff/sqlfluff/pull/4867)
* [@spex66](https://github.com/spex66) made their first contribution in [#4874](https://github.com/sqlfluff/sqlfluff/pull/4874)
* [@dimitris-flyr](https://github.com/dimitris-flyr) made their first contribution in [#4879](https://github.com/sqlfluff/sqlfluff/pull/4879)
* [@JasonGluck](https://github.com/JasonGluck) made their first contribution in [#4886](https://github.com/sqlfluff/sqlfluff/pull/4886)

## [2.1.0] - 2023-05-03

## Highlights

This release brings support for dbt 1.5+. Some internals of dbt mean
that SQFluff versions prior to this release may experience errors with
dbt versions post 1.5. In addition to that there are some dialect and
templating improvements bundled too:
* Support for custom Jinja filters.
* An additional configurable indent behaviour within `CASE WHEN` clauses.
* Additional support for bracket quoted literals in TSQL and RF06.
* Dialect improvements to Snowflake, Hive, Redshift, Postgres,
  Clickhouse, Oracle and SQLite

## What’s Changed

* Add support for Jinja filters [#4810](https://github.com/sqlfluff/sqlfluff/pull/4810) [@dmohns](https://github.com/dmohns)
* Postgres: Allow INSERT RETURNING [#4820](https://github.com/sqlfluff/sqlfluff/pull/4820) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Support partial index [#4833](https://github.com/sqlfluff/sqlfluff/pull/4833) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Make SQLFluff compatible with DBT 1.5 [#4828](https://github.com/sqlfluff/sqlfluff/pull/4828) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake dialect: Add support for comment clause in the create warehouse statement [#4823](https://github.com/sqlfluff/sqlfluff/pull/4823) [@moreaupascal56](https://github.com/moreaupascal56)
* fix(dialect-clickhouse): Support DROP statements [#4821](https://github.com/sqlfluff/sqlfluff/pull/4821) [@germainlefebvre4](https://github.com/germainlefebvre4)
* Hive: INSERT INTO without TABLE keyword [#4819](https://github.com/sqlfluff/sqlfluff/pull/4819) [@greg-finley](https://github.com/greg-finley)
* Fix: Small typo in error message [#4814](https://github.com/sqlfluff/sqlfluff/pull/4814) [@JavierMonton](https://github.com/JavierMonton)
* Redshift: Support with no schema binding [#4813](https://github.com/sqlfluff/sqlfluff/pull/4813) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Detect tsql square bracket quotes for RF06 #4724 [#4781](https://github.com/sqlfluff/sqlfluff/pull/4781) [@daviewales](https://github.com/daviewales)
* Apply implicit indents to `WHEN` blocks and introduce `indented_then_contents` [#4755](https://github.com/sqlfluff/sqlfluff/pull/4755) [@borchero](https://github.com/borchero)
* Oracle: Update Drop Behaviour [#4803](https://github.com/sqlfluff/sqlfluff/pull/4803) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Oracle: Update bare functions [#4804](https://github.com/sqlfluff/sqlfluff/pull/4804) [@WittierDinosaur](https://github.com/WittierDinosaur)

## New Contributors

* [@daviewales](https://github.com/daviewales) made their first contribution in [#4781](https://github.com/sqlfluff/sqlfluff/pull/4781)

## [2.0.7] - 2023-04-20

## Highlights

This is a bugfix release to resolve two regressions included in 2.0.6
related to implicit indents. This also includes a bugfix for config
file on osx, contributed by first time contributor [@jpuris](https://github.com/jpuris) 🎉.

## What’s Changed

* Fix regression in implicit indents [#4798](https://github.com/sqlfluff/sqlfluff/pull/4798) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix bug with brackets and implicit indents [#4797](https://github.com/sqlfluff/sqlfluff/pull/4797) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix: correct macos/osx config file location [#4795](https://github.com/sqlfluff/sqlfluff/pull/4795) [@jpuris](https://github.com/jpuris)

## New Contributors

* [@jpuris](https://github.com/jpuris) made their first contribution in [#4795](https://github.com/sqlfluff/sqlfluff/pull/4795)

## [2.0.6] - 2023-04-19

## Highlights

* Introduction of a `--quiet` option for the CLI for situations
  where less output is useful.
* When using the `--force` option is used for `sqlfluff fix` each
  file is fixed during the linting process rather than at the end.
* Bugfixes to comment and templated section indentation.
* Performance improvements to parsing.
* Bugfix to macros triggering LT01.
* Renaming `layout.end-of-file` to `layout.end_of_file` in line
  with other rules.
* Dialect improvements to SparkSQL, BigQuery, Hive & Snowflake.


## What’s Changed

* Snowflake: Support Temporary View [#4789](https://github.com/sqlfluff/sqlfluff/pull/4789) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Inroduce `SAFE` prefix segment [#4773](https://github.com/sqlfluff/sqlfluff/pull/4773) [@dmohns](https://github.com/dmohns)
* Fix #4660: Better handling of empty files. [#4780](https://github.com/sqlfluff/sqlfluff/pull/4780) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #3538: (Fix files as we go) [#4777](https://github.com/sqlfluff/sqlfluff/pull/4777) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #2855: (Tech debt: check consistency in TemplatedFile init) [#4776](https://github.com/sqlfluff/sqlfluff/pull/4776) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add a --quiet option for fix [#4764](https://github.com/sqlfluff/sqlfluff/pull/4764) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4603 indent after Jinja 'do' directive [#4778](https://github.com/sqlfluff/sqlfluff/pull/4778) [@fredriv](https://github.com/fredriv)
* Snowflake Execute Task with Schema [#4771](https://github.com/sqlfluff/sqlfluff/pull/4771) [@Thashin](https://github.com/Thashin)
* SQLite: Support CreateTrigger [#4767](https://github.com/sqlfluff/sqlfluff/pull/4767) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix #2865 (AL05 exception for Redshift Semi-structured) [#4775](https://github.com/sqlfluff/sqlfluff/pull/4775) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4540: Untaken indents evaluation order. [#4768](https://github.com/sqlfluff/sqlfluff/pull/4768) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Use the new CollationReferenceSegment everywhere [#4770](https://github.com/sqlfluff/sqlfluff/pull/4770) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SQLite: Fix multiple parse issues in Expression_A_Grammar [#4769](https://github.com/sqlfluff/sqlfluff/pull/4769) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SQLite: Remove refs to RESPECT and QUALIFY [#4765](https://github.com/sqlfluff/sqlfluff/pull/4765) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite: Support STRICT [#4766](https://github.com/sqlfluff/sqlfluff/pull/4766) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Support hive set syntax [#4763](https://github.com/sqlfluff/sqlfluff/pull/4763) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4582: Comments after end of line [#4760](https://github.com/sqlfluff/sqlfluff/pull/4760) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow comment match with preceding line [#4758](https://github.com/sqlfluff/sqlfluff/pull/4758) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove the majority of greedy matchers [#4761](https://github.com/sqlfluff/sqlfluff/pull/4761) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix #4745: (max() error in reindent) [#4752](https://github.com/sqlfluff/sqlfluff/pull/4752) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix issue with macros triggering LT01 [#4757](https://github.com/sqlfluff/sqlfluff/pull/4757) [@alanmcruickshank](https://github.com/alanmcruickshank)
* end-of-file > end_of_file [#4753](https://github.com/sqlfluff/sqlfluff/pull/4753) [@alanmcruickshank](https://github.com/alanmcruickshank)


## [2.0.5] - 2023-04-14

## Highlights

This is a relatively swift bugfix to refine some of the changes made to
widow function indentation in `2.0.4`. In addition there are two dialect
refinements also made since that release.

## What’s Changed

* Refactor PG segments to reuse new common segments [#4726](https://github.com/sqlfluff/sqlfluff/pull/4726) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Recognize quoted data types [#4747](https://github.com/sqlfluff/sqlfluff/pull/4747) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)


## [2.0.4] - 2023-04-14

## Highlights

This is primarily a _bugfix_ and _dialect_ release:
* Several bugfixes related to templating and indentation, in particular some
  improvements to the indentation of aliases and window functions.
* Performance improvements to the parser.
* The `--persist-timing` option is now also available on `sqlfluff fix`.
* A refresh to getting started and rule documentation.
* Dialect improvements to PostgreSQL, Athena, SparkSQL, MySQL & Snowflake.

Thanks also to [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
and [@Thashin](https://github.com/Thashin) who made their first contributions
in this release. In particular, [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
made **twenty one** contributions in their first month! 🎉🎉🎉

## What’s Changed

* SparkSQL: Improvements to lateral view, hints, sort by [#4731](https://github.com/sqlfluff/sqlfluff/pull/4731) [@bmorck](https://github.com/bmorck)
* Add ExpressionSegment to CREATE TABLE ... DEFAULT / Fix multiple parse issues in Expression_A_Grammar [#4717](https://github.com/sqlfluff/sqlfluff/pull/4717) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add support for the PG VACUUM statement [#4742](https://github.com/sqlfluff/sqlfluff/pull/4742) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Simplify and fix PG array accessor segment & support expressions [#4748](https://github.com/sqlfluff/sqlfluff/pull/4748) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SparkSQL: Allow for any ordering of create table clauses [#4721](https://github.com/sqlfluff/sqlfluff/pull/4721) [@bmorck](https://github.com/bmorck)
* Suggested started config file [#4702](https://github.com/sqlfluff/sqlfluff/pull/4702) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Indents on window functions [#4560](https://github.com/sqlfluff/sqlfluff/pull/4560) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SparkSQL: Fix Group By Clause [#4732](https://github.com/sqlfluff/sqlfluff/pull/4732) [@bmorck](https://github.com/bmorck)
* Improve support for EXCLUDE table constraints in PG [#4725](https://github.com/sqlfluff/sqlfluff/pull/4725) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add support for dropping multiple indexes in PG [#4737](https://github.com/sqlfluff/sqlfluff/pull/4737) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Recognize "on" value and integers for PG SET statement [#4740](https://github.com/sqlfluff/sqlfluff/pull/4740) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Improve interval expressions on MySQL [#4746](https://github.com/sqlfluff/sqlfluff/pull/4746) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Keep out zero length keywords [#4723](https://github.com/sqlfluff/sqlfluff/pull/4723) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add PG support for CREATE SCHEMA AUTHORIZATION [#4735](https://github.com/sqlfluff/sqlfluff/pull/4735) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add support for dropping multiple views with PostgreSQL [#4736](https://github.com/sqlfluff/sqlfluff/pull/4736) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add CHAR VARYING data type for PG [#4738](https://github.com/sqlfluff/sqlfluff/pull/4738) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* fix(athena): map type matching failed, array type only contains a datatype [#4739](https://github.com/sqlfluff/sqlfluff/pull/4739) [@timcosta](https://github.com/timcosta)
* Allow DML queries to be selectable in CTEs on PG [#4741](https://github.com/sqlfluff/sqlfluff/pull/4741) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add the CREATE/DROP CAST statements to ANSI and PG [#4744](https://github.com/sqlfluff/sqlfluff/pull/4744) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add support for PG SET ROLE / RESET ROLE [#4734](https://github.com/sqlfluff/sqlfluff/pull/4734) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Support Spark Iceberg DDL [#4690](https://github.com/sqlfluff/sqlfluff/pull/4690) [@bmorck](https://github.com/bmorck)
* Fix #4680 [#4707](https://github.com/sqlfluff/sqlfluff/pull/4707) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Indent Aliases [#4706](https://github.com/sqlfluff/sqlfluff/pull/4706) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SparkSQL: Improve window frame bounds [#4722](https://github.com/sqlfluff/sqlfluff/pull/4722) [@bmorck](https://github.com/bmorck)
* Add support for PG CREATE/ALTER/DROP PUBLICATION stmts [#4716](https://github.com/sqlfluff/sqlfluff/pull/4716) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SparkSQL: Create external table support [#4692](https://github.com/sqlfluff/sqlfluff/pull/4692) [@bmorck](https://github.com/bmorck)
* SparkSQL: Fix file literal lexing [#4718](https://github.com/sqlfluff/sqlfluff/pull/4718) [@bmorck](https://github.com/bmorck)
* Add PG DROP/REASSIGN OWNED statements [#4720](https://github.com/sqlfluff/sqlfluff/pull/4720) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* SparkSQL: Add distinct to comparison operator [#4719](https://github.com/sqlfluff/sqlfluff/pull/4719) [@bmorck](https://github.com/bmorck)
* Rethink Rule Docs [#4695](https://github.com/sqlfluff/sqlfluff/pull/4695) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Performance: Reduce calls to _prune_options [#4705](https://github.com/sqlfluff/sqlfluff/pull/4705) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Add ReferencedVariableNameSegment to sample function [#4712](https://github.com/sqlfluff/sqlfluff/pull/4712) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Mark AM02 as fix compatible [#4714](https://github.com/sqlfluff/sqlfluff/pull/4714) [@yoichi](https://github.com/yoichi)
* Fix LT01 spacing check in templated areas [#4698](https://github.com/sqlfluff/sqlfluff/pull/4698) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Don't do newline conversion on write [#4703](https://github.com/sqlfluff/sqlfluff/pull/4703) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: CREATE/ALTER VIEW may take UNION [#4713](https://github.com/sqlfluff/sqlfluff/pull/4713) [@yoichi](https://github.com/yoichi)
* Preserve zero-length template segments [#4708](https://github.com/sqlfluff/sqlfluff/pull/4708) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* CV06: don't flag files that don't have code [#4709](https://github.com/sqlfluff/sqlfluff/pull/4709) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Add a no-output option [#4704](https://github.com/sqlfluff/sqlfluff/pull/4704) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Jinja templater: treat "import" and "from" as templated [#4696](https://github.com/sqlfluff/sqlfluff/pull/4696) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Capitalization rules ignore templated code only if configured to [#4697](https://github.com/sqlfluff/sqlfluff/pull/4697) [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack)
* Update getting started docs [#4700](https://github.com/sqlfluff/sqlfluff/pull/4700) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add a default for config_keywords and remove noisy error. [#4701](https://github.com/sqlfluff/sqlfluff/pull/4701) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake Select System Functions [#4687](https://github.com/sqlfluff/sqlfluff/pull/4687) [@Thashin](https://github.com/Thashin)
* SparkSQL: Add using and options clause to create view statement [#4691](https://github.com/sqlfluff/sqlfluff/pull/4691) [@bmorck](https://github.com/bmorck)
* MySQL: Add RETURN Statement [#4693](https://github.com/sqlfluff/sqlfluff/pull/4693) [@yoichi](https://github.com/yoichi)
* Safety valve for fixes in CV03 [#4685](https://github.com/sqlfluff/sqlfluff/pull/4685) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow persist timing on `fix` too. [#4679](https://github.com/sqlfluff/sqlfluff/pull/4679) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix{dialect-snowflake}:Alter Table Column Set/Unset Tag [#4682](https://github.com/sqlfluff/sqlfluff/pull/4682) [@Thashin](https://github.com/Thashin)
* fix{dialect-snowflake}:Execute Task [#4683](https://github.com/sqlfluff/sqlfluff/pull/4683) [@Thashin](https://github.com/Thashin)
* Make version number an argument not an option in release script. [#4677](https://github.com/sqlfluff/sqlfluff/pull/4677) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@Thashin](https://github.com/Thashin) made their first contribution in [#4683](https://github.com/sqlfluff/sqlfluff/pull/4683)
* [@james-johnston-thumbtack](https://github.com/james-johnston-thumbtack) made their first contribution in [#4697](https://github.com/sqlfluff/sqlfluff/pull/4697)

## [2.0.3] - 2023-04-05

## Highlights

This is primarily a _bugfix_ and _dialect_ release:
* Several bugfixes related to templating and indentation.
* Configurable indentation before `THEN` in `CASE` statements
  (see [#4598](https://github.com/sqlfluff/sqlfluff/pull/4598)).
* Performance improvements to `TypedParser`, `LT03` & `LT04`.
* Rule timings now appear in the `--persist-timing` option for deeper
  performance understanding.
* The introduction of a Greenplum dialect.
* Dialect improvements to TSQL, Athena, Snowflake, MySQL, SparkSQL
  BigQuery, Databricks, Clickhouse & Postgres.

We also saw a _huge number of first time contributors_ with **9** contributing
in this release 🎉🏆🎉.

## What’s Changed

* Better error message for missing keywords [#4676](https://github.com/sqlfluff/sqlfluff/pull/4676) [@tunetheweb](https://github.com/tunetheweb)
* Add performance shortcuts to LT03 & LT04 [#4672](https://github.com/sqlfluff/sqlfluff/pull/4672) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Clickhouse: Add support for [LEFT] ARRAY JOIN [#4618](https://github.com/sqlfluff/sqlfluff/pull/4618) [@simpl1g](https://github.com/simpl1g)
* Postgres - allow untyped OVERLAPS clauses [#4674](https://github.com/sqlfluff/sqlfluff/pull/4674) [@tunetheweb](https://github.com/tunetheweb)
* Mark `is_alias_required` as a private class so it doesn't appear in docs [#4673](https://github.com/sqlfluff/sqlfluff/pull/4673) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug in templated with clauses LT07 [#4671](https://github.com/sqlfluff/sqlfluff/pull/4671) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: `OPENJSON()` [#4652](https://github.com/sqlfluff/sqlfluff/pull/4652) [@keen85](https://github.com/keen85)
* fix(RF06/L059): allows configuring prefer_quoted_keywords to deconflict with L029 [#4396](https://github.com/sqlfluff/sqlfluff/pull/4396) [@timcosta](https://github.com/timcosta)
* TSQL: `Create External Table` [#4642](https://github.com/sqlfluff/sqlfluff/pull/4642) [@aly76](https://github.com/aly76)
* Consistent indentation in `MERGE` `INSERT` clause [#4666](https://github.com/sqlfluff/sqlfluff/pull/4666) [@dmohns](https://github.com/dmohns)
* BigQuery: Fix null assignment in options segment [#4669](https://github.com/sqlfluff/sqlfluff/pull/4669) [@greg-finley](https://github.com/greg-finley)
* BigQuery: Delete table reference [#4668](https://github.com/sqlfluff/sqlfluff/pull/4668) [@greg-finley](https://github.com/greg-finley)
* TSQL: `CREATE EXTERNAL FILE FORMAT` [#4647](https://github.com/sqlfluff/sqlfluff/pull/4647) [@keen85](https://github.com/keen85)
* Remove TIME as reserved keyword in SparkSQL [#4662](https://github.com/sqlfluff/sqlfluff/pull/4662) [@bmorck](https://github.com/bmorck)
* Start of the Greenplum dialect implementation  [#4661](https://github.com/sqlfluff/sqlfluff/pull/4661) [@JackWolverson](https://github.com/JackWolverson)
* Enable configuring whether to require indent before THEN [#4598](https://github.com/sqlfluff/sqlfluff/pull/4598) [@fredriv](https://github.com/fredriv)
* Sequence Meta Handling [#4622](https://github.com/sqlfluff/sqlfluff/pull/4622) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add support for non-quoted file paths in SparkSQL [#4650](https://github.com/sqlfluff/sqlfluff/pull/4650) [@bmorck](https://github.com/bmorck)
* Remove three RegexParsers [#4658](https://github.com/sqlfluff/sqlfluff/pull/4658) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Make parse test readout more helpful [#4657](https://github.com/sqlfluff/sqlfluff/pull/4657) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: support for `sqlcmd` commands `:r` and `:setvar` [#4653](https://github.com/sqlfluff/sqlfluff/pull/4653) [@keen85](https://github.com/keen85)
* Update README with Databricks note [#4632](https://github.com/sqlfluff/sqlfluff/pull/4632) [@liamperritt](https://github.com/liamperritt)
* Athena: Fix parsing error with aliases starting with underscore [#4636](https://github.com/sqlfluff/sqlfluff/pull/4636) [@maiarareinaldo](https://github.com/maiarareinaldo)
* Snowflake: Stop ever-increasing indent in CREATE USER [#4638](https://github.com/sqlfluff/sqlfluff/pull/4638) [@roman-ef](https://github.com/roman-ef)
* TSQL: `PERIOD FOR SYSTEM_TIME` (temporal tables) [#4654](https://github.com/sqlfluff/sqlfluff/pull/4654) [@keen85](https://github.com/keen85)
* MySQL: SelectStatementSegment in CREATE/ALTER VIEW may be bracketed [#4655](https://github.com/sqlfluff/sqlfluff/pull/4655) [@yoichi](https://github.com/yoichi)
* TSQL: `CREATE EXTERNAL DATA SOURCE` [#4634](https://github.com/sqlfluff/sqlfluff/pull/4634) [@keen85](https://github.com/keen85)
* Safety valve on source fixes [#4640](https://github.com/sqlfluff/sqlfluff/pull/4640) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add SparkSQL support for LONG primitive type [#4639](https://github.com/sqlfluff/sqlfluff/pull/4639) [@bmorck](https://github.com/bmorck)
* Fix PIVOT clauses for BigQuery and SparkSQL [#4630](https://github.com/sqlfluff/sqlfluff/pull/4630) [@tunetheweb](https://github.com/tunetheweb)
* Correct BigQuery WINDOW parsing [#4629](https://github.com/sqlfluff/sqlfluff/pull/4629) [@tunetheweb](https://github.com/tunetheweb)
* Add Databricks dialect support for Unity Catalog [#4568](https://github.com/sqlfluff/sqlfluff/pull/4568) [@liamperritt](https://github.com/liamperritt)
* .simple() matching for TypedMatcher [#4612](https://github.com/sqlfluff/sqlfluff/pull/4612) [@alanmcruickshank](https://github.com/alanmcruickshank)
* --bench output with rule timings [#4601](https://github.com/sqlfluff/sqlfluff/pull/4601) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: Unnamed constraints [#4616](https://github.com/sqlfluff/sqlfluff/pull/4616) [@greg-finley](https://github.com/greg-finley)
* TSQL: Create database scoped credential [#4615](https://github.com/sqlfluff/sqlfluff/pull/4615) [@greg-finley](https://github.com/greg-finley)
* fix(dialect-clickhouse): Add materialized view statement [#4605](https://github.com/sqlfluff/sqlfluff/pull/4605) [@germainlefebvre4](https://github.com/germainlefebvre4)
* Nicer formatted dbt errors [#4606](https://github.com/sqlfluff/sqlfluff/pull/4606) [@alanmcruickshank](https://github.com/alanmcruickshank)
* add parse lambda function Clickhouse [#4611](https://github.com/sqlfluff/sqlfluff/pull/4611) [@konnectr](https://github.com/konnectr)
* Support `WITH ORDINALITY` clauses in Postgres [#4599](https://github.com/sqlfluff/sqlfluff/pull/4599) [@tunetheweb](https://github.com/tunetheweb)


## New Contributors
* [@germainlefebvre4](https://github.com/germainlefebvre4) made their first contribution in [#4605](https://github.com/sqlfluff/sqlfluff/pull/4605)
* [@liamperritt](https://github.com/liamperritt) made their first contribution in [#4568](https://github.com/sqlfluff/sqlfluff/pull/4568)
* [@bmorck](https://github.com/bmorck) made their first contribution in [#4639](https://github.com/sqlfluff/sqlfluff/pull/4639)
* [@keen85](https://github.com/keen85) made their first contribution in [#4634](https://github.com/sqlfluff/sqlfluff/pull/4634)
* [@roman-ef](https://github.com/roman-ef) made their first contribution in [#4638](https://github.com/sqlfluff/sqlfluff/pull/4638)
* [@maiarareinaldo](https://github.com/maiarareinaldo) made their first contribution in [#4636](https://github.com/sqlfluff/sqlfluff/pull/4636)
* [@fredriv](https://github.com/fredriv) made their first contribution in [#4598](https://github.com/sqlfluff/sqlfluff/pull/4598)
* [@aly76](https://github.com/aly76) made their first contribution in [#4642](https://github.com/sqlfluff/sqlfluff/pull/4642)
* [@simpl1g](https://github.com/simpl1g) made their first contribution in [#4618](https://github.com/sqlfluff/sqlfluff/pull/4618)

## [2.0.2] - 2023-03-23

## Highlights

This is primarily a _bugfix_ release. Most notably this solves some of the
issues introduced in 2.0.1 around spacing within datatypes. Expressions
like `1.0::double precision` should now be spaced correctly.

Beyond that, this contains a selection of smaller bugfixes and dialect
improvements. Even for a relatively small release we saw three new
contributors (thanks [@aurany](https://github.com/aurany), [@JackWolverson](https://github.com/JackWolverson)
& [@mikaeltw](https://github.com/mikaeltw) 🎉).

The one new _feature_ (as such) is being able to now configure `LT05`
(aka `layout.long_lines`) to optionally move trailing comments _after_
the line they are found on, rather than the default behaviour of moving
them up and _before_. Users can enable this with the `trailing_comments`
configuration setting in the `indentation` section.

This release _also_ contains some performance optimisations in the parser,
especially on queries with heavily nested expressions. There will be more
to come in this space, but we hope this leads to a better experience for
many users. 🚀

## What’s Changed

* Parse Caching [#4576](https://github.com/sqlfluff/sqlfluff/pull/4576) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Data type spacing [#4592](https://github.com/sqlfluff/sqlfluff/pull/4592) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: allow quoted literal in alias name [#4591](https://github.com/sqlfluff/sqlfluff/pull/4591) [@yoichi](https://github.com/yoichi)
* Make implicit indents visible in the parse tree [#4584](https://github.com/sqlfluff/sqlfluff/pull/4584) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4559: TSQL implicit indents on WHERE [#4583](https://github.com/sqlfluff/sqlfluff/pull/4583) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Added keywords to DB2 dialect from IBM docs [#4575](https://github.com/sqlfluff/sqlfluff/pull/4575) [@aurany](https://github.com/aurany)
* Remove matches_target_tuples (#3873) [#4561](https://github.com/sqlfluff/sqlfluff/pull/4561) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Use terminators in BaseExpression [#4577](https://github.com/sqlfluff/sqlfluff/pull/4577) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Address #1630: Optionally move comments after long line [#4558](https://github.com/sqlfluff/sqlfluff/pull/4558) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Added schema to set statement [#4580](https://github.com/sqlfluff/sqlfluff/pull/4580) [@JackWolverson](https://github.com/JackWolverson)
* Refactor lint_line_length and fix comma bug [#4564](https://github.com/sqlfluff/sqlfluff/pull/4564) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix untaken indent bug [#4562](https://github.com/sqlfluff/sqlfluff/pull/4562) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SQLite: Fix SELECT LIMIT [#4566](https://github.com/sqlfluff/sqlfluff/pull/4566) [@greg-finley](https://github.com/greg-finley)
* Fix #4453: Snowflake semi-stuctured casts in CV11 [#4571](https://github.com/sqlfluff/sqlfluff/pull/4571) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Name of LT07 [#4557](https://github.com/sqlfluff/sqlfluff/pull/4557) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Patch fetch and over [#4555](https://github.com/sqlfluff/sqlfluff/pull/4555) [@mikaeltw](https://github.com/mikaeltw)

## New Contributors

* [@mikaeltw](https://github.com/mikaeltw) made their first contribution in [#4555](https://github.com/sqlfluff/sqlfluff/pull/4555)
* [@JackWolverson](https://github.com/JackWolverson) made their first contribution in [#4580](https://github.com/sqlfluff/sqlfluff/pull/4580)
* [@aurany](https://github.com/aurany) made their first contribution in [#4575](https://github.com/sqlfluff/sqlfluff/pull/4575)

## [2.0.1] - 2023-03-17

## Highlights

This is mostly a bugfix release addressing some of the issues from the recent
2.0 release. Notable fixes are:
- Spacing for (as applied by `LT01`) for datatypes, hyphenated identifiers and
  casting operators.
- Several bugs in the indentation routines (`LT02`), in particular with implicit
  indents.
- Fixing a conflict between `LT09` and `LT02`, by only limiting `LT09` to bringing
  targets onto a single line if there is only one select target **and** that it
  contains no newlines.
- Supporting arrays, and the new rules configuration more effectively in `pyproject.toml`.
- Configuring dialects on a file by file basis using inline comments now works.

This release also brings one small new feature in allowing additional flags to
be passed to SQLFluff when called as a `pre-commit` hook.

Thanks especially to [@JavierMonton](https://github.com/JavierMonton) and
[@LauraRichter](https://github.com/LauraRichter) who made their first contributions
to the project as part of this release! 🎉🏆

## What’s Changed

* Add support for arrays in TOML configuration [#4387](https://github.com/sqlfluff/sqlfluff/pull/4387) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Rethink test segregation in CI [#4547](https://github.com/sqlfluff/sqlfluff/pull/4547) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4515 and add more test cases [#4525](https://github.com/sqlfluff/sqlfluff/pull/4525) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add additional flags to `sqlfluff` invocations in pre-commit hooks [#4546](https://github.com/sqlfluff/sqlfluff/pull/4546) [@borchero](https://github.com/borchero)
* Resolve #4484 (issues with indented_joins indents) [#4544](https://github.com/sqlfluff/sqlfluff/pull/4544) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Per file dialect selection fix [#4518](https://github.com/sqlfluff/sqlfluff/pull/4518) [@LauraRichter](https://github.com/LauraRichter)
* MySQL: Add CREATE INDEX [#4538](https://github.com/sqlfluff/sqlfluff/pull/4538) [@yoichi](https://github.com/yoichi)
* Resolve implicit indent issues when catching negative indents [#4543](https://github.com/sqlfluff/sqlfluff/pull/4543) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Github Action Deprecations [#4545](https://github.com/sqlfluff/sqlfluff/pull/4545) [@alanmcruickshank](https://github.com/alanmcruickshank)
* LT09 and multiline select targets [#4529](https://github.com/sqlfluff/sqlfluff/pull/4529) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Remove Codecov from CI [#4535](https://github.com/sqlfluff/sqlfluff/pull/4535) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bigquery hyphentated identifiers [#4530](https://github.com/sqlfluff/sqlfluff/pull/4530) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Attempt in-house coverage [#4532](https://github.com/sqlfluff/sqlfluff/pull/4532) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres datatype spacing issues [#4528](https://github.com/sqlfluff/sqlfluff/pull/4528) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Support new rules config in toml files. [#4526](https://github.com/sqlfluff/sqlfluff/pull/4526) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #1146 (log propagation) [#4513](https://github.com/sqlfluff/sqlfluff/pull/4513) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Optional quotes for `create user` statement [#4514](https://github.com/sqlfluff/sqlfluff/pull/4514) [@JavierMonton](https://github.com/JavierMonton)

## New Contributors

* [@JavierMonton](https://github.com/JavierMonton) made their first contribution in [#4514](https://github.com/sqlfluff/sqlfluff/pull/4514)
* [@LauraRichter](https://github.com/LauraRichter) made their first contribution in [#4518](https://github.com/sqlfluff/sqlfluff/pull/4518)

## [2.0.0] - 2023-03-13

## Highlights

Upgrading to 2.0 brings several important **breaking changes**:

* All bundled rules have been recoded, both from generic `L00X` formats
  into groups within similar codes (e.g. an *aliasing* group with codes
  of the format `AL0X`), but also given *names* to allow much clearer
  referencing (e.g. `aliasing.column`).
* [Configuring rules](https://docs.sqlfluff.com/en/latest/configuration.html#rule-configuration)
  now uses the rule *name* rather than the rule *code* to
  specify the section. Any unrecognised references in config files (whether
  they are references which *do* match existing rules by code or alias, or
  whether the match no rules at all) will raise warnings at runtime.
* A complete re-write of layout and whitespace handling rules (see
  [layout](https://docs.sqlfluff.com/en/latest/layout.html)), and with
  that a change in how layout is configured (see
  [configuring layout](https://docs.sqlfluff.com/en/latest/layout.html#configuring-layout))
  and the combination of some rules that were previously separate. One
  example of this is that the legacy rules `L001`, `L005`, `L006`, `L008`,
  `L023`, `L024`, `L039`, `L048` & `L071` have been combined simply into
  [LT01](https://docs.sqlfluff.com/en/latest/rules.html#sqlfluff.rules.sphinx.Rule_LT01).
* Dropping support for dbt versions before `1.1`.

To help users upgrade to 2.0, we've put together a recommended process
as part of our [release notes](https://docs.sqlfluff.com/en/latest/releasenotes.html#upgrading-from-1-x-to-2-0).

Beyond the breaking changes, this release brings *a load* of additional
changes:

* Introduces the the `sqlfluff format` CLI command (a la `sqlfmt` or `black`)
  to auto-format sql files using a known set of _fairly safe_ rules.
* Databricks as a distinct new dialect (rather than as previously an alias
  for `sparksql`).
* Performance improvements in our parsing engine.
* Dialect improvements to _almost all of them_.

As a new major release, especially with significant rewrites of large
portions of the codebase, we recommend using [compatible release](https://peps.python.org/pep-0440/#compatible-release)
specifiers in your dependencies (i.e. `sqlfluff~=2.0.0`) so that you
can automatically take advantage of any bugfix releases in the coming
weeks. The alpha releases of 2.0.0 have been tested on a range of large
projects, but we know that the range of use cases _"in the wild"_ is
very diverse. If you do experience issues, please post them
[on GitHub](https://github.com/sqlfluff/sqlfluff/issues/new/choose)
in the usual manner.

Finally thanks to everyone who has worked on this release, especially
[@konnectr](https://github.com/konnectr),
[@ValentinCrr](https://github.com/ValentinCrr),
[@FabianScheidt](https://github.com/FabianScheidt),
[@dflem97](https://github.com/dflem97),
[@timcosta](https://github.com/timcosta),
[@AidanHarveyNelson](https://github.com/AidanHarveyNelson),
[@joar](https://github.com/joar),
[@jmpfar](https://github.com/jmpfar),
[@jared-rimmer](https://github.com/jared-rimmer),
[@vesatoivonen](https://github.com/vesatoivonen),
[@briankravec](https://github.com/briankravec),
[@saintamh](https://github.com/saintamh),
[@tdurieux](https://github.com/tdurieux),
[@baa-ableton](https://github.com/baa-ableton),
& [@WillAyd](https://github.com/WillAyd) who made their first contributions
during the development of 2.0.0. Thanks for your contributions, and
especially your patience in the slightly slower release of your efforts
into the wild. 🙏🎉

## What’s Changed

* Revise templating and lexing of calls. [#4506](https://github.com/sqlfluff/sqlfluff/pull/4506) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Struct Access Spacing [#4512](https://github.com/sqlfluff/sqlfluff/pull/4512) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Array and Struct Spacing [#4511](https://github.com/sqlfluff/sqlfluff/pull/4511) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add a deprecation warning for removed config option. [#4509](https://github.com/sqlfluff/sqlfluff/pull/4509) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bigquery spacing (#4508) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4433 (more untaken positive indents) [#4499](https://github.com/sqlfluff/sqlfluff/pull/4499) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix parse error on double parentheses [#4504](https://github.com/sqlfluff/sqlfluff/pull/4504) [@yoichi](https://github.com/yoichi)
* 2.0.0 Migration Guide [#4498](https://github.com/sqlfluff/sqlfluff/pull/4498) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle missing aliases and align constraints better [#4493](https://github.com/sqlfluff/sqlfluff/pull/4493) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: Add support For Clause [#4501](https://github.com/sqlfluff/sqlfluff/pull/4501) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Allow Jinja rule to loop safely [#4495](https://github.com/sqlfluff/sqlfluff/pull/4495) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Trigger CI tests for merge groups [#4503](https://github.com/sqlfluff/sqlfluff/pull/4503) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update Readme and Contributing [#4502](https://github.com/sqlfluff/sqlfluff/pull/4502) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update layout docs [#4500](https://github.com/sqlfluff/sqlfluff/pull/4500) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bug in operator precedence [#4497](https://github.com/sqlfluff/sqlfluff/pull/4497) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: correct query syntax for single column `UNPIVOT` clauses [#4494](https://github.com/sqlfluff/sqlfluff/pull/4494) [@imrehg](https://github.com/imrehg)
* Fix #4485 [#4491](https://github.com/sqlfluff/sqlfluff/pull/4491) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update reserved keywords in Athena language [#4490](https://github.com/sqlfluff/sqlfluff/pull/4490) [@ValentinCrr](https://github.com/ValentinCrr)
* Clickhouse support all join types  [#4488](https://github.com/sqlfluff/sqlfluff/pull/4488) [@konnectr](https://github.com/konnectr)
* Snowflake semi-structured spacing [#4487](https://github.com/sqlfluff/sqlfluff/pull/4487) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prep version 2.0.0a6 [#4476](https://github.com/sqlfluff/sqlfluff/pull/4476) [@github-actions](https://github.com/github-actions)
* Fix #4367 [#4479](https://github.com/sqlfluff/sqlfluff/pull/4479) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Teradata: Improve COLLECT STATS parsing [#4478](https://github.com/sqlfluff/sqlfluff/pull/4478) [@dflem97](https://github.com/dflem97)
* Add a sqlfluff format CLI command [#4473](https://github.com/sqlfluff/sqlfluff/pull/4473) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode and disable L031 -> AL07 [#4471](https://github.com/sqlfluff/sqlfluff/pull/4471) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Named Config (part 2) [#4470](https://github.com/sqlfluff/sqlfluff/pull/4470) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Rule config lookup improvements & config warnings [#4465](https://github.com/sqlfluff/sqlfluff/pull/4465) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode L050 [#4468](https://github.com/sqlfluff/sqlfluff/pull/4468) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Implicit indent fixes #4467 [#4469](https://github.com/sqlfluff/sqlfluff/pull/4469) [@alanmcruickshank](https://github.com/alanmcruickshank)
* ANSI: Add IfExistsGrammar to DropTrigger [#4466](https://github.com/sqlfluff/sqlfluff/pull/4466) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Rules Reorg Mopup [#4462](https://github.com/sqlfluff/sqlfluff/pull/4462) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Layout Rules Recode (part 2) [#4456](https://github.com/sqlfluff/sqlfluff/pull/4456) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix(athena): resolve errors parsing around maps, structs, and arrays [#4391](https://github.com/sqlfluff/sqlfluff/pull/4391) [@timcosta](https://github.com/timcosta)
* Layout Rules Recode (part 1) [#4432](https://github.com/sqlfluff/sqlfluff/pull/4432) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: EXEC string literal [#4458](https://github.com/sqlfluff/sqlfluff/pull/4458) [@jpers36](https://github.com/jpers36)
* Teradata: Added SET QUERY_BAND statement  [#4459](https://github.com/sqlfluff/sqlfluff/pull/4459) [@dflem97](https://github.com/dflem97)
* Teradata: Added TOP select clause modifier [#4461](https://github.com/sqlfluff/sqlfluff/pull/4461) [@dflem97](https://github.com/dflem97)
* Teradata: Addition of comparison operator extensions [#4451](https://github.com/sqlfluff/sqlfluff/pull/4451) [@dflem97](https://github.com/dflem97)
* Add extensions and plugin section to the README.md [#4454](https://github.com/sqlfluff/sqlfluff/pull/4454) [@jared-rimmer](https://github.com/jared-rimmer)
* Convention rules bundle [#4448](https://github.com/sqlfluff/sqlfluff/pull/4448) [@alanmcruickshank](https://github.com/alanmcruickshank)
* References rule bundle [#4446](https://github.com/sqlfluff/sqlfluff/pull/4446) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Structure and Ambiguous rule bundles [#4444](https://github.com/sqlfluff/sqlfluff/pull/4444) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: Bare functions [#4439](https://github.com/sqlfluff/sqlfluff/pull/4439) [@jpers36](https://github.com/jpers36)
* Pull dbt CI tests forward to 1.1 and 1.4 [#4442](https://github.com/sqlfluff/sqlfluff/pull/4442) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Teradata: Added "AND STATS" options when creating table [#4440](https://github.com/sqlfluff/sqlfluff/pull/4440) [@dflem97](https://github.com/dflem97)
* Add Databricks as a distinct dialect [#4438](https://github.com/sqlfluff/sqlfluff/pull/4438) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remove importlib deprecated methods [#4437](https://github.com/sqlfluff/sqlfluff/pull/4437) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SQLite: Support PRAGMA statements [#4431](https://github.com/sqlfluff/sqlfluff/pull/4431) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Proposed graceful handling of noqa by L016 (#4248) [#4424](https://github.com/sqlfluff/sqlfluff/pull/4424) [@alanmcruickshank](https://github.com/alanmcruickshank)
* DuckDb: Allow quoted literals as identifiers [#4410](https://github.com/sqlfluff/sqlfluff/pull/4410) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite Refactor to reduce statement and keyword scope [#4409](https://github.com/sqlfluff/sqlfluff/pull/4409) [@WittierDinosaur](https://github.com/WittierDinosaur)
* L046 and L056 recode [#4430](https://github.com/sqlfluff/sqlfluff/pull/4430) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode Aliasing Rules [#4427](https://github.com/sqlfluff/sqlfluff/pull/4427) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adjust MySQL dialect to support combination of not-null, default and … [#4426](https://github.com/sqlfluff/sqlfluff/pull/4426) [@FabianScheidt](https://github.com/FabianScheidt)
* Revert some changes to tox [#4428](https://github.com/sqlfluff/sqlfluff/pull/4428) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Migrate capitalisation rules to plugin and recode [#4413](https://github.com/sqlfluff/sqlfluff/pull/4413) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Prep version 2.0.0a5 [#4419](https://github.com/sqlfluff/sqlfluff/pull/4419) [@github-actions](https://github.com/github-actions)
* Handle long lines without trailing newlines gracefully (#4386) [#4423](https://github.com/sqlfluff/sqlfluff/pull/4423) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4184 (index error in L007) [#4422](https://github.com/sqlfluff/sqlfluff/pull/4422) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle untaken positive indents with taken negative pair. [#4420](https://github.com/sqlfluff/sqlfluff/pull/4420) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: AS MATERIALIZED support [#4417](https://github.com/sqlfluff/sqlfluff/pull/4417) [@saintamh](https://github.com/saintamh)
* Align warnings config with example shown [#4421](https://github.com/sqlfluff/sqlfluff/pull/4421) [@briankravec](https://github.com/briankravec)
* BigQuery: parse "AS description" part of assert expressions [#4418](https://github.com/sqlfluff/sqlfluff/pull/4418) [@yoichi](https://github.com/yoichi)
* Deprecate doc decorators (replace with metaclass) [#4415](https://github.com/sqlfluff/sqlfluff/pull/4415) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Enable noqa using aliases and groups [#4414](https://github.com/sqlfluff/sqlfluff/pull/4414) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add rule names to CLI outputs [#4400](https://github.com/sqlfluff/sqlfluff/pull/4400) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Remove execution keyword inherited from ANSI [#4411](https://github.com/sqlfluff/sqlfluff/pull/4411) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Rule names, aliases and more complicated selection. [#4399](https://github.com/sqlfluff/sqlfluff/pull/4399) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Support Recursive View [#4412](https://github.com/sqlfluff/sqlfluff/pull/4412) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL: Implement BULK INSERT statement [#4381](https://github.com/sqlfluff/sqlfluff/pull/4381) [@borchero](https://github.com/borchero)
* L062: Add match_source (#4172) [#4335](https://github.com/sqlfluff/sqlfluff/pull/4335) [@vesatoivonen](https://github.com/vesatoivonen)
* TSQL: Add SET to ALTER TABLE [#4407](https://github.com/sqlfluff/sqlfluff/pull/4407) [@jared-rimmer](https://github.com/jared-rimmer)
* Snowflake: ALTER STORAGE INTEGRATION segment [#4406](https://github.com/sqlfluff/sqlfluff/pull/4406) [@jared-rimmer](https://github.com/jared-rimmer)
* Fix incorrect link to pre-commit docs [#4405](https://github.com/sqlfluff/sqlfluff/pull/4405) [@pdebelak](https://github.com/pdebelak)
* Add Snowflake dialect ALTER ROLE segment [#4403](https://github.com/sqlfluff/sqlfluff/pull/4403) [@jared-rimmer](https://github.com/jared-rimmer)
* Improving Postgres create index statement [#4356](https://github.com/sqlfluff/sqlfluff/pull/4356) [@jmpfar](https://github.com/jmpfar)
* Resolve #4291: Comments forcing unexpected indents. [#4384](https://github.com/sqlfluff/sqlfluff/pull/4384) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4294: Comments affecting indentation [#4337](https://github.com/sqlfluff/sqlfluff/pull/4337) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4292: Window function long line fixes [#4383](https://github.com/sqlfluff/sqlfluff/pull/4383) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: ALTER INDEX [#4364](https://github.com/sqlfluff/sqlfluff/pull/4364) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Added Varying Keyword to allowed data type segments [#4375](https://github.com/sqlfluff/sqlfluff/pull/4375) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Add ruff linter [#4372](https://github.com/sqlfluff/sqlfluff/pull/4372) [@greg-finley](https://github.com/greg-finley)
* Fix postgres column constraint default syntax [#4379](https://github.com/sqlfluff/sqlfluff/pull/4379) [@pdebelak](https://github.com/pdebelak)
* Allow function names to have a leading underscore [#4377](https://github.com/sqlfluff/sqlfluff/pull/4377) [@gavin-tsang](https://github.com/gavin-tsang)
* TSQL: Merge Hints [#4354](https://github.com/sqlfluff/sqlfluff/pull/4354) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: Temporal Table [#4358](https://github.com/sqlfluff/sqlfluff/pull/4358) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: ALTER TABLE [#4369](https://github.com/sqlfluff/sqlfluff/pull/4369) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Bugfix: Duckdb SELECT * [#4365](https://github.com/sqlfluff/sqlfluff/pull/4365) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: TABLESAMPLE query [#4357](https://github.com/sqlfluff/sqlfluff/pull/4357) [@greg-finley](https://github.com/greg-finley)
* reindent refactor [#4338](https://github.com/sqlfluff/sqlfluff/pull/4338) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: INSERT INTO [#4363](https://github.com/sqlfluff/sqlfluff/pull/4363) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Docs: correct toml syntax of pyproject.toml file config example [#4361](https://github.com/sqlfluff/sqlfluff/pull/4361) [@imrehg](https://github.com/imrehg)
* Allowed Naked Identifiers [#4359](https://github.com/sqlfluff/sqlfluff/pull/4359) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: TABLESAMPLE [#4353](https://github.com/sqlfluff/sqlfluff/pull/4353) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Tsql: Function Parameters [#4352](https://github.com/sqlfluff/sqlfluff/pull/4352) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Postgres: Storage parameters [#4350](https://github.com/sqlfluff/sqlfluff/pull/4350) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: Bare Function Set [#4351](https://github.com/sqlfluff/sqlfluff/pull/4351) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Postgres: View options [#4340](https://github.com/sqlfluff/sqlfluff/pull/4340) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* BigQuery: SELECT DISTINCT AS STRUCT [#4341](https://github.com/sqlfluff/sqlfluff/pull/4341) [@joar](https://github.com/joar)
* Snowflake: Fix Alter Warehouse [#4344](https://github.com/sqlfluff/sqlfluff/pull/4344) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Parser: Optimise lookahead_match [#4327](https://github.com/sqlfluff/sqlfluff/pull/4327) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add support for dbt test macros [#4319](https://github.com/sqlfluff/sqlfluff/pull/4319) [@pdebelak](https://github.com/pdebelak)
* Bracket complex expressions before applying :: operator in Rule L067 [#4326](https://github.com/sqlfluff/sqlfluff/pull/4326) [@pdebelak](https://github.com/pdebelak)
* Prep version 2.0.0a4 [#4322](https://github.com/sqlfluff/sqlfluff/pull/4322) [@github-actions](https://github.com/github-actions)
* BigQuery: Alter table alter column [#4316](https://github.com/sqlfluff/sqlfluff/pull/4316) [@greg-finley](https://github.com/greg-finley)
* Handle renamed dbt exceptions [#4317](https://github.com/sqlfluff/sqlfluff/pull/4317) [@greg-finley](https://github.com/greg-finley)
* Parser: Fix early exit for simple matchers [#4305](https://github.com/sqlfluff/sqlfluff/pull/4305) [@WittierDinosaur](https://github.com/WittierDinosaur)
* MySQL: Add CREATE DATABASE and ALTER DATABASE [#4307](https://github.com/sqlfluff/sqlfluff/pull/4307) [@yoichi](https://github.com/yoichi)
* BigQuery: Add ALTER VIEW [#4306](https://github.com/sqlfluff/sqlfluff/pull/4306) [@yoichi](https://github.com/yoichi)
* toml: only install `toml` dependency if < Python 3.11 (otherwise use builtin `tomllib`) [#4303](https://github.com/sqlfluff/sqlfluff/pull/4303) [@kevinmarsh](https://github.com/kevinmarsh)
* Fix #4024 example plugin unit tests import [#4302](https://github.com/sqlfluff/sqlfluff/pull/4302) [@matthieucan](https://github.com/matthieucan)
* Prep version 2.0.0a3 [#4290](https://github.com/sqlfluff/sqlfluff/pull/4290) [@github-actions](https://github.com/github-actions)
* Move ISSUE from Snwoflake reserved keywords to unreserved ones [#4279](https://github.com/sqlfluff/sqlfluff/pull/4279) [@KaoutherElhamdi](https://github.com/KaoutherElhamdi)
* Due to performance and other issues, revert the osmosis implementation of the templater for now [#4273](https://github.com/sqlfluff/sqlfluff/pull/4273) [@barrywhart](https://github.com/barrywhart)
* Simplify lexing [#4289](https://github.com/sqlfluff/sqlfluff/pull/4289) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4255 (Fix exception on mixed indent description) [#4288](https://github.com/sqlfluff/sqlfluff/pull/4288) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4253 (incorrect trigger of L006 around placeholders) [#4287](https://github.com/sqlfluff/sqlfluff/pull/4287) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4249 (TSQL block comment indents) [#4286](https://github.com/sqlfluff/sqlfluff/pull/4286) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4252 (Resolve multiple sensible indents) [#4285](https://github.com/sqlfluff/sqlfluff/pull/4285) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Parser Performance: Cache segment string repr to reduce function calls [#4278](https://github.com/sqlfluff/sqlfluff/pull/4278) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: GRANT SUPPORT CASES [#4283](https://github.com/sqlfluff/sqlfluff/pull/4283) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Dialect: duckdb [#4284](https://github.com/sqlfluff/sqlfluff/pull/4284) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add variable pattern to CopyIntoTable [#4275](https://github.com/sqlfluff/sqlfluff/pull/4275) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Non-reserved keyword bugfix [#4277](https://github.com/sqlfluff/sqlfluff/pull/4277) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Hive: Add Table constraints DISABLE VALIDATE [#4281](https://github.com/sqlfluff/sqlfluff/pull/4281) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add Python and Java UDF support [#4280](https://github.com/sqlfluff/sqlfluff/pull/4280) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SparkSQL: Support DIV binary operator [#4282](https://github.com/sqlfluff/sqlfluff/pull/4282) [@WittierDinosaur](https://github.com/WittierDinosaur)
* BigQuery: Add ALTER TABLE [#4272](https://github.com/sqlfluff/sqlfluff/pull/4272) [@yoichi](https://github.com/yoichi)
* Snowflake: Update bare functions [#4276](https://github.com/sqlfluff/sqlfluff/pull/4276) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Improve Dockerfile to reduce image size [#4262](https://github.com/sqlfluff/sqlfluff/pull/4262) [@tdurieux](https://github.com/tdurieux)
* Prep version 2.0.0a2 [#4247](https://github.com/sqlfluff/sqlfluff/pull/4247) [@github-actions](https://github.com/github-actions)
* Push indents to after comments [#4239](https://github.com/sqlfluff/sqlfluff/pull/4239) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Templated fix improvements and indentation [#4245](https://github.com/sqlfluff/sqlfluff/pull/4245) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix block comment indent fixes #4224 [#4240](https://github.com/sqlfluff/sqlfluff/pull/4240) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix for #4222 [#4236](https://github.com/sqlfluff/sqlfluff/pull/4236) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Allow multiple unpivot [#4242](https://github.com/sqlfluff/sqlfluff/pull/4242) [@greg-finley](https://github.com/greg-finley)
* postgres: add row-level locks to SELECT statements [#4209](https://github.com/sqlfluff/sqlfluff/pull/4209) [@Yiwen-Gao](https://github.com/Yiwen-Gao)
* Add more parsing logic for db2 [#4206](https://github.com/sqlfluff/sqlfluff/pull/4206) [@NelsonTorres](https://github.com/NelsonTorres)
* Include the filename in critical exceptions [#4225](https://github.com/sqlfluff/sqlfluff/pull/4225) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update Readme Badges [#4219](https://github.com/sqlfluff/sqlfluff/pull/4219) [@alanmcruickshank](https://github.com/alanmcruickshank)
* diff-quality: Handle the case where there are no files to check [#4220](https://github.com/sqlfluff/sqlfluff/pull/4220) [@barrywhart](https://github.com/barrywhart)
* Prep version 2.0.0a1 [#4203](https://github.com/sqlfluff/sqlfluff/pull/4203) [@github-actions](https://github.com/github-actions)
* Fixed False Positive for L037 [#4198](https://github.com/sqlfluff/sqlfluff/pull/4198) [@WillAyd](https://github.com/WillAyd)
* Fix #4215 [#4217](https://github.com/sqlfluff/sqlfluff/pull/4217) [@alanmcruickshank](https://github.com/alanmcruickshank)
* don't consider templated whitespace [#4213](https://github.com/sqlfluff/sqlfluff/pull/4213) [@alanmcruickshank](https://github.com/alanmcruickshank)
* show fatal errors regardless [#4214](https://github.com/sqlfluff/sqlfluff/pull/4214) [@alanmcruickshank](https://github.com/alanmcruickshank)
* don't pickle the templater [#4208](https://github.com/sqlfluff/sqlfluff/pull/4208) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: Support column character set and collation [#4204](https://github.com/sqlfluff/sqlfluff/pull/4204) [@yoichi](https://github.com/yoichi)
* Fix some issues with Docker Compose environment [#4201](https://github.com/sqlfluff/sqlfluff/pull/4201) [@barrywhart](https://github.com/barrywhart)
* Implicit Indents [#4054](https://github.com/sqlfluff/sqlfluff/pull/4054) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Tweak Coveralls settings [#4199](https://github.com/sqlfluff/sqlfluff/pull/4199) [@barrywhart](https://github.com/barrywhart)
* In addition to Codecov, also upload to Coveralls [#4197](https://github.com/sqlfluff/sqlfluff/pull/4197) [@barrywhart](https://github.com/barrywhart)
* Fix: create table default cast returns unparsable section [#4192](https://github.com/sqlfluff/sqlfluff/pull/4192) [@NelsonTorres](https://github.com/NelsonTorres)
* Fix JSON parsing issue with diff-quality plugin [#4190](https://github.com/sqlfluff/sqlfluff/pull/4190) [@barrywhart](https://github.com/barrywhart)
* Codecov migration [#4195](https://github.com/sqlfluff/sqlfluff/pull/4195) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Stop adding trailing os.sep if ignore file is on the root of the file… [#4182](https://github.com/sqlfluff/sqlfluff/pull/4182) [@baa-ableton](https://github.com/baa-ableton)
* Port dbt-osmosis templater changes to SQLFluff [#3976](https://github.com/sqlfluff/sqlfluff/pull/3976) [@barrywhart](https://github.com/barrywhart)
* Reflow 4: Long Lines [#4067](https://github.com/sqlfluff/sqlfluff/pull/4067) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix comment bug on reindent [#4179](https://github.com/sqlfluff/sqlfluff/pull/4179) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Reflow 3: Reindent [#3942](https://github.com/sqlfluff/sqlfluff/pull/3942) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@konnectr](https://github.com/konnectr) made their first contribution in [#4488](https://github.com/sqlfluff/sqlfluff/pull/4488)
* [@ValentinCrr](https://github.com/ValentinCrr) made their first contribution in [#4490](https://github.com/sqlfluff/sqlfluff/pull/4490)
* [@FabianScheidt](https://github.com/FabianScheidt) made their first contribution in [#4426](https://github.com/sqlfluff/sqlfluff/pull/4426)
* [@dflem97](https://github.com/dflem97) made their first contribution in [#4440](https://github.com/sqlfluff/sqlfluff/pull/4440)
* [@timcosta](https://github.com/timcosta) made their first contribution in [#4391](https://github.com/sqlfluff/sqlfluff/pull/4391)
* [@AidanHarveyNelson](https://github.com/AidanHarveyNelson) made their first contribution in [#4344](https://github.com/sqlfluff/sqlfluff/pull/4344)
* [@joar](https://github.com/joar) made their first contribution in [#4341](https://github.com/sqlfluff/sqlfluff/pull/4341)
* [@jmpfar](https://github.com/jmpfar) made their first contribution in [#4356](https://github.com/sqlfluff/sqlfluff/pull/4356)
* [@jared-rimmer](https://github.com/jared-rimmer) made their first contribution in [#4403](https://github.com/sqlfluff/sqlfluff/pull/4403)
* [@vesatoivonen](https://github.com/vesatoivonen) made their first contribution in [#4335](https://github.com/sqlfluff/sqlfluff/pull/4335)
* [@briankravec](https://github.com/briankravec) made their first contribution in [#4421](https://github.com/sqlfluff/sqlfluff/pull/4421)
* [@saintamh](https://github.com/saintamh) made their first contribution in [#4417](https://github.com/sqlfluff/sqlfluff/pull/4417)
* [@tdurieux](https://github.com/tdurieux) made their first contribution in [#4262](https://github.com/sqlfluff/sqlfluff/pull/4262)
* [@baa-ableton](https://github.com/baa-ableton) made their first contribution in [#4182](https://github.com/sqlfluff/sqlfluff/pull/4182)
* [@WillAyd](https://github.com/WillAyd) made their first contribution in [#4198](https://github.com/sqlfluff/sqlfluff/pull/4198)

## [2.0.0a6] - 2023-03-06

> NOTE: This is effectively a release candidate for testing purposes.
> There are several new features here, and breaking changes to
> configuration. We welcome testing feedback from the community, and
> the intent is that following this release there will be no more
> major breaking changes in the before the 2.0.0 release.

## Highlights

This is the sixth alpha release for 2.0.0, and effectively the first release
candidate for 2.0.0. All the intended breaking changes for the upcoming
release have now been made and only bugfixes and non breaking feature
changes should happen between this release and the full release.

It contains:
* A reorganisation of rules. All rules have been recoded, and can now be
  referred to by their name, code, alias or group. The legacy code for the
  rule is included as an alias for each rule to support some backward
  compatibility.
* Configuration files (and inline configuration flags), should now use the
  **name** of the rule rather than the **code**. Any configuration files
  which reference using legacy rules (or reference unknown rules) should
  now display warnings.
* Introduces the the `sqlfluff format` CLI command (a la `sqlfmt` or `black`)
  to auto-format sql files using a known set of _fairly safe_ rules.
* Databricks as a distinct new dialect (rather than as previously an alias
  for `sparksql`).

There are also numerous dialect improvements to ANSI, Athena, TSQL, Teradata,
SQLite & MySQL.

## What’s Changed

* Fix #4367 [#4479](https://github.com/sqlfluff/sqlfluff/pull/4479) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Teradata: Improve COLLECT STATS parsing [#4478](https://github.com/sqlfluff/sqlfluff/pull/4478) [@dflem97](https://github.com/dflem97)
* Add a sqlfluff format CLI command [#4473](https://github.com/sqlfluff/sqlfluff/pull/4473) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode and disable L031 -> AL07 [#4471](https://github.com/sqlfluff/sqlfluff/pull/4471) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Named Config (part 2) [#4470](https://github.com/sqlfluff/sqlfluff/pull/4470) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Rule config lookup improvements & config warnings [#4465](https://github.com/sqlfluff/sqlfluff/pull/4465) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode L050 [#4468](https://github.com/sqlfluff/sqlfluff/pull/4468) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Implicit indent fixes #4467 [#4469](https://github.com/sqlfluff/sqlfluff/pull/4469) [@alanmcruickshank](https://github.com/alanmcruickshank)
* ANSI: Add IfExistsGrammar to DropTrigger [#4466](https://github.com/sqlfluff/sqlfluff/pull/4466) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Rules Reorg Mopup [#4462](https://github.com/sqlfluff/sqlfluff/pull/4462) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Layout Rules Recode (part 2) [#4456](https://github.com/sqlfluff/sqlfluff/pull/4456) [@alanmcruickshank](https://github.com/alanmcruickshank)
* fix(athena): resolve errors parsing around maps, structs, and arrays [#4391](https://github.com/sqlfluff/sqlfluff/pull/4391) [@timcosta](https://github.com/timcosta)
* Layout Rules Recode (part 1) [#4432](https://github.com/sqlfluff/sqlfluff/pull/4432) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: EXEC string literal [#4458](https://github.com/sqlfluff/sqlfluff/pull/4458) [@jpers36](https://github.com/jpers36)
* Teradata: Added SET QUERY_BAND statement  [#4459](https://github.com/sqlfluff/sqlfluff/pull/4459) [@dflem97](https://github.com/dflem97)
* Teradata: Added TOP select clause modifier [#4461](https://github.com/sqlfluff/sqlfluff/pull/4461) [@dflem97](https://github.com/dflem97)
* Teradata: Addition of comparison operator extensions [#4451](https://github.com/sqlfluff/sqlfluff/pull/4451) [@dflem97](https://github.com/dflem97)
* Add extensions and plugin section to the README.md [#4454](https://github.com/sqlfluff/sqlfluff/pull/4454) [@jared-rimmer](https://github.com/jared-rimmer)
* Convention rules bundle [#4448](https://github.com/sqlfluff/sqlfluff/pull/4448) [@alanmcruickshank](https://github.com/alanmcruickshank)
* References rule bundle [#4446](https://github.com/sqlfluff/sqlfluff/pull/4446) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Structure and Ambiguous rule bundles [#4444](https://github.com/sqlfluff/sqlfluff/pull/4444) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: Bare functions [#4439](https://github.com/sqlfluff/sqlfluff/pull/4439) [@jpers36](https://github.com/jpers36)
* Pull dbt CI tests forward to 1.1 and 1.4 [#4442](https://github.com/sqlfluff/sqlfluff/pull/4442) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Teradata: Added "AND STATS" options when creating table [#4440](https://github.com/sqlfluff/sqlfluff/pull/4440) [@dflem97](https://github.com/dflem97)
* Add Databricks as a distinct dialect [#4438](https://github.com/sqlfluff/sqlfluff/pull/4438) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remove importlib deprecated methods [#4437](https://github.com/sqlfluff/sqlfluff/pull/4437) [@alanmcruickshank](https://github.com/alanmcruickshank)
* SQLite: Support PRAGMA statements [#4431](https://github.com/sqlfluff/sqlfluff/pull/4431) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Proposed graceful handling of noqa by L016 (#4248) [#4424](https://github.com/sqlfluff/sqlfluff/pull/4424) [@alanmcruickshank](https://github.com/alanmcruickshank)
* DuckDb: Allow quoted literals as identifiers [#4410](https://github.com/sqlfluff/sqlfluff/pull/4410) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SQLite Refactor to reduce statement and keyword scope [#4409](https://github.com/sqlfluff/sqlfluff/pull/4409) [@WittierDinosaur](https://github.com/WittierDinosaur)
* L046 and L056 recode [#4430](https://github.com/sqlfluff/sqlfluff/pull/4430) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Recode Aliasing Rules [#4427](https://github.com/sqlfluff/sqlfluff/pull/4427) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adjust MySQL dialect to support combination of not-null, default and … [#4426](https://github.com/sqlfluff/sqlfluff/pull/4426) [@FabianScheidt](https://github.com/FabianScheidt)
* Revert some changes to tox [#4428](https://github.com/sqlfluff/sqlfluff/pull/4428) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Migrate capitalisation rules to plugin and recode [#4413](https://github.com/sqlfluff/sqlfluff/pull/4413) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@FabianScheidt](https://github.com/FabianScheidt) made their first contribution in [#4426](https://github.com/sqlfluff/sqlfluff/pull/4426)
* [@dflem97](https://github.com/dflem97) made their first contribution in [#4440](https://github.com/sqlfluff/sqlfluff/pull/4440)
* [@timcosta](https://github.com/timcosta) made their first contribution in [#4391](https://github.com/sqlfluff/sqlfluff/pull/4391)

## [2.0.0a5] - 2023-02-24

> NOTE: This is an alpha release for testing purposes. There are several new features
> here, and breaking changes to configuration. We welcome testing feedback from the
> community, but know that this release may feel less polished than usual.

## Highlights

This is the fifth alpha release for 2.0.0. It contains:
* Significant rework to rule naming and categorisation.
* Several performance improvements.
* Many dialect improvements to several dialects.
* Bugfixes to many of the issues raised in 2.0.0a4.

There will likely be more changes to rule classification before a full release of 2.0.0,
so anticipate that configuration files may change slightly again in future alpha releases.

## What’s Changed

* Handle long lines without trailing newlines gracefully (#4386) [#4423](https://github.com/sqlfluff/sqlfluff/pull/4423) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4184 (index error in L007) [#4422](https://github.com/sqlfluff/sqlfluff/pull/4422) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle untaken positive indents with taken negative pair. [#4420](https://github.com/sqlfluff/sqlfluff/pull/4420) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: AS MATERIALIZED support [#4417](https://github.com/sqlfluff/sqlfluff/pull/4417) [@saintamh](https://github.com/saintamh)
* Align warnings config with example shown [#4421](https://github.com/sqlfluff/sqlfluff/pull/4421) [@briankravec](https://github.com/briankravec)
* BigQuery: parse "AS description" part of assert expressions [#4418](https://github.com/sqlfluff/sqlfluff/pull/4418) [@yoichi](https://github.com/yoichi)
* Deprecate doc decorators (replace with metaclass) [#4415](https://github.com/sqlfluff/sqlfluff/pull/4415) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Enable noqa using aliases and groups [#4414](https://github.com/sqlfluff/sqlfluff/pull/4414) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add rule names to CLI outputs [#4400](https://github.com/sqlfluff/sqlfluff/pull/4400) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Remove execution keyword inherited from ANSI [#4411](https://github.com/sqlfluff/sqlfluff/pull/4411) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Rule names, aliases and more complicated selection. [#4399](https://github.com/sqlfluff/sqlfluff/pull/4399) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Support Recursive View [#4412](https://github.com/sqlfluff/sqlfluff/pull/4412) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL: Implement BULK INSERT statement [#4381](https://github.com/sqlfluff/sqlfluff/pull/4381) [@borchero](https://github.com/borchero)
* L062: Add match_source (#4172) [#4335](https://github.com/sqlfluff/sqlfluff/pull/4335) [@vesatoivonen](https://github.com/vesatoivonen)
* TSQL: Add SET to ALTER TABLE [#4407](https://github.com/sqlfluff/sqlfluff/pull/4407) [@jared-rimmer](https://github.com/jared-rimmer)
* Snowflake: ALTER STORAGE INTEGRATION segment [#4406](https://github.com/sqlfluff/sqlfluff/pull/4406) [@jared-rimmer](https://github.com/jared-rimmer)
* Fix incorrect link to pre-commit docs [#4405](https://github.com/sqlfluff/sqlfluff/pull/4405) [@pdebelak](https://github.com/pdebelak)
* Add Snowflake dialect ALTER ROLE segment [#4403](https://github.com/sqlfluff/sqlfluff/pull/4403) [@jared-rimmer](https://github.com/jared-rimmer)
* Improving Postgres create index statement [#4356](https://github.com/sqlfluff/sqlfluff/pull/4356) [@jmpfar](https://github.com/jmpfar)
* Resolve #4291: Comments forcing unexpected indents. [#4384](https://github.com/sqlfluff/sqlfluff/pull/4384) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4294: Comments affecting indentation [#4337](https://github.com/sqlfluff/sqlfluff/pull/4337) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Resolve #4292: Window function long line fixes [#4383](https://github.com/sqlfluff/sqlfluff/pull/4383) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: ALTER INDEX [#4364](https://github.com/sqlfluff/sqlfluff/pull/4364) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Added Varying Keyword to allowed data type segments [#4375](https://github.com/sqlfluff/sqlfluff/pull/4375) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Add ruff linter [#4372](https://github.com/sqlfluff/sqlfluff/pull/4372) [@greg-finley](https://github.com/greg-finley)
* Fix postgres column constraint default syntax [#4379](https://github.com/sqlfluff/sqlfluff/pull/4379) [@pdebelak](https://github.com/pdebelak)
* Allow function names to have a leading underscore [#4377](https://github.com/sqlfluff/sqlfluff/pull/4377) [@gavin-tsang](https://github.com/gavin-tsang)
* TSQL: Merge Hints [#4354](https://github.com/sqlfluff/sqlfluff/pull/4354) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: Temporal Table [#4358](https://github.com/sqlfluff/sqlfluff/pull/4358) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: ALTER TABLE [#4369](https://github.com/sqlfluff/sqlfluff/pull/4369) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Bugfix: Duckdb SELECT * [#4365](https://github.com/sqlfluff/sqlfluff/pull/4365) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: TABLESAMPLE query [#4357](https://github.com/sqlfluff/sqlfluff/pull/4357) [@greg-finley](https://github.com/greg-finley)
* reindent refactor [#4338](https://github.com/sqlfluff/sqlfluff/pull/4338) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: INSERT INTO [#4363](https://github.com/sqlfluff/sqlfluff/pull/4363) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Docs: correct toml syntax of pyproject.toml file config example [#4361](https://github.com/sqlfluff/sqlfluff/pull/4361) [@imrehg](https://github.com/imrehg)
* Allowed Naked Identifiers [#4359](https://github.com/sqlfluff/sqlfluff/pull/4359) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: TABLESAMPLE [#4353](https://github.com/sqlfluff/sqlfluff/pull/4353) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Tsql: Function Parameters [#4352](https://github.com/sqlfluff/sqlfluff/pull/4352) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Postgres: Storage parameters [#4350](https://github.com/sqlfluff/sqlfluff/pull/4350) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* TSQL: Bare Function Set [#4351](https://github.com/sqlfluff/sqlfluff/pull/4351) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Postgres: View options [#4340](https://github.com/sqlfluff/sqlfluff/pull/4340) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* BigQuery: SELECT DISTINCT AS STRUCT [#4341](https://github.com/sqlfluff/sqlfluff/pull/4341) [@joar](https://github.com/joar)
* Snowflake: Fix Alter Warehouse [#4344](https://github.com/sqlfluff/sqlfluff/pull/4344) [@AidanHarveyNelson](https://github.com/AidanHarveyNelson)
* Parser: Optimise lookahead_match [#4327](https://github.com/sqlfluff/sqlfluff/pull/4327) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add support for dbt test macros [#4319](https://github.com/sqlfluff/sqlfluff/pull/4319) [@pdebelak](https://github.com/pdebelak)
* Bracket complex expressions before applying :: operator in Rule L067 [#4326](https://github.com/sqlfluff/sqlfluff/pull/4326) [@pdebelak](https://github.com/pdebelak)

## New Contributors
* [@AidanHarveyNelson](https://github.com/AidanHarveyNelson) made their first contribution in [#4344](https://github.com/sqlfluff/sqlfluff/pull/4344)
* [@joar](https://github.com/joar) made their first contribution in [#4341](https://github.com/sqlfluff/sqlfluff/pull/4341)
* [@jmpfar](https://github.com/jmpfar) made their first contribution in [#4356](https://github.com/sqlfluff/sqlfluff/pull/4356)
* [@jared-rimmer](https://github.com/jared-rimmer) made their first contribution in [#4403](https://github.com/sqlfluff/sqlfluff/pull/4403)
* [@vesatoivonen](https://github.com/vesatoivonen) made their first contribution in [#4335](https://github.com/sqlfluff/sqlfluff/pull/4335)
* [@briankravec](https://github.com/briankravec) made their first contribution in [#4421](https://github.com/sqlfluff/sqlfluff/pull/4421)
* [@saintamh](https://github.com/saintamh) made their first contribution in [#4417](https://github.com/sqlfluff/sqlfluff/pull/4417)

## [2.0.0a4] - 2023-01-26

## Highlights

This is the fourth alpha release for 2.0.0. It contains a fix for the renamed dbt exceptions in dbt version 1.4.0, a fix for a major performance issue with the 2.0 dbt templater, and improvements to parse performance of large SQL files.

## What’s Changed

* BigQuery: Alter table alter column [#4316](https://github.com/sqlfluff/sqlfluff/pull/4316) [@greg-finley](https://github.com/greg-finley)
* Handle renamed dbt exceptions [#4317](https://github.com/sqlfluff/sqlfluff/pull/4317) [@greg-finley](https://github.com/greg-finley)
* Parser: Fix early exit for simple matchers [#4305](https://github.com/sqlfluff/sqlfluff/pull/4305) [@WittierDinosaur](https://github.com/WittierDinosaur)
* MySQL: Add CREATE DATABASE and ALTER DATABASE [#4307](https://github.com/sqlfluff/sqlfluff/pull/4307) [@yoichi](https://github.com/yoichi)
* BigQuery: Add ALTER VIEW [#4306](https://github.com/sqlfluff/sqlfluff/pull/4306) [@yoichi](https://github.com/yoichi)
* toml: only install `toml` dependency if < Python 3.11 (otherwise use builtin `tomllib`) [#4303](https://github.com/sqlfluff/sqlfluff/pull/4303) [@kevinmarsh](https://github.com/kevinmarsh)
* Fix #4024 example plugin unit tests import [#4302](https://github.com/sqlfluff/sqlfluff/pull/4302) [@matthieucan](https://github.com/matthieucan)

## [2.0.0a3] - 2023-01-16

> NOTE: This is an alpha release for testing purposes. There are several new features
> here, and breaking changes to configuration. We welcome testing feedback from the
> community, but know that this release may feel less polished than usual.

## Highlights

This is the third alpha release for 2.0.0. It contains primarily bugfixes from 2.0.0a2
to allow continued testing. In particular, some of the recent 2.0.0-related changes to the
dbt templater have been reverted, primarily due to performance and other issues. If
those issues can be resolved, the changes will be re-introduced. The long-term goal of
this work is to ease maintenance of the templater by separating dbt integration concerns
from SQLFluff concerns.

There will likely be more changes to rule classification before a full release of 2.0.0,
so anticipate that configuration files may change slightly again in future alpha releases.

## What’s Changed

* Move ISSUE from Snowflake reserved keywords to unreserved ones [#4279](https://github.com/sqlfluff/sqlfluff/pull/4279) [@KaoutherElhamdi](https://github.com/KaoutherElhamdi)
* Due to performance and other issues, revert the osmosis implementation of the templater for now [#4273](https://github.com/sqlfluff/sqlfluff/pull/4273) [@barrywhart](https://github.com/barrywhart)
* Simplify lexing [#4289](https://github.com/sqlfluff/sqlfluff/pull/4289) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4255 (Fix exception on mixed indent description) [#4288](https://github.com/sqlfluff/sqlfluff/pull/4288) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4253 (incorrect trigger of L006 around placeholders) [#4287](https://github.com/sqlfluff/sqlfluff/pull/4287) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4249 (TSQL block comment indents) [#4286](https://github.com/sqlfluff/sqlfluff/pull/4286) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix #4252 (Resolve multiple sensible indents) [#4285](https://github.com/sqlfluff/sqlfluff/pull/4285) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Parser Performance: Cache segment string repr to reduce function calls [#4278](https://github.com/sqlfluff/sqlfluff/pull/4278) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: GRANT SUPPORT CASES [#4283](https://github.com/sqlfluff/sqlfluff/pull/4283) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Dialect: duckdb [#4284](https://github.com/sqlfluff/sqlfluff/pull/4284) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add variable pattern to CopyIntoTable [#4275](https://github.com/sqlfluff/sqlfluff/pull/4275) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Non-reserved keyword bugfix [#4277](https://github.com/sqlfluff/sqlfluff/pull/4277) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Hive: Add Table constraints DISABLE VALIDATE [#4281](https://github.com/sqlfluff/sqlfluff/pull/4281) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Snowflake: Add Python and Java UDF support [#4280](https://github.com/sqlfluff/sqlfluff/pull/4280) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SparkSQL: Support DIV binary operator [#4282](https://github.com/sqlfluff/sqlfluff/pull/4282) [@WittierDinosaur](https://github.com/WittierDinosaur)
* BigQuery: Add ALTER TABLE [#4272](https://github.com/sqlfluff/sqlfluff/pull/4272) [@yoichi](https://github.com/yoichi)
* Snowflake: Update bare functions [#4276](https://github.com/sqlfluff/sqlfluff/pull/4276) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Improve Dockerfile to reduce image size [#4262](https://github.com/sqlfluff/sqlfluff/pull/4262) [@tdurieux](https://github.com/tdurieux)

## New Contributors

* [@tdurieux](https://github.com/tdurieux) made their first contribution in [#4262](https://github.com/sqlfluff/sqlfluff/pull/4262)

## [2.0.0a2] - 2023-01-07

## Highlights

This is the second alpha release for 2.0.0. It contains primarily bugfixes from 2.0.0a1
to allow continued testing along with dialect improvements for Snowflake, Postgres and DB2.

## What’s Changed

* Push indents to after comments [#4239](https://github.com/sqlfluff/sqlfluff/pull/4239) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Templated fix improvements and indentation [#4245](https://github.com/sqlfluff/sqlfluff/pull/4245) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix block comment indent fixes #4224 [#4240](https://github.com/sqlfluff/sqlfluff/pull/4240) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix for #4222 [#4236](https://github.com/sqlfluff/sqlfluff/pull/4236) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Allow multiple unpivot [#4242](https://github.com/sqlfluff/sqlfluff/pull/4242) [@greg-finley](https://github.com/greg-finley)
* postgres: add row-level locks to SELECT statements [#4209](https://github.com/sqlfluff/sqlfluff/pull/4209) [@Yiwen-Gao](https://github.com/Yiwen-Gao)
* Add more parsing logic for db2 [#4206](https://github.com/sqlfluff/sqlfluff/pull/4206) [@NelsonTorres](https://github.com/NelsonTorres)
* Include the filename in critical exceptions [#4225](https://github.com/sqlfluff/sqlfluff/pull/4225) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update Readme Badges [#4219](https://github.com/sqlfluff/sqlfluff/pull/4219) [@alanmcruickshank](https://github.com/alanmcruickshank)
* diff-quality: Handle the case where there are no files to check [#4220](https://github.com/sqlfluff/sqlfluff/pull/4220) [@barrywhart](https://github.com/barrywhart)

## [2.0.0a1] - 2022-12-28

## Highlights

This is the first alpha version for 2.0.0. It brings all of the changes to whitespace
handing, including a total rewrite of indentation and long line logic (L003 & L016).
That brings several breaking changes to the configuration of layout, see the
[layout docs](https://docs.sqlfluff.com/en/stable/layout.html) for more details and
familiarise yourself with the new
[default configuration](https://docs.sqlfluff.com/en/stable/configuration.html#default-configuration).

In addition, for the dbt templater, this introduces a large re-write of the codebase,
dropping support for dbt versions before 1.0.0. This leverages functionality from
[dbt-osmosis](https://github.com/z3z1ma/dbt-osmosis) to reduce the amount of
functionality supported directly by SQLFluff, and performance during testing of the new
version has been reported as significantly faster.

## What’s Changed

* Fixed False Positive for L037 [#4198](https://github.com/sqlfluff/sqlfluff/pull/4198) [@WillAyd](https://github.com/WillAyd)
* Indentation bug [#4217](https://github.com/sqlfluff/sqlfluff/pull/4217) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Show fatal errors regardless [#4214](https://github.com/sqlfluff/sqlfluff/pull/4214) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Don't consider templated whitespace [#4213](https://github.com/sqlfluff/sqlfluff/pull/4213) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Don't pickle the templater [#4208](https://github.com/sqlfluff/sqlfluff/pull/4208) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: Support column character set and collation [#4204](https://github.com/sqlfluff/sqlfluff/pull/4204) [@yoichi](https://github.com/yoichi)
* Fix some issues with Docker Compose environment [#4201](https://github.com/sqlfluff/sqlfluff/pull/4201) [@barrywhart](https://github.com/barrywhart)
* Implicit Indents [#4054](https://github.com/sqlfluff/sqlfluff/pull/4054) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Tweak Coveralls settings [#4199](https://github.com/sqlfluff/sqlfluff/pull/4199) [@barrywhart](https://github.com/barrywhart)
* In addition to Codecov, also upload to Coveralls [#4197](https://github.com/sqlfluff/sqlfluff/pull/4197) [@barrywhart](https://github.com/barrywhart)
* Fix: create table default cast returns unparsable section [#4192](https://github.com/sqlfluff/sqlfluff/pull/4192) [@NelsonTorres](https://github.com/NelsonTorres)
* Fix JSON parsing issue with diff-quality plugin [#4190](https://github.com/sqlfluff/sqlfluff/pull/4190) [@barrywhart](https://github.com/barrywhart)
* Codecov migration [#4195](https://github.com/sqlfluff/sqlfluff/pull/4195) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Stop adding trailing os.sep if ignore file is on the root of the file… [#4182](https://github.com/sqlfluff/sqlfluff/pull/4182) [@baa-ableton](https://github.com/baa-ableton)
* Port dbt-osmosis templater changes to SQLFluff [#3976](https://github.com/sqlfluff/sqlfluff/pull/3976) [@barrywhart](https://github.com/barrywhart)
* Reflow 4: Long Lines [#4067](https://github.com/sqlfluff/sqlfluff/pull/4067) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix comment bug on reindent [#4179](https://github.com/sqlfluff/sqlfluff/pull/4179) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Reflow 3: Reindent [#3942](https://github.com/sqlfluff/sqlfluff/pull/3942) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@baa-ableton](https://github.com/baa-ableton) made their first contribution in [#4182](https://github.com/sqlfluff/sqlfluff/pull/4182)
* [@WillAyd](https://github.com/WillAyd) made their first contribution in [#4198](https://github.com/sqlfluff/sqlfluff/pull/4198)

## [1.4.5] - 2022-12-18

## Highlights

This is a bugfix release, primarily for diff-quality. In addition, a new rules for spacing
around parenthesis is also included.

This is also the final 1.x.x release. Following releases will be a series of alpha releases
for 2.x.x. If you affected by any outstanding bugs or regressions from this release, consider
either rolling _backward_ to a previous release without those issues, or failing _forward_
to on an alpha release for 2.x.x (or a full release if that's out). Note that 2.x.x will bring
a selection of breaking changes to config file structure, rule categorisation and dbt support.

## What’s Changed

* Add rule for space around parenthesis [#4131](https://github.com/sqlfluff/sqlfluff/pull/4131) [@NelsonTorres](https://github.com/NelsonTorres)
* diff-quality plugin: Print invalid JSON on parse failure [#4176](https://github.com/sqlfluff/sqlfluff/pull/4176) [@barrywhart](https://github.com/barrywhart)
* Ensure diff-quality runs the correct SQLFluff [#4175](https://github.com/sqlfluff/sqlfluff/pull/4175) [@barrywhart](https://github.com/barrywhart)

## New Contributors

* [@NelsonTorres](https://github.com/NelsonTorres) made their first contribution in [#4131](https://github.com/sqlfluff/sqlfluff/pull/4131)

## [1.4.4] - 2022-12-14

## Highlights

Bug fix for 1.4.3 which was incorrectly flagging L006 for concat operators (`||`) and other two-symbol binary operators.

## What’s Changed

* Recognise || as an operator to avoid rule L006 flagging it [#4168](https://github.com/sqlfluff/sqlfluff/pull/4168) [@tunetheweb](https://github.com/tunetheweb)
* :bug: Check verbosity level of pytest run before running certain tests [#4167](https://github.com/sqlfluff/sqlfluff/pull/4167) [@pwildenhain](https://github.com/pwildenhain)
* [snowflake] Add support for snowflake select * exclude/replace syntax [#4160](https://github.com/sqlfluff/sqlfluff/pull/4160) [@moreaupascal56](https://github.com/moreaupascal56)


## [1.4.3] - 2022-12-13

## Highlights

* Rewrote `diff-quality` plugin to run SQLFluff as a subprocess. More reliable, easier to switch between `diff-quality` and running `sqlfluff lint` directly.
* New rule L067 enforces consistent syntax for type casts.
* New rule L068 enforces a consistent number of columns in set queries (e.g. UNION).
* Initial support for Materialize dialect.

## What's Changed
* Add flyway variables support via placeholder templater [#4026](https://github.com/sqlfluff/sqlfluff/pull/4026) [@srjonemed](https://github.com/srjonemed)
* Fix Spark comparison parsing [#4066](https://github.com/sqlfluff/sqlfluff/pull/4066) [@ms32035](https://github.com/ms32035)
* Add errors and fails to pytest summary [#4076](https://github.com/sqlfluff/sqlfluff/pull/4076) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Storage reference segment [#4057](https://github.com/sqlfluff/sqlfluff/pull/4057) [@YilangHe](https://github.com/YilangHe)
* New rule L069: Consistent syntax for sql type casting [#3747](https://github.com/sqlfluff/sqlfluff/pull/3747) [@bolajiwahab](https://github.com/bolajiwahab)
* Postgres: Views and named notations [#4073](https://github.com/sqlfluff/sqlfluff/pull/4073) [@davetapley](https://github.com/davetapley)
* Switch reflow buffer from LintFix to LintResult [#4083](https://github.com/sqlfluff/sqlfluff/pull/4083) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Support parallel linting when many individual files specified [#4084](https://github.com/sqlfluff/sqlfluff/pull/4084) [@barrywhart](https://github.com/barrywhart)
* Rule: check number of columns in set operations match [#4028](https://github.com/sqlfluff/sqlfluff/pull/4028) [@erevear](https://github.com/erevear)
* Fix syntax in indentation sample code docs [#4087](https://github.com/sqlfluff/sqlfluff/pull/4087) [@PBalsdon](https://github.com/PBalsdon)
* Remove "mystery" binary file added in PR #2923 [#4088](https://github.com/sqlfluff/sqlfluff/pull/4088) [@barrywhart](https://github.com/barrywhart)
* Fix mypy issue with regex [#4097](https://github.com/sqlfluff/sqlfluff/pull/4097) [@barrywhart](https://github.com/barrywhart)
* Enable variable reference names to have leading underscore for snowflake dialect [#4098](https://github.com/sqlfluff/sqlfluff/pull/4098) [@gavin-tsang](https://github.com/gavin-tsang)
* Fix flake8 issue with segment_predicates.py [#4101](https://github.com/sqlfluff/sqlfluff/pull/4101) [@barrywhart](https://github.com/barrywhart)
* Fix bug in example rule plugin [#4103](https://github.com/sqlfluff/sqlfluff/pull/4103) [@barrywhart](https://github.com/barrywhart)
* Fix bug where L034 should ignore INSERT or "CREATE TABLE AS SELECT" with CTE [#4108](https://github.com/sqlfluff/sqlfluff/pull/4108) [@barrywhart](https://github.com/barrywhart)
* Postgres: Alter type rename value [#4100](https://github.com/sqlfluff/sqlfluff/pull/4100) [@greg-finley](https://github.com/greg-finley)
* Bug fix: dbt templater ignores .sqlfluff file encoding on Windows [#4109](https://github.com/sqlfluff/sqlfluff/pull/4109) [@barrywhart](https://github.com/barrywhart)
* Add initial Materialize dialect [#4112](https://github.com/sqlfluff/sqlfluff/pull/4112) [@bobbyiliev](https://github.com/bobbyiliev)
* L015: Handle COUNT(DISTINCT(col)) [#4110](https://github.com/sqlfluff/sqlfluff/pull/4110) [@barrywhart](https://github.com/barrywhart)
* [Snowflake] format type options extensions for copy_into_location [#4129](https://github.com/sqlfluff/sqlfluff/pull/4129) [@YilangHe](https://github.com/YilangHe)
* Fix tox arguments [#4144](https://github.com/sqlfluff/sqlfluff/pull/4144) [@greg-finley](https://github.com/greg-finley)
* [DB2] Fix parsing of string identifiers [#4134](https://github.com/sqlfluff/sqlfluff/pull/4134) [@borchero](https://github.com/borchero)
* BigQuery: Allow double quoted literal in export_option_list [#4126](https://github.com/sqlfluff/sqlfluff/pull/4126) [@yoichi](https://github.com/yoichi)
* Only upload 3 sets of test results to codecov (possible workaround for hanging builds) [#4147](https://github.com/sqlfluff/sqlfluff/pull/4147) [@barrywhart](https://github.com/barrywhart)
* SparkSQL: ILIKE [#4138](https://github.com/sqlfluff/sqlfluff/pull/4138) [@greg-finley](https://github.com/greg-finley)
* SparkSQL: Mark `AS` as optional keyword for CTE & CTS [#4127](https://github.com/sqlfluff/sqlfluff/pull/4127) [@ulixius9](https://github.com/ulixius9)
* Fix passenv to work with tox 4 [#4154](https://github.com/sqlfluff/sqlfluff/pull/4154) [@tunetheweb](https://github.com/tunetheweb)
* Allow deprecated --disable_progress_bar flag for fix command [#4151](https://github.com/sqlfluff/sqlfluff/pull/4151) [@pdebelak](https://github.com/pdebelak)
* Implement diff_quality_plugin using command-line rather than Python [#4148](https://github.com/sqlfluff/sqlfluff/pull/4148) [@barrywhart](https://github.com/barrywhart)
* L037: insert ASC just after column_reference [#4149](https://github.com/sqlfluff/sqlfluff/pull/4149) [@yoichi](https://github.com/yoichi)

## New Contributors
* [@srjonemed](https://github.com/srjonemed) made their first contribution in [#4026](https://github.com/sqlfluff/sqlfluff/pull/4026)
* [@ms32035](https://github.com/ms32035) made their first contribution in [#4066](https://github.com/sqlfluff/sqlfluff/pull/4066)
* [@davetapley](https://github.com/davetapley) made their first contribution in [#4073](https://github.com/sqlfluff/sqlfluff/pull/4073)
* [@PBalsdon](https://github.com/PBalsdon) made their first contribution in [#4087](https://github.com/sqlfluff/sqlfluff/pull/4087)
* [@gavin-tsang](https://github.com/gavin-tsang) made their first contribution in [#4098](https://github.com/sqlfluff/sqlfluff/pull/4098)
* [@bobbyiliev](https://github.com/bobbyiliev) made their first contribution in [#4112](https://github.com/sqlfluff/sqlfluff/pull/4112)
* [@ulixius9](https://github.com/ulixius9) made their first contribution in [#4127](https://github.com/sqlfluff/sqlfluff/pull/4127)

## [1.4.2] - 2022-11-13

## Highlights

This release is less about internals and much more about some quality of life
improvements and dialect changes. The most notable are:
- The introduction of a `sqlfluff render` command to preview the results of
  templated sql.
- Linting errors within templated loops should now only appear once in the
  linting output.
- Indentation around jinja `{% set %}` statements should now be more consistent.
- Linting errors around unparsable code are now more appropriately handled (with
  more to come soon on that front).
- Error messages when specified files aren't found are now more specific.

We've also got dialect improvements for Redshift, SOQL & SparkSQL.

## What’s Changed

* Fix type error in `get_rules` hook of plugin example [#4060](https://github.com/sqlfluff/sqlfluff/pull/4060) [@Samyak2](https://github.com/Samyak2)
* L003: Add missing "pragma: no cover" [#4058](https://github.com/sqlfluff/sqlfluff/pull/4058) [@barrywhart](https://github.com/barrywhart)
* Fix bug in sparksql SELECT statement termination at UNION #4050 [#4052](https://github.com/sqlfluff/sqlfluff/pull/4052) [@anna-azizian](https://github.com/anna-azizian)
* Deduplicate violations in the source space [#4041](https://github.com/sqlfluff/sqlfluff/pull/4041) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Use "docker compose", not "docker-compose" [#4055](https://github.com/sqlfluff/sqlfluff/pull/4055) [@barrywhart](https://github.com/barrywhart)
* Allow warnings for specific rules [#4053](https://github.com/sqlfluff/sqlfluff/pull/4053) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Better file not found error #1023 [#4051](https://github.com/sqlfluff/sqlfluff/pull/4051) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Filter out issues in unparsable sections [#4032](https://github.com/sqlfluff/sqlfluff/pull/4032) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: ADD and DROP without COLUMN [#4049](https://github.com/sqlfluff/sqlfluff/pull/4049) [@greg-finley](https://github.com/greg-finley)
* Make render command [#4043](https://github.com/sqlfluff/sqlfluff/pull/4043) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bump after_n_builds to 10 [#4046](https://github.com/sqlfluff/sqlfluff/pull/4046) [@greg-finley](https://github.com/greg-finley)
* Redshift: allows for parenthesis around FROM content [#3962](https://github.com/sqlfluff/sqlfluff/pull/3962) [@adam-tokarski](https://github.com/adam-tokarski)
* Update CI to use Python 3.11 [#4038](https://github.com/sqlfluff/sqlfluff/pull/4038) [@greg-finley](https://github.com/greg-finley)
* Classify self contained set statements as templated [#4034](https://github.com/sqlfluff/sqlfluff/pull/4034) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Date and Datetime literals in SOQL [#4037](https://github.com/sqlfluff/sqlfluff/pull/4037) [@alanmcruickshank](https://github.com/alanmcruickshank)
* mypy edits for 0.990 [#4035](https://github.com/sqlfluff/sqlfluff/pull/4035) [@alanmcruickshank](https://github.com/alanmcruickshank)
* sparksql: support for create/remove widget clause [#4021](https://github.com/sqlfluff/sqlfluff/pull/4021) [@Coola4kov](https://github.com/Coola4kov)
* Redshift CREATE EXTERNAL FUNCTION statement [#4011](https://github.com/sqlfluff/sqlfluff/pull/4011) [@rpr-ableton](https://github.com/rpr-ableton)
* Update Redshift bare functions [#4012](https://github.com/sqlfluff/sqlfluff/pull/4012) [@rpr-ableton](https://github.com/rpr-ableton)


## New Contributors
* [@Coola4kov](https://github.com/Coola4kov) made their first contribution in [#4021](https://github.com/sqlfluff/sqlfluff/pull/4021)
* [@anna-azizian](https://github.com/anna-azizian) made their first contribution in [#4052](https://github.com/sqlfluff/sqlfluff/pull/4052)

## [1.4.1] - 2022-10-31

## Highlights

This is a fix to the configuration migration from 1.4.0. In that release, the configuration
of leading/trailing operators would be migrated the wrong way around and precedence between
new and old configuration values behaved unexpectedly.

## What’s Changed

* Config precedence [#4007](https://github.com/sqlfluff/sqlfluff/pull/4007) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Redshift CREATE/ATTACH/DETACH/DROP RLS POLICY statements [#4004](https://github.com/sqlfluff/sqlfluff/pull/4004) [@rpr-ableton](https://github.com/rpr-ableton)
* Redshift: Add support for APPROXIMATE functions [#3997](https://github.com/sqlfluff/sqlfluff/pull/3997) [@rpr-ableton](https://github.com/rpr-ableton)
* hotfix to config migration [#4005](https://github.com/sqlfluff/sqlfluff/pull/4005) [@alanmcruickshank](https://github.com/alanmcruickshank)

## [1.4.0] - 2022-10-31

## Highlights

This release brings several internal changes, and acts as a prelude to 2.0.0 which
will be released fairly soon. In particular, the following config values have changed:
- `sqlfluff:rules:L007:operator_new_lines` has been changed to
  `sqlfluff:layout:type:binary_operator:line_position`.
- `sqlfluff:rules:comma_style` and `sqlfluff:rules:L019:comma_style` have both been
  consolidated into `sqlfluff:layout:type:comma:line_position`.

If any of these values have been set in your config, they will be automatically
translated to the new values at runtime, and a warning will be shown. To silence
the warning, update your config file to the new values. For more details on
configuring layout (including some changes yet to come in future versions)
see [the docs](https://docs.sqlfluff.com/en/latest/layout.html#configuring-layout).

These changes are driven by underlying centralisation in the routines which control
layout. While for this release, no breaking changes are expected - you may find
slight differences in how SQLFluff handles edge cases. We believe in the majority
of cases these are _more_ consistent, but if you find any which are problematic
then do post an issue on GitHub as usual.

Other highlights from this release:
- Better dbt supportfor graph nodes and avoiding dependency conflicts.
- Numerous dialect improvements to T-SQL, MySQL, SparkSQL, SQLite, Athena
  Snowflake, Hive, Postgres & Databricks.

There have also been first time contributions from **10 new contributors**! 🎉🎉🎉


## What’s Changed

* Snowflake partition nonreserved keyword [#3972](https://github.com/sqlfluff/sqlfluff/pull/3972) [@YilangHe](https://github.com/YilangHe)
* Hive: Add support for EXCHANGE PARTITION in ALTER TABLE [#3991](https://github.com/sqlfluff/sqlfluff/pull/3991) [@nahuelverdugo](https://github.com/nahuelverdugo)
* Resolve parse error on multiple bracketed statements [#3994](https://github.com/sqlfluff/sqlfluff/pull/3994) [@yoichi](https://github.com/yoichi)
* Enable parsing of CLONE keyword in bigquery dialect [#3984](https://github.com/sqlfluff/sqlfluff/pull/3984) [@realLyans](https://github.com/realLyans)
* BigQuery: allow nesting of SetExpressionSegment [#3990](https://github.com/sqlfluff/sqlfluff/pull/3990) [@yoichi](https://github.com/yoichi)
* feat(clickhouse): Support non-standard CREATE TABLE statement [#3986](https://github.com/sqlfluff/sqlfluff/pull/3986) [@tomasfarias](https://github.com/tomasfarias)
* Fix Windows CI check [#3992](https://github.com/sqlfluff/sqlfluff/pull/3992) [@greg-finley](https://github.com/greg-finley)
* Snowflake tag reference segment [#3985](https://github.com/sqlfluff/sqlfluff/pull/3985) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix Jinja templater issue where undefined callable threw an exception [#3982](https://github.com/sqlfluff/sqlfluff/pull/3982) [@barrywhart](https://github.com/barrywhart)
* Reflow Documentation V1 [#3970](https://github.com/sqlfluff/sqlfluff/pull/3970) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow lambda argument columns to be unqualified [#3971](https://github.com/sqlfluff/sqlfluff/pull/3971) [@olagjo](https://github.com/olagjo)
* document inline configuration [#3981](https://github.com/sqlfluff/sqlfluff/pull/3981) [@alanmcruickshank](https://github.com/alanmcruickshank)
* [BUGFIX] Changing cwd temporarily on manifest load as dbt is not using project_dir to read/write target folder [#3979](https://github.com/sqlfluff/sqlfluff/pull/3979) [@barrywhart](https://github.com/barrywhart)
* Fix type annotation of user_rules in `Linter` [#3977](https://github.com/sqlfluff/sqlfluff/pull/3977) [@Samyak2](https://github.com/Samyak2)
* Unpin `markupsafe` [#3967](https://github.com/sqlfluff/sqlfluff/pull/3967) [@judahrand](https://github.com/judahrand)
* Snowflake frame clause variables [#3969](https://github.com/sqlfluff/sqlfluff/pull/3969) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SparkSQL: added support for : (colon sign) operator (Databricks SQL) [#3956](https://github.com/sqlfluff/sqlfluff/pull/3956) [@karabulute](https://github.com/karabulute)
* Athena: Add support for using underscore aliases [#3965](https://github.com/sqlfluff/sqlfluff/pull/3965) [@hectcastro](https://github.com/hectcastro)
* Snowflake: ALTER TABLE constraint actions [#3959](https://github.com/sqlfluff/sqlfluff/pull/3959) [@erevear](https://github.com/erevear)
* MySQL: Support REPLACE statement [#3964](https://github.com/sqlfluff/sqlfluff/pull/3964) [@yoichi](https://github.com/yoichi)
* TSQL: Add support for UPDATE STATISTICS option FULLSCAN [#3950](https://github.com/sqlfluff/sqlfluff/pull/3950) [@hectcastro](https://github.com/hectcastro)
* ANSI: fixed typos in docstrings and comments [#3953](https://github.com/sqlfluff/sqlfluff/pull/3953) [@karabulute](https://github.com/karabulute)
* Postgres: ALTER PROCEDURE [#3949](https://github.com/sqlfluff/sqlfluff/pull/3949) [@krokofant](https://github.com/krokofant)
* T-SQL: Allow arbitrary expressions in PARTITION BY clause [#3939](https://github.com/sqlfluff/sqlfluff/pull/3939) [@borchero](https://github.com/borchero)
* Enable dumping of performance information to csv. [#3937](https://github.com/sqlfluff/sqlfluff/pull/3937) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Consolidate comma style configs [#3945](https://github.com/sqlfluff/sqlfluff/pull/3945) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adding missing KeywordSegments for different file types in Athena dialect [#3898](https://github.com/sqlfluff/sqlfluff/pull/3898) [@CommonCrisis](https://github.com/CommonCrisis)
* Add templated block uuids [#3936](https://github.com/sqlfluff/sqlfluff/pull/3936) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Load the full dbt manifest [#3926](https://github.com/sqlfluff/sqlfluff/pull/3926) [@davajm](https://github.com/davajm)
* MySQL: Support optional "IF NOT EXISTS" with CREATE TRIGGER [#3943](https://github.com/sqlfluff/sqlfluff/pull/3943) [@yoichi](https://github.com/yoichi)
* T-SQL: Allow to parse SYNONYM statements [#3941](https://github.com/sqlfluff/sqlfluff/pull/3941) [@borchero](https://github.com/borchero)
* Hive: Add support for LATERAL VIEW clause [#3935](https://github.com/sqlfluff/sqlfluff/pull/3935) [@hectcastro](https://github.com/hectcastro)
* Fix crash in L042 on "UNION" or other "set" queries [#3931](https://github.com/sqlfluff/sqlfluff/pull/3931) [@barrywhart](https://github.com/barrywhart)
* Refactor Lexer: Split apart elements_to_segments and refine placement of meta segments. [#3925](https://github.com/sqlfluff/sqlfluff/pull/3925) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add INSERT INTO <> DEFAULT VALUES to ANSI SQL and T-SQL [#3934](https://github.com/sqlfluff/sqlfluff/pull/3934) [@borchero](https://github.com/borchero)
* Break apart reflow classes and extract methods [#3919](https://github.com/sqlfluff/sqlfluff/pull/3919) [@alanmcruickshank](https://github.com/alanmcruickshank)
* T-SQL: Fix indendentation of OUTER APPLY [#3932](https://github.com/sqlfluff/sqlfluff/pull/3932) [@borchero](https://github.com/borchero)
* MySQL: Fix create trigger [#3928](https://github.com/sqlfluff/sqlfluff/pull/3928) [@adam-tokarski](https://github.com/adam-tokarski)
* SparkSQL: Fixed bug with `QUALIFY` usage without `WHERE` clause (applies also for Databricks dialect) [#3930](https://github.com/sqlfluff/sqlfluff/pull/3930) [@karabulute](https://github.com/karabulute)
* T-SQL: Allow specifying join hints [#3921](https://github.com/sqlfluff/sqlfluff/pull/3921) [@borchero](https://github.com/borchero)
* SQLite: Add support for table-level CHECK constraint [#3923](https://github.com/sqlfluff/sqlfluff/pull/3923) [@hectcastro](https://github.com/hectcastro)
* sparksql: added * EXCEPT for SELECT clause [#3922](https://github.com/sqlfluff/sqlfluff/pull/3922) [@adam-tokarski](https://github.com/adam-tokarski)
* Map old configs to new configs [#3915](https://github.com/sqlfluff/sqlfluff/pull/3915) [@alanmcruickshank](https://github.com/alanmcruickshank)
* [issue_3794] allow to use 'usage' as identifier for postgres [#3914](https://github.com/sqlfluff/sqlfluff/pull/3914) [@adam-tokarski](https://github.com/adam-tokarski)
* `DATABRICKS`: Add Support for Delta Live Tables (DLT) Syntax [#3899](https://github.com/sqlfluff/sqlfluff/pull/3899) [@R7L208](https://github.com/R7L208)
* Postgres Revoke fix [#3912](https://github.com/sqlfluff/sqlfluff/pull/3912) [@greg-finley](https://github.com/greg-finley)
* fix: Click output to stderr on errors [#3902](https://github.com/sqlfluff/sqlfluff/pull/3902) [@KingMichaelPark](https://github.com/KingMichaelPark)
* fix issue with empty enum for postgres [#3910](https://github.com/sqlfluff/sqlfluff/pull/3910) [@adam-tokarski](https://github.com/adam-tokarski)
* feat: Optional numerics for postgres arrays [#3903](https://github.com/sqlfluff/sqlfluff/pull/3903) [@KingMichaelPark](https://github.com/KingMichaelPark)
* fix(test): Return ParseExample namedtuple in get_parse_fixtures [#3911](https://github.com/sqlfluff/sqlfluff/pull/3911) [@tomasfarias](https://github.com/tomasfarias)
* Fix typos [#3901](https://github.com/sqlfluff/sqlfluff/pull/3901) [@kianmeng](https://github.com/kianmeng)
* provide custom DeprecatedOption [#3904](https://github.com/sqlfluff/sqlfluff/pull/3904) [@adam-tokarski](https://github.com/adam-tokarski)
* fix(redshift): Allow keywords in qualified references [#3905](https://github.com/sqlfluff/sqlfluff/pull/3905) [@tomasfarias](https://github.com/tomasfarias)
* Reflow centralisation 2: Rebreak (operators & commas) [#3847](https://github.com/sqlfluff/sqlfluff/pull/3847) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Bring L008 into reflow work [#3908](https://github.com/sqlfluff/sqlfluff/pull/3908) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Snowflake: Create network policy ip lists [#3888](https://github.com/sqlfluff/sqlfluff/pull/3888) [@greg-finley](https://github.com/greg-finley)
* MySQL: Implement (key_part, ...) in index definitions [#3887](https://github.com/sqlfluff/sqlfluff/pull/3887) [@yoichi](https://github.com/yoichi)
* Reflow centralisation 1: Scope + Respace [#3824](https://github.com/sqlfluff/sqlfluff/pull/3824) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update github badge and add docker badge [#3884](https://github.com/sqlfluff/sqlfluff/pull/3884) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@kianmeng](https://github.com/kianmeng) made their first contribution in [#3901](https://github.com/sqlfluff/sqlfluff/pull/3901)
* [@KingMichaelPark](https://github.com/KingMichaelPark) made their first contribution in [#3903](https://github.com/sqlfluff/sqlfluff/pull/3903)
* [@hectcastro](https://github.com/hectcastro) made their first contribution in [#3923](https://github.com/sqlfluff/sqlfluff/pull/3923)
* [@karabulute](https://github.com/karabulute) made their first contribution in [#3930](https://github.com/sqlfluff/sqlfluff/pull/3930)
* [@davajm](https://github.com/davajm) made their first contribution in [#3926](https://github.com/sqlfluff/sqlfluff/pull/3926)
* [@CommonCrisis](https://github.com/CommonCrisis) made their first contribution in [#3898](https://github.com/sqlfluff/sqlfluff/pull/3898)
* [@krokofant](https://github.com/krokofant) made their first contribution in [#3949](https://github.com/sqlfluff/sqlfluff/pull/3949)
* [@Samyak2](https://github.com/Samyak2) made their first contribution in [#3977](https://github.com/sqlfluff/sqlfluff/pull/3977)
* [@realLyans](https://github.com/realLyans) made their first contribution in [#3984](https://github.com/sqlfluff/sqlfluff/pull/3984)
* [@nahuelverdugo](https://github.com/nahuelverdugo) made their first contribution in [#3991](https://github.com/sqlfluff/sqlfluff/pull/3991)
* [@YilangHe](https://github.com/YilangHe) made their first contribution in [#3972](https://github.com/sqlfluff/sqlfluff/pull/3972)

## [1.3.2] - 2022-09-27

## Highlights

This is primarily a release for dialect fixes and improvements with additions
and changes to TSQL, Snowflake, MySQL & Redshift. The other changes of note are:
1. Support for warnings when users set old removed config values. This supports
   future change work by allowing a mechanism to warn if they are used.
2. Improvements to the fix routines for L014 and L042 to handle some trickier
   cases.

## What’s Changed

* Add CreateUserSegment for Snowflake dialect [#3880](https://github.com/sqlfluff/sqlfluff/pull/3880) [@Gal40n04ek](https://github.com/Gal40n04ek)
* raw_segments_with_ancestors [#3878](https://github.com/sqlfluff/sqlfluff/pull/3878) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Adjust TSQL Operators [#3877](https://github.com/sqlfluff/sqlfluff/pull/3877) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Refactor path_to [#3875](https://github.com/sqlfluff/sqlfluff/pull/3875) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Support Removed warning on configs [#3874](https://github.com/sqlfluff/sqlfluff/pull/3874) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MySQL: Support column-path operator for JSON type [#3864](https://github.com/sqlfluff/sqlfluff/pull/3864) [@yoichi](https://github.com/yoichi)
* T-SQL: ALTER FUNCTION/PROCEDURE/VIEW parsing [#3867](https://github.com/sqlfluff/sqlfluff/pull/3867) [@differgroup](https://github.com/differgroup)
* MySQL: Support hexadecimal literals and bit value literals [#3869](https://github.com/sqlfluff/sqlfluff/pull/3869) [@yoichi](https://github.com/yoichi)
* MySQL: Treat double quotes the same as single quotes [#3871](https://github.com/sqlfluff/sqlfluff/pull/3871) [@yoichi](https://github.com/yoichi)
* Snowflake: COMMIT WORK [#3862](https://github.com/sqlfluff/sqlfluff/pull/3862) [@rglbr](https://github.com/rglbr)
* Snowflake: AlterShareStatementSegment and CreateDatabaseFromShareStatementSegment [#3858](https://github.com/sqlfluff/sqlfluff/pull/3858) [@moreaupascal56](https://github.com/moreaupascal56)
* MySQL: Add CREATE/ALTER VIEW [#3859](https://github.com/sqlfluff/sqlfluff/pull/3859) [@wfelipew](https://github.com/wfelipew)
* Redshift: CREATE TABLE LIKE enhancements [#3853](https://github.com/sqlfluff/sqlfluff/pull/3853) [@greg-finley](https://github.com/greg-finley)
* L014 leading underscore capitalization inference fix [#3841](https://github.com/sqlfluff/sqlfluff/pull/3841) [@j-svensmark](https://github.com/j-svensmark)
* MySQL: Add extended DROP TRIGGER functionality [#3846](https://github.com/sqlfluff/sqlfluff/pull/3846) [@yoichi](https://github.com/yoichi)
* Allow standalone aliases in L027 [#3848](https://github.com/sqlfluff/sqlfluff/pull/3848) [@olagjo](https://github.com/olagjo)
* L042: Enable autofix for some tricky cases [#3700](https://github.com/sqlfluff/sqlfluff/pull/3700) [@barrywhart](https://github.com/barrywhart)
* Snowflake: CREATE FUNCTION IF NOT EXISTS [#3845](https://github.com/sqlfluff/sqlfluff/pull/3845) [@greg-finley](https://github.com/greg-finley)
* ignore functions with more than one element ... [#3792](https://github.com/sqlfluff/sqlfluff/pull/3792) [@fmms](https://github.com/fmms)
* MySQL: support remaining constraint parts of CREATE/ALTER TABLE [#3827](https://github.com/sqlfluff/sqlfluff/pull/3827) [@yoichi](https://github.com/yoichi)

## New Contributors

* [@olagjo](https://github.com/olagjo) made their first contribution in [#3848](https://github.com/sqlfluff/sqlfluff/pull/3848)
* [@j-svensmark](https://github.com/j-svensmark) made their first contribution in [#3841](https://github.com/sqlfluff/sqlfluff/pull/3841)
* [@wfelipew](https://github.com/wfelipew) made their first contribution in [#3859](https://github.com/sqlfluff/sqlfluff/pull/3859)
* [@moreaupascal56](https://github.com/moreaupascal56) made their first contribution in [#3858](https://github.com/sqlfluff/sqlfluff/pull/3858)
* [@rglbr](https://github.com/rglbr) made their first contribution in [#3862](https://github.com/sqlfluff/sqlfluff/pull/3862)
* [@differgroup](https://github.com/differgroup) made their first contribution in [#3867](https://github.com/sqlfluff/sqlfluff/pull/3867)

## [1.3.1] - 2022-09-09

## Highlights

* More refactoring of parse structures in preparation for upcoming refactor of
  formatting/whitespace rules.
* Fixes some bugs in L003 (indentation).
* New config flag `large_file_skip_byte_limit` which applies **prior to**
  loading the file.

## What’s Changed

* Snowflake: Fix syntax errors in tests [#3834](https://github.com/sqlfluff/sqlfluff/pull/3834) [@JamesRTaylor](https://github.com/JamesRTaylor)
* Add support for additional magic methods on DummyUndefined [#3835](https://github.com/sqlfluff/sqlfluff/pull/3835) [@barrywhart](https://github.com/barrywhart)
* MySQL: support variable assignments by assignment operator := [#3829](https://github.com/sqlfluff/sqlfluff/pull/3829) [@yoichi](https://github.com/yoichi)
* MYSQL: improve lexing for single-quoted strings [#3831](https://github.com/sqlfluff/sqlfluff/pull/3831) [@mdahlman](https://github.com/mdahlman)
* MySQL: More support for index definition in CREATE TABLE [#3826](https://github.com/sqlfluff/sqlfluff/pull/3826) [@yoichi](https://github.com/yoichi)
* Typed matching and ripping out the rest of .name [#3819](https://github.com/sqlfluff/sqlfluff/pull/3819) [@alanmcruickshank](https://github.com/alanmcruickshank)
* sparksql dialect to support lambda expressions (->) [#3821](https://github.com/sqlfluff/sqlfluff/pull/3821) [@juhoautio](https://github.com/juhoautio)
* Fixed broken main branch [#3825](https://github.com/sqlfluff/sqlfluff/pull/3825) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Enable file name logging for multi-files w/ --show-lint-violations flag [#3788](https://github.com/sqlfluff/sqlfluff/pull/3788) [@thechopkins](https://github.com/thechopkins)
* Take database and schema out of Snowflake reserved keywords list [#3818](https://github.com/sqlfluff/sqlfluff/pull/3818) [@NiallRees](https://github.com/NiallRees)
* Remove a chunk of name references [#3814](https://github.com/sqlfluff/sqlfluff/pull/3814) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix typo in Snowflake dialect  [#3813](https://github.com/sqlfluff/sqlfluff/pull/3813) [@Gal40n04ek](https://github.com/Gal40n04ek)
* Allow the use of libraries in macro definitions [#3803](https://github.com/sqlfluff/sqlfluff/pull/3803) [@bjgbeelen](https://github.com/bjgbeelen)
* Indentation fixes and rule logging improvements [#3808](https://github.com/sqlfluff/sqlfluff/pull/3808) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fixes a recursion error in  JinjaTemplater handling of undefined values [#3809](https://github.com/sqlfluff/sqlfluff/pull/3809) [@barrywhart](https://github.com/barrywhart)
* Snowflake: extend `GRANT` syntax [#3807](https://github.com/sqlfluff/sqlfluff/pull/3807) [@Gal40n04ek](https://github.com/Gal40n04ek)
* add warehouse_type in snowflake dialect [#3805](https://github.com/sqlfluff/sqlfluff/pull/3805) [@Gal40n04ek](https://github.com/Gal40n04ek)
* add Create Notification Integration syntax [#3801](https://github.com/sqlfluff/sqlfluff/pull/3801) [@Gal40n04ek](https://github.com/Gal40n04ek)
* T-SQL: fix parsing PARTITION BY NULL in window function [#3790](https://github.com/sqlfluff/sqlfluff/pull/3790) [@fmms](https://github.com/fmms)
* SparkSQL: Update L014 rule to not flag Delta Change Data Feed Session & Table Property [#3689](https://github.com/sqlfluff/sqlfluff/pull/3689) [@R7L208](https://github.com/R7L208)
* Snowflake: OVER (ORDER BY) clause required for first_value (fixes #3797) [#3798](https://github.com/sqlfluff/sqlfluff/pull/3798) [@JamesRTaylor](https://github.com/JamesRTaylor)
* add Alter Pipe syntax for snowflake dialect [#3796](https://github.com/sqlfluff/sqlfluff/pull/3796) [@Gal40n04ek](https://github.com/Gal40n04ek)
* BigQuery: Parse WEEK(<WEEKDAY>) in date_part [#3787](https://github.com/sqlfluff/sqlfluff/pull/3787) [@yoichi](https://github.com/yoichi)
* Postgres: Support setting user properties using intrinsic ON & OFF values [#3793](https://github.com/sqlfluff/sqlfluff/pull/3793) [@chris-codaio](https://github.com/chris-codaio)
* extend SF dialect for File Format statements [#3774](https://github.com/sqlfluff/sqlfluff/pull/3774) [@Gal40n04ek](https://github.com/Gal40n04ek)
* Add QUALIFY to SparkSQL dialect [#3778](https://github.com/sqlfluff/sqlfluff/pull/3778) [@ThijsKoot](https://github.com/ThijsKoot)
* fix regex for S3Path [#3782](https://github.com/sqlfluff/sqlfluff/pull/3782) [@Gal40n04ek](https://github.com/Gal40n04ek)
* Snowflake: add Optional parameter ERROR INTEGRATION for PIPE [#3785](https://github.com/sqlfluff/sqlfluff/pull/3785) [@Gal40n04ek](https://github.com/Gal40n04ek)
* Add a file size check in bytes [#3770](https://github.com/sqlfluff/sqlfluff/pull/3770) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Require importlib_metadata >=1.0.0 [#3769](https://github.com/sqlfluff/sqlfluff/pull/3769) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@Gal40n04ek](https://github.com/Gal40n04ek) made their first contribution in [#3785](https://github.com/sqlfluff/sqlfluff/pull/3785)
* [@ThijsKoot](https://github.com/ThijsKoot) made their first contribution in [#3778](https://github.com/sqlfluff/sqlfluff/pull/3778)
* [@chris-codaio](https://github.com/chris-codaio) made their first contribution in [#3793](https://github.com/sqlfluff/sqlfluff/pull/3793)
* [@JamesRTaylor](https://github.com/JamesRTaylor) made their first contribution in [#3798](https://github.com/sqlfluff/sqlfluff/pull/3798)
* [@fmms](https://github.com/fmms) made their first contribution in [#3790](https://github.com/sqlfluff/sqlfluff/pull/3790)
* [@bjgbeelen](https://github.com/bjgbeelen) made their first contribution in [#3803](https://github.com/sqlfluff/sqlfluff/pull/3803)
* [@thechopkins](https://github.com/thechopkins) made their first contribution in [#3788](https://github.com/sqlfluff/sqlfluff/pull/3788)

## [1.3.0] - 2022-08-21

## Highlights

This release brings several potentially breaking changes to the underlying parse tree. For
users of the cli tool in a linting context you should notice no change. If however
your application relies on the structure of the SQLFluff parse tree or the naming of certain
elements within the yaml format, then this may not be a drop-in replacement. Specifically:
- The addition of a new `end_of_file` meta segment at the end of the parse structure.
- The addition of a `template_loop` meta segment to signify a jump backward in the source
  file within a loop structure (e.g. a jinja for loop).
- Much more specific types on some raw segments, in particular `identifier` and `literal`
  type segments will now appear in the parse tree with their more specific type (which
  used to be called `name`) e.g. `naked_identifier`, `quoted_identifier`, `numeric_literal` etc...

If using the python api, the _parent_ type (such as `identifier`) will still register if
you call `.is_type("identifier")`, as this function checks all inherited types. However the
eventual type returned by `.get_type()` will now be (in most cases) what used to be accessible
at `.name`. The `name` attribute will be deprecated in a future release.

Other highlights:
* New command-line option `--show-lint-violations` to show details on unfixable errors when
  running `sqlfluff fix`.
* Improved consistency of process exit codes.
* Short CLI options for many common options.
* Jinja templater: When `--ignore=templating` is enabled, undefined Jinja variables now take
  on "reasonable" default values rather than blank string (`""`). This can streamline initial
  rollout of SQLFluff by reducing or eliminating the need to configure templater variables.

There are also a _ton_ of other features and bug fixes in this release, including first-time
contributions from **11 new contributors**! 🎉

## What’s Changed

* T-SQL: ALTER TABLE DROP COLUMN [#3749](https://github.com/sqlfluff/sqlfluff/pull/3749) [@greg-finley](https://github.com/greg-finley)
* Add "# pragma: no cover" to work around sporadic, spurious coverage failure [#3767](https://github.com/sqlfluff/sqlfluff/pull/3767) [@barrywhart](https://github.com/barrywhart)
* Add end_of_file and template_loop markers [#3766](https://github.com/sqlfluff/sqlfluff/pull/3766) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Provide usage examples for new users [#3765](https://github.com/sqlfluff/sqlfluff/pull/3765) [@sirlark](https://github.com/sirlark)
* SQLite: deferrable in create table statement [#3757](https://github.com/sqlfluff/sqlfluff/pull/3757) [@RossOkuno](https://github.com/RossOkuno)
* When ignore=templating and fix_even_unparsable=True, provide defaults for missing vars [#3753](https://github.com/sqlfluff/sqlfluff/pull/3753) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Support Materialized Views [#3759](https://github.com/sqlfluff/sqlfluff/pull/3759) [@yoichi](https://github.com/yoichi)
* Enhance L062 to ignore blocked words in comments [#3754](https://github.com/sqlfluff/sqlfluff/pull/3754) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug where undefined Jinja variable in macro file crashes linter [#3751](https://github.com/sqlfluff/sqlfluff/pull/3751) [@barrywhart](https://github.com/barrywhart)
* Migrate analysis, functional and testing to utils [#3743](https://github.com/sqlfluff/sqlfluff/pull/3743) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Build out rule crawling mechanisms [#3717](https://github.com/sqlfluff/sqlfluff/pull/3717) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add current_timestamp to Redshift as a bare function [#3741](https://github.com/sqlfluff/sqlfluff/pull/3741) [@RossOkuno](https://github.com/RossOkuno)
* BigQuery: Fix parsing parameterized data types [#3735](https://github.com/sqlfluff/sqlfluff/pull/3735) [@yoichi](https://github.com/yoichi)
* Change MySQL Create Statement Equals Segment to Optional [#3730](https://github.com/sqlfluff/sqlfluff/pull/3730) [@keyem4251](https://github.com/keyem4251)
* SQLite: add parsing of INSERT statement [#3734](https://github.com/sqlfluff/sqlfluff/pull/3734) [@imrehg](https://github.com/imrehg)
* SPARKSQL: Support Delta Lake Drop Column Clause in `ALTER TABLE` [#3727](https://github.com/sqlfluff/sqlfluff/pull/3727) [@R7L208](https://github.com/R7L208)
* Add short versions of several cli options [#3732](https://github.com/sqlfluff/sqlfluff/pull/3732) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Build out type hints in Grammars [#3718](https://github.com/sqlfluff/sqlfluff/pull/3718) [@alanmcruickshank](https://github.com/alanmcruickshank)
* dbt 1.3.0 compatibility [#3708](https://github.com/sqlfluff/sqlfluff/pull/3708) [@edgarrmondragon](https://github.com/edgarrmondragon)
* Revise no cover direction and remove unused code. [#3723](https://github.com/sqlfluff/sqlfluff/pull/3723) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Update broken flattr link [#3720](https://github.com/sqlfluff/sqlfluff/pull/3720) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery: remove `key` from unreserved keywords list [#3719](https://github.com/sqlfluff/sqlfluff/pull/3719) [@sabrikaragonen](https://github.com/sabrikaragonen)
* Bigquery reset primary and foreign keys [#3714](https://github.com/sqlfluff/sqlfluff/pull/3714) [@sabrikaragonen](https://github.com/sabrikaragonen)
* Name Deprecation (Part 1) [#3701](https://github.com/sqlfluff/sqlfluff/pull/3701) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Teradata: Add two TdTableConstraints [#3690](https://github.com/sqlfluff/sqlfluff/pull/3690) [@greg-finley](https://github.com/greg-finley)
* Redshift: support expressions in array accessors [#3706](https://github.com/sqlfluff/sqlfluff/pull/3706) [@chronitis](https://github.com/chronitis)
* Handle logging issues at teardown [#3703](https://github.com/sqlfluff/sqlfluff/pull/3703) [@alanmcruickshank](https://github.com/alanmcruickshank)
* L028, L032: Fix bug where fixes were copying templated table names [#3699](https://github.com/sqlfluff/sqlfluff/pull/3699) [@barrywhart](https://github.com/barrywhart)
* L042: Autofix sometimes results in "fix looping", hitting the linter "loop limit" [#3697](https://github.com/sqlfluff/sqlfluff/pull/3697) [@barrywhart](https://github.com/barrywhart)
* L042: Address corner cases where fix corrupts the SQL [#3694](https://github.com/sqlfluff/sqlfluff/pull/3694) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Properly parse collation names [#3686](https://github.com/sqlfluff/sqlfluff/pull/3686) [@borchero](https://github.com/borchero)
* Allow escaping single quotes in single-quoted literal with '' [#3682](https://github.com/sqlfluff/sqlfluff/pull/3682) [@pdebelak](https://github.com/pdebelak)
* T-SQL: Fix indentation after JOIN/APPLY clauses with no ON statement [#3684](https://github.com/sqlfluff/sqlfluff/pull/3684) [@borchero](https://github.com/borchero)
* T-SQL: Parse `DATEPART` date type as date type instead of column name [#3681](https://github.com/sqlfluff/sqlfluff/pull/3681) [@borchero](https://github.com/borchero)
* T-SQL: Allow `COLLATE` clause in `JOIN` conditions [#3680](https://github.com/sqlfluff/sqlfluff/pull/3680) [@borchero](https://github.com/borchero)
* T-SQL: Fix parsing of CREATE VIEW statements with column name syntax [#3669](https://github.com/sqlfluff/sqlfluff/pull/3669) [@borchero](https://github.com/borchero)
* Fix typo in github issue template [#3674](https://github.com/sqlfluff/sqlfluff/pull/3674) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add Athena issue label [#3676](https://github.com/sqlfluff/sqlfluff/pull/3676) [@greg-finley](https://github.com/greg-finley)
* Set issue dialect labels via Github Actions [#3666](https://github.com/sqlfluff/sqlfluff/pull/3666) [@greg-finley](https://github.com/greg-finley)
* Allow configuration of processes from config [#3662](https://github.com/sqlfluff/sqlfluff/pull/3662) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Reposition before recursion in fixes to avoid internal error [#3658](https://github.com/sqlfluff/sqlfluff/pull/3658) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Use UUIDs for matching [#3661](https://github.com/sqlfluff/sqlfluff/pull/3661) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: Add dialect-specific bare functions [#3660](https://github.com/sqlfluff/sqlfluff/pull/3660) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Add `CALL` Support [#3659](https://github.com/sqlfluff/sqlfluff/pull/3659) [@WittierDinosaur](https://github.com/WittierDinosaur)
* ANSI - Add support for `INTERSECT ALL` and `EXCEPT ALL` [#3657](https://github.com/sqlfluff/sqlfluff/pull/3657) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Option to show errors on fix [#3610](https://github.com/sqlfluff/sqlfluff/pull/3610) [@chaimt](https://github.com/chaimt)
* L042: Fix internal error "Attempted to make a parent marker from multiple files" [#3655](https://github.com/sqlfluff/sqlfluff/pull/3655) [@barrywhart](https://github.com/barrywhart)
* L026: Add support for `merge_statement` [#3654](https://github.com/sqlfluff/sqlfluff/pull/3654) [@barrywhart](https://github.com/barrywhart)
* Add handling for Redshift `CONVERT` function data type argument [#3653](https://github.com/sqlfluff/sqlfluff/pull/3653) [@pdebelak](https://github.com/pdebelak)
* Deduplicate files before and during templating [#3629](https://github.com/sqlfluff/sqlfluff/pull/3629) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Rationalise Rule Imports [#3631](https://github.com/sqlfluff/sqlfluff/pull/3631) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle Jinja `{% call ... %}` blocks [#3648](https://github.com/sqlfluff/sqlfluff/pull/3648) [@barrywhart](https://github.com/barrywhart)
* SPARKSQL: Add Delta Lake Constraints syntax to `ALTER TABLE` [#3643](https://github.com/sqlfluff/sqlfluff/pull/3643) [@R7L208](https://github.com/R7L208)
* Redshift: syntax for array unnesting with index [#3646](https://github.com/sqlfluff/sqlfluff/pull/3646) [@chronitis](https://github.com/chronitis)
* Snowflake - `ALTER TABLE IF EXISTS` and `WHEN SYSTEM$STREAM_HAS_DATA()` [#3641](https://github.com/sqlfluff/sqlfluff/pull/3641) [@chrisalexeev](https://github.com/chrisalexeev)
* L057: In BigQuery, allow hyphens by default [#3645](https://github.com/sqlfluff/sqlfluff/pull/3645) [@barrywhart](https://github.com/barrywhart)
* Better messages for partial indentation in L003 [#3634](https://github.com/sqlfluff/sqlfluff/pull/3634) [@pdebelak](https://github.com/pdebelak)
* Add `INTEGER` to `PrimitiveTypeSegment` for Sparksql [#3624](https://github.com/sqlfluff/sqlfluff/pull/3624) [@ciwassano](https://github.com/ciwassano)
* Bump version in gettingstarted.rst via the release script [#3642](https://github.com/sqlfluff/sqlfluff/pull/3642) [@greg-finley](https://github.com/greg-finley)
* Improve handling of BigQuery hyphenated table names [#3638](https://github.com/sqlfluff/sqlfluff/pull/3638) [@barrywhart](https://github.com/barrywhart)
* update sqlfluff version in gettingstareted.rst [#3639](https://github.com/sqlfluff/sqlfluff/pull/3639) [@keyem4251](https://github.com/keyem4251)
* L016: Ignore jinja comments if `ignore_comment_clauses=True` [#3637](https://github.com/sqlfluff/sqlfluff/pull/3637) [@barrywhart](https://github.com/barrywhart)
* Add errors for redundant definitions. [#3626](https://github.com/sqlfluff/sqlfluff/pull/3626) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Object Literals [#3620](https://github.com/sqlfluff/sqlfluff/pull/3620) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Dialect Crumbs [#3625](https://github.com/sqlfluff/sqlfluff/pull/3625) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Consistent return codes [#3608](https://github.com/sqlfluff/sqlfluff/pull/3608) [@alanmcruickshank](https://github.com/alanmcruickshank)


## New Contributors
* [@keyem4251](https://github.com/keyem4251) made their first contribution in [#3639](https://github.com/sqlfluff/sqlfluff/pull/3639)
* [@ciwassano](https://github.com/ciwassano) made their first contribution in [#3624](https://github.com/sqlfluff/sqlfluff/pull/3624)
* [@chronitis](https://github.com/chronitis) made their first contribution in [#3646](https://github.com/sqlfluff/sqlfluff/pull/3646)
* [@chaimt](https://github.com/chaimt) made their first contribution in [#3610](https://github.com/sqlfluff/sqlfluff/pull/3610)
* [@borchero](https://github.com/borchero) made their first contribution in [#3669](https://github.com/sqlfluff/sqlfluff/pull/3669)
* [@sabrikaragonen](https://github.com/sabrikaragonen) made their first contribution in [#3714](https://github.com/sqlfluff/sqlfluff/pull/3714)
* [@edgarrmondragon](https://github.com/edgarrmondragon) made their first contribution in [#3708](https://github.com/sqlfluff/sqlfluff/pull/3708)
* [@imrehg](https://github.com/imrehg) made their first contribution in [#3734](https://github.com/sqlfluff/sqlfluff/pull/3734)
* [@yoichi](https://github.com/yoichi) made their first contribution in [#3735](https://github.com/sqlfluff/sqlfluff/pull/3735)
* [@RossOkuno](https://github.com/RossOkuno) made their first contribution in [#3741](https://github.com/sqlfluff/sqlfluff/pull/3741)
* [@sirlark](https://github.com/sirlark) made their first contribution in [#3765](https://github.com/sqlfluff/sqlfluff/pull/3765)

## [1.2.1] - 2022-07-15

## Highlights

This is primarily a bugfix release to resolve an issue with the 1.2.0 release
where the new version of `sqlfluff-templater-dbt` relied on functionality
from the new version of `sqlfluff` but the package configuration had not
been updated. Versions of the two packages are now pinned together.

## What’s Changed

* Pin sqlfluff-templater-dbt via release script [#3613](https://github.com/sqlfluff/sqlfluff/pull/3613) [@greg-finley](https://github.com/greg-finley)
* Specifying comma delimited is unnecessary [#3616](https://github.com/sqlfluff/sqlfluff/pull/3616) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Handle redshift temporary tables with # at the beginning of name [#3615](https://github.com/sqlfluff/sqlfluff/pull/3615) [@pdebelak](https://github.com/pdebelak)


## [1.2.0] - 2022-07-13

## Highlights
Major changes include:
* Adding AWS Athena as a dialect.
* A fix routine for L046 (whitespace in jinja tags), and the mechanisms for
  more source-only fixes in future.
* By default, large files (over 20k characters) are now skipped by sqlfluff. This
  limit is configurable and disable-able but exists as a sensible default to avoid
  the performance overhead of linting *very* large files.
* For the dbt templater, fatal compilation errors now no longer stop linting, and
  these files are now skipped instead. This enables projects to continue linting
  beyond the offending file and much better logging information to enable better
  debugging.

## What’s Changed

* Improve documentation for custom implemented rules [#3604](https://github.com/sqlfluff/sqlfluff/pull/3603) [@Aditya-Tripuraneni](https://github.com/Aditya-Tripuraneni)
* Add a skip and better logging for fatal dbt issues [#3603](https://github.com/sqlfluff/sqlfluff/pull/3603) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add large file check [#3600](https://github.com/sqlfluff/sqlfluff/pull/3600) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Oracle: extend support for `ALTER TABLE` [#3596](https://github.com/sqlfluff/sqlfluff/pull/3596) [@davidfuhr](https://github.com/davidfuhr)
* Immutability fixes [#3428](https://github.com/sqlfluff/sqlfluff/pull/3428) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Struct type should be a segment [#3591](https://github.com/sqlfluff/sqlfluff/pull/3591) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix Bracketed Struct issue [#3590](https://github.com/sqlfluff/sqlfluff/pull/3590) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Allow spaces and multiple signs for numeric literals [#3581](https://github.com/sqlfluff/sqlfluff/pull/3581) [@tunetheweb](https://github.com/tunetheweb)
* Add source fixing capability and fix routines for L046 [#3578](https://github.com/sqlfluff/sqlfluff/pull/3578) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Small grammar cleanup in team rollout docs [#3584](https://github.com/sqlfluff/sqlfluff/pull/3584) [@theianrobertson](https://github.com/theianrobertson)
* Postgres: `CREATE COLLATION` support [#3571](https://github.com/sqlfluff/sqlfluff/pull/3571) [@greg-finley](https://github.com/greg-finley)
* Redshift: Add `TOP X` to select clause modifiers [#3582](https://github.com/sqlfluff/sqlfluff/pull/3582) [@pdebelak](https://github.com/pdebelak)
* Postgres: Small fixes to `COMMENT ON` [#3566](https://github.com/sqlfluff/sqlfluff/pull/3566) [@greg-finley](https://github.com/greg-finley)
* Support MySQL system variables [#3576](https://github.com/sqlfluff/sqlfluff/pull/3576) [@qgallet](https://github.com/qgallet)
* Allow no alias for selects in CTEs with a column list [#3580](https://github.com/sqlfluff/sqlfluff/pull/3580) [@pdebelak](https://github.com/pdebelak)
* New dialect AWS Athena [#3551](https://github.com/sqlfluff/sqlfluff/pull/3551) [@cmotta](https://github.com/cmotta)
* Split apart `fix_string()`. [#3568](https://github.com/sqlfluff/sqlfluff/pull/3568) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fix incorrect L022 with postgres dialect with CTE argument list [#3570](https://github.com/sqlfluff/sqlfluff/pull/3570) [@pdebelak](https://github.com/pdebelak)
* Simplify lint fixing (prep for source fixes) [#3567](https://github.com/sqlfluff/sqlfluff/pull/3567) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Exclude .coverage.py from linting [#3564](https://github.com/sqlfluff/sqlfluff/pull/3564) [@zidder](https://github.com/zidder)
* L016: `ignore_comment_clauses` not working for postgres dialect [#3549](https://github.com/sqlfluff/sqlfluff/pull/3549) [@barrywhart](https://github.com/barrywhart)
* Groundwork for a fix routine for L046 [#3552](https://github.com/sqlfluff/sqlfluff/pull/3552) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add better handling for SQLFluffUserError when running core cli commands [#3431](https://github.com/sqlfluff/sqlfluff/pull/3431) [@alanmcruickshank](https://github.com/alanmcruickshank)

## New Contributors

* [@pdebelak](https://github.com/pdebelak) made their first contribution in [#3570](https://github.com/sqlfluff/sqlfluff/pull/3570)
* [@cmotta](https://github.com/cmotta) made their first contribution in [#3551](https://github.com/sqlfluff/sqlfluff/pull/3551)
* [@qgallet](https://github.com/qgallet) made their first contribution in [#3576](https://github.com/sqlfluff/sqlfluff/pull/3576)
* [@theianrobertson](https://github.com/theianrobertson) made their first contribution in [#3584](https://github.com/sqlfluff/sqlfluff/pull/3584)
* [@davidfuhr](https://github.com/davidfuhr) made their first contribution in [#3596](https://github.com/sqlfluff/sqlfluff/pull/3596)
* [@Aditya-Tripuraneni](https://github.com/Aditya-Tripuraneni) made their first contribution in [#3604](https://github.com/sqlfluff/sqlfluff/pull/3596)

## [1.1.0] - 2022-07-03

## Highlights
Major changes include:
* L066 - New rule to allow you to set min/max length requirements for aliases to ensure they are meaningful
* L062 - addition of `blocked_regex` as well as `blocked_words`
* L025 - fix several corner cases where aliases were removed inappropriately
* L059 is now disabled by default for Postgres
* Many more dialect improvements and bug fixes.

## Highlights

## What’s Changed

* L025: Derived query requires alias -- also handle UNION, etc. [#3548](https://github.com/sqlfluff/sqlfluff/pull/3548) [@barrywhart](https://github.com/barrywhart)
* L025 should not remove aliases from derived queries [#3546](https://github.com/sqlfluff/sqlfluff/pull/3546) [@barrywhart](https://github.com/barrywhart)
* T-SQL keyword functions should be treated as keywords [#3540](https://github.com/sqlfluff/sqlfluff/pull/3540) [@tunetheweb](https://github.com/tunetheweb)
* Fix issue where "--nocolor" is ignored [#3536)(https://github.com/sqlfluff/sqlfluff/pull/3536) [@barrywhart](https://github.com/barrywhart)
* Clickhouse: allow `FINAL` modifier [#3534](https://github.com/sqlfluff/sqlfluff/pull/3534) [@ThomAub](https://github.com/ThomAub)
* L018 change to just check for newlines rather than alignment [#3499](https://github.com/sqlfluff/sqlfluff/pull/3499) [@zidder](https://github.com/zidder)
* SparkSQL: Update terminator grammar for `HAVING`, `WHERE`, `GROUP BY` [#3526](https://github.com/sqlfluff/sqlfluff/pull/3526) [@R7L208](https://github.com/R7L208)
* Fix L025 false positive for T-SQL `VALUES` clause [#3533](https://github.com/sqlfluff/sqlfluff/pull/3533) [@barrywhart](https://github.com/barrywhart)
* New rule L066 for enforcing table alias lengths [#3384](https://github.com/sqlfluff/sqlfluff/pull/3384) [@f0rk](https://github.com/f0rk)
* Redshift: `CALL` statement [#3529](https://github.com/sqlfluff/sqlfluff/pull/3529) [@greg-finley](https://github.com/greg-finley)
* Core: Compile regexes at init time to avoid overhead [#3511](https://github.com/sqlfluff/sqlfluff/pull/3511) [@judahrand](https://github.com/judahrand)
* Disable L059 by default for Postgres [#3528](https://github.com/sqlfluff/sqlfluff/pull/3528) [@tunetheweb](https://github.com/tunetheweb)
* Core: Add `MultiStringParser` to match a collection of strings [#3510](https://github.com/sqlfluff/sqlfluff/pull/3510) [@judahrand](https://github.com/judahrand)
* SQLite: `PRIMARY KEY AUTOINCREMENT` [#3527](https://github.com/sqlfluff/sqlfluff/pull/3527) [@greg-finley](https://github.com/greg-finley)
* MySQL: Support `LOAD DATA` [#3518](https://github.com/sqlfluff/sqlfluff/pull/3518) [@greg-finley](https://github.com/greg-finley)
* Redshift: `GRANT EXECUTE ON PROCEDURES` [#3516](https://github.com/sqlfluff/sqlfluff/pull/3516) [@greg-finley](https://github.com/greg-finley)
* Allow `DEFAULT` expression in Redshift `ALTER TABLE ADD COLUMN` statements [#3513](https://github.com/sqlfluff/sqlfluff/pull/3513) [@menzenski](https://github.com/menzenski)
* BigQuery: Fix parsing of Array creation from full subquery [#3502](https://github.com/sqlfluff/sqlfluff/pull/3502) [@judahrand](https://github.com/judahrand)
* SparkSQL: Allow dateparts as table aliases [#3500](https://github.com/sqlfluff/sqlfluff/pull/3500) [@R7L208](https://github.com/R7L208)
* Fix `load_macros_from_path` to actually support multiple paths [#3488](https://github.com/sqlfluff/sqlfluff/pull/3488) [@emancu](https://github.com/emancu)
* Allow linter to apply fixes spanning more than 2 slices [#3492](https://github.com/sqlfluff/sqlfluff/pull/3492) [@barrywhart](https://github.com/barrywhart)
* Fix L022 false positive when the CTE definition has a column list [#3490](https://github.com/sqlfluff/sqlfluff/pull/3490) [@barrywhart](https://github.com/barrywhart)
* SparkSQL: Support for Delta `RESTORE` statement [#3486](https://github.com/sqlfluff/sqlfluff/pull/3486) [@R7L208](https://github.com/R7L208)
* Add values function to `SET` clause [#3483](https://github.com/sqlfluff/sqlfluff/pull/3483) [@hgranthorner](https://github.com/hgranthorner)
* SparkSQL: Support for `CONVERT TO DELTA` command [#3482](https://github.com/sqlfluff/sqlfluff/pull/3482) [@R7L208](https://github.com/R7L208)
* BigQuery: Remaining procedural statements [#3473](https://github.com/sqlfluff/sqlfluff/pull/3473) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: support grouping sets [#3477](https://github.com/sqlfluff/sqlfluff/pull/3477) [@tunetheweb](https://github.com/tunetheweb)
* SparkSQL: Support for Delta syntax to create manifest files through the `GENERATE` command [#3478](https://github.com/sqlfluff/sqlfluff/pull/3478) [@R7L208](https://github.com/R7L208)
* Add config for optionally indenting contents of `ON` blocks [#3471](https://github.com/sqlfluff/sqlfluff/pull/3471) [@PeterBalsdon](https://github.com/PeterBalsdon)
* L026: check standalone aliases as well as table aliases [#3470](https://github.com/sqlfluff/sqlfluff/pull/3470) [@tunetheweb](https://github.com/tunetheweb)
* L045: Add handling for nested queries and CTEs [#3468](https://github.com/sqlfluff/sqlfluff/pull/3468) [@barrywhart](https://github.com/barrywhart)
* L062: add `blocked_regex` support [#3467](https://github.com/sqlfluff/sqlfluff/pull/3467) [@tunetheweb](https://github.com/tunetheweb)
* SparkSQL: Support for the Delta `DESCRIBE DETAIL` command [#3465](https://github.com/sqlfluff/sqlfluff/pull/3465) [@R7L208](https://github.com/R7L208)

## New Contributors

* [@PeterBalsdon](https://github.com/PeterBalsdon) made their first contribution in [#3471](https://github.com/sqlfluff/sqlfluff/pull/3471)
* [@hgranthorner](https://github.com/hgranthorner) made their first contribution in [#3483](https://github.com/sqlfluff/sqlfluff/pull/3483)
* [@emancu](https://github.com/emancu) made their first contribution in [#3488](https://github.com/sqlfluff/sqlfluff/pull/3488)
* [@judahrand](https://github.com/judahrand) made their first contribution in [#3502](https://github.com/sqlfluff/sqlfluff/pull/3502)
* [@f0rk](https://github.com/f0rk) made their first contribution in [#3384](https://github.com/sqlfluff/sqlfluff/pull/3384)
* [@zidder](https://github.com/zidder) made their first contribution in [#3499](https://github.com/sqlfluff/sqlfluff/pull/3499)
* [@ThomAub](https://github.com/ThomAub) made their first contribution in [#3534](https://github.com/sqlfluff/sqlfluff/pull/3534)

## [1.0.0] - 2022-06-17

## Highlights

This is the first _stable_ release of SQLFluff 🎉🎉🎉.

- _Does this mean there are no more bugs?_ **No.**
- _Does this mean we're going to stop developing new features?_ **No.**
- _Does this mean that this is a tool that is now broadly usable for many teams?_ **Yes.**

We've intentionally chosen to release 1.0.0 at a time of relative stability within SQLFluff and
not at a time when new big structural changes are being made. This means that there's a good
chance that this release is broadly usable. This also recognises that through the hard work
of a _huge_ number of contributors that we've built out this from a fringe tool, to something
which gets over 500k downloads a month and over 4k stars on Github.

There's still a lot to do, and some more exciting things on the horizon. If you want to be
part of this and join the team of contributors, come and hang out in our [slack community](https://join.slack.com/t/sqlfluff/shared_invite/zt-o1f4x0e8-pZzarAIlQmKj_6ZwD16w0g)
or on our [twitter account](https://twitter.com/SQLFluff) where people can help you get
started. If you're a long time user, keep submitting bug reports and inputting
on [issues on Github](https://github.com/sqlfluff/sqlfluff/issues).

If you've never used SQLFluff before, or are hesitant about starting to use it in your day
to day work, now might be a good time to try it. We have guides on how to [get started with the tool](https://docs.sqlfluff.com/en/stable/gettingstarted.html),
and how to [get started with rolling out to a team](https://docs.sqlfluff.com/en/stable/teamrollout.html) in our docs.

## What’s Changed

* Swap to skip file if not found [#3464](https://github.com/sqlfluff/sqlfluff/pull/3464) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Postgres: treat `GENERATE_SERIES` as a value table function [#3463](https://github.com/sqlfluff/sqlfluff/pull/3463) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Support multiple `CONSTRAINTS` in `CREATE DOMAIN` [#3460](https://github.com/sqlfluff/sqlfluff/pull/3460) [@tunetheweb](https://github.com/tunetheweb)
* Redshift: Add `ANYELEMENT` support [#3458](https://github.com/sqlfluff/sqlfluff/pull/3458) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Optional select clause elements and better `ON CONFLICT` support [#3452](https://github.com/sqlfluff/sqlfluff/pull/3452) [@tunetheweb](https://github.com/tunetheweb)
* Add ClickHouse as a dialect [#3448](https://github.com/sqlfluff/sqlfluff/pull/3448) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: allow keywords in qualified column references [#3450](https://github.com/sqlfluff/sqlfluff/pull/3450) [@tunetheweb](https://github.com/tunetheweb)
* Remove Baron Schwatz Dead Link [#3453](https://github.com/sqlfluff/sqlfluff/pull/3453) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Finish `ALTER TYPE` [#3451](https://github.com/sqlfluff/sqlfluff/pull/3451) [@greg-finley](https://github.com/greg-finley)
* SparkSQL: Add Delta Syntax for `DESCRIBE HISTORY` statement [#3447](https://github.com/sqlfluff/sqlfluff/pull/3447) [@R7L208](https://github.com/R7L208)
* Snowflake: Support Stage data file parameters in `FROM` clauses [#3446](https://github.com/sqlfluff/sqlfluff/pull/3446) [@tunetheweb](https://github.com/tunetheweb)
* Redshift: Support Object unpivoting [#3441](https://github.com/sqlfluff/sqlfluff/pull/3441) [@tunetheweb](https://github.com/tunetheweb)
* Python script to automate release [#3403](https://github.com/sqlfluff/sqlfluff/pull/3403) [@greg-finley](https://github.com/greg-finley)
* Remove Delta Lake Reference in README.md [#3444](https://github.com/sqlfluff/sqlfluff/pull/3444) [@R7L208](https://github.com/R7L208)
* Add `databricks` dialect as an alias for `sparksql` dialect [#3440](https://github.com/sqlfluff/sqlfluff/pull/3440) [@R7L208](https://github.com/R7L208)
* Make all Postgres identifiers quotable  [#3442](https://github.com/sqlfluff/sqlfluff/pull/3442) [@tunetheweb](https://github.com/tunetheweb)
* Update JinjaAnalyzer and JinjaTracer to handle `{% block %}` [#3436](https://github.com/sqlfluff/sqlfluff/pull/3436) [@barrywhart](https://github.com/barrywhart)
* SparkSQL: Add support for Delta `VACUUM` statement [#3439](https://github.com/sqlfluff/sqlfluff/pull/3439) [@R7L208](https://github.com/R7L208)
* Warning for parsing errors extended to all dialects [#3411](https://github.com/sqlfluff/sqlfluff/pull/3411) [@mdahlman](https://github.com/mdahlman)
* Handle templater validation errors more gracefully [#3433](https://github.com/sqlfluff/sqlfluff/pull/3433) [@alanmcruickshank](https://github.com/alanmcruickshank)
* MYSQL: allow for escaped single quotes [#3424](https://github.com/sqlfluff/sqlfluff/pull/3424) [@mdahlman](https://github.com/mdahlman)
* L027: Fix false positives by reverting the PR for issue #2992: Check table aliases exist [#3435](https://github.com/sqlfluff/sqlfluff/pull/3435) [@barrywhart](https://github.com/barrywhart)
* Allow `numeric_dollar` templater to have curly braces, update `dollar` + `numeric_dollar` templater examples in docs [#3432](https://github.com/sqlfluff/sqlfluff/pull/3432) [@menzenski](https://github.com/menzenski)
* Allow Redshift `IDENTITY` column `(seed, step)` to be optional [#3430](https://github.com/sqlfluff/sqlfluff/pull/3430) [@menzenski](https://github.com/menzenski)
* L036: Make wildcard behavior configurable [#3426](https://github.com/sqlfluff/sqlfluff/pull/3426) [@barrywhart](https://github.com/barrywhart)
* L034: Don't autofix if numeric column references [#3423](https://github.com/sqlfluff/sqlfluff/pull/3423) [@barrywhart](https://github.com/barrywhart)
* L036: Treat wildcard as multiple select targets (i.e. separate line) [#3422](https://github.com/sqlfluff/sqlfluff/pull/3422) [@barrywhart](https://github.com/barrywhart)
* Snowflake: IDENTIFIER pseudo-function [#3409](https://github.com/sqlfluff/sqlfluff/pull/3409) [@mdahlman](https://github.com/mdahlman)
* SNOWFLAKE: Fully referenced object names in clone statements [#3414](https://github.com/sqlfluff/sqlfluff/pull/3414) [@mdahlman](https://github.com/mdahlman)
* Unpin coverage now issue with 6.3 has been resolved [#3393](https://github.com/sqlfluff/sqlfluff/pull/3393) [@tunetheweb](https://github.com/tunetheweb)
* L045: handle `UPDATE` statements with CTEs [#3397](https://github.com/sqlfluff/sqlfluff/pull/3397) [@tunetheweb](https://github.com/tunetheweb)
* L027: Add support for `ignore_words` [#3398](https://github.com/sqlfluff/sqlfluff/pull/3398) [@dmohns](https://github.com/dmohns)
* Postgres: Allow `CREATE FUNCTION` to use Expressions in default values [#3408](https://github.com/sqlfluff/sqlfluff/pull/3408) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug in `apply_fixes()` with leading/trailing whitespace [#3407](https://github.com/sqlfluff/sqlfluff/pull/3407) [@barrywhart](https://github.com/barrywhart)
* Redshift: Correct `ALTER TABLE` syntax [#3395](https://github.com/sqlfluff/sqlfluff/pull/3395) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Parse index with column sort [#3405](https://github.com/sqlfluff/sqlfluff/pull/3405) [@greg-finley](https://github.com/greg-finley)
* MySQL: Improve SET Syntax for Variable Assignment [#3394](https://github.com/sqlfluff/sqlfluff/pull/3394) [@mdahlman](https://github.com/mdahlman)
* Handle Postgres-style type casts when using the `colon_nospaces` templating style [#3383](https://github.com/sqlfluff/sqlfluff/pull/3383) [@benji-york](https://github.com/benji-york)
* Capitalization in help message [#3385](https://github.com/sqlfluff/sqlfluff/pull/3385) [@mdahlman](https://github.com/mdahlman)
* MySQL: Update keywords [#3381](https://github.com/sqlfluff/sqlfluff/pull/3381) [@mdahlman](https://github.com/mdahlman)
* Teradata: Database statement and Set Session Database [#3382](https://github.com/sqlfluff/sqlfluff/pull/3382) [@mdahlman](https://github.com/mdahlman)


## New Contributors
* [@benji-york](https://github.com/benji-york) made their first contribution in [#3383](https://github.com/sqlfluff/sqlfluff/pull/3383)
* [@menzenski](https://github.com/menzenski) made their first contribution in [#3430](https://github.com/sqlfluff/sqlfluff/pull/3430)

## [0.13.2] - 2022-05-20

## Highlights
Major changes include:
* Fix bug causing L003 to report indentation errors for templated code - sorry we know that one's caused many of you some grief :-(
* Initial support of SOQL (Salesforce Object Query Language).
* Additional Placeholder templating options.
* Start of BigQuery procedural language support (starting simple `FOR` statements and `CREATE PROCEDURE` statements).
* New rule L065 to put set operators onto new lines.
* Many more dialect improvements and bug fixes.

## What’s Changed

* All dialects: Allow `RESPECT NULLS`/`IGNORE NULLS` in window functions [#3376](https://github.com/sqlfluff/sqlfluff/pull/3376) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: correct `RETURNS TABLE` column type [#3379](https://github.com/sqlfluff/sqlfluff/pull/3379) [@tunetheweb](https://github.com/tunetheweb)
* L065: Add rule for set operators surrounded by newlines [#3330](https://github.com/sqlfluff/sqlfluff/pull/3330) [@dmohns](https://github.com/dmohns)
* L064: Apply preferred quote-style for partially templated quoted literals [#3300](https://github.com/sqlfluff/sqlfluff/pull/3300) [@dmohns](https://github.com/dmohns)
* BigQuery: Support Stored Procedures [#3369](https://github.com/sqlfluff/sqlfluff/pull/3369) [@tunetheweb](https://github.com/tunetheweb)
* MySQL extra Boolean operators (`&&`, `||`, `!`) [#3359](https://github.com/sqlfluff/sqlfluff/pull/3359) [@mdahlman](https://github.com/mdahlman)
* Postgres and Redshift: Support `LOCK [TABLE]` [#3350](https://github.com/sqlfluff/sqlfluff/pull/3350) [@tunetheweb](https://github.com/tunetheweb)
* Placeholder updates: Allow optional braces in dollar placeholders, add `colon_nospaces`, and cast to string [#3354](https://github.com/sqlfluff/sqlfluff/pull/3354) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Basic `FOR..IN..DO...END FOR` support [#3340](https://github.com/sqlfluff/sqlfluff/pull/3340) [@tunetheweb](https://github.com/tunetheweb)
* L025: exclude `VALUES` clauses [#3358](https://github.com/sqlfluff/sqlfluff/pull/3358) [@tunetheweb](https://github.com/tunetheweb)
* GitHub Actions: Update existing PR on new runs [#3367](https://github.com/sqlfluff/sqlfluff/pull/3367) [@greg-finley](https://github.com/greg-finley)
* GitHub Actions: Copy draft release notes to CHANGELOG [#3360](https://github.com/sqlfluff/sqlfluff/pull/3360) [@greg-finley](https://github.com/greg-finley)
* GitHub Action to set version number [#3347](https://github.com/sqlfluff/sqlfluff/pull/3347) [@greg-finley](https://github.com/greg-finley)
* Postgres and Redshift: support `ALTER SCHEMA` [#3346](https://github.com/sqlfluff/sqlfluff/pull/3346) [@mdahlman](https://github.com/mdahlman)
* MySQL: better `SELECT..INTO` support [#3351](https://github.com/sqlfluff/sqlfluff/pull/3351) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: support better function calls in `CREATE TRIGGER` [#3349](https://github.com/sqlfluff/sqlfluff/pull/3349) [@tunetheweb](https://github.com/tunetheweb)
* Misc rule doc updates [#3352](https://github.com/sqlfluff/sqlfluff/pull/3352) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Move `CASE` keyword to Unreserved list [#3353](https://github.com/sqlfluff/sqlfluff/pull/3353) [@tunetheweb](https://github.com/tunetheweb)
* MySQL: Added support for multiple variables in `SET` statement. [#3328](https://github.com/sqlfluff/sqlfluff/pull/3328) [@cgkoutzigiannis](https://github.com/cgkoutzigiannis)
* SOQL: Support `date_n_literal` [#3344](https://github.com/sqlfluff/sqlfluff/pull/3344) [@greg-finley](https://github.com/greg-finley)
* Update Docs: Getting Started and Index [#3339](https://github.com/sqlfluff/sqlfluff/pull/3339) [@mdahlman](https://github.com/mdahlman)
* SOQL: Disable L026 rule [#3338](https://github.com/sqlfluff/sqlfluff/pull/3338) [@greg-finley](https://github.com/greg-finley)
* Fix critical parse error logged after L003 fix [#3337](https://github.com/sqlfluff/sqlfluff/pull/3337) [@barrywhart](https://github.com/barrywhart)
* SOQL: Disallow non-`SELECT` statements [#3329](https://github.com/sqlfluff/sqlfluff/pull/3329) [@greg-finley](https://github.com/greg-finley)
* ci: bump github actions [#3336](https://github.com/sqlfluff/sqlfluff/pull/3336) [@Fdawgs](https://github.com/Fdawgs)
* Start SOQL dialect [#3312](https://github.com/sqlfluff/sqlfluff/pull/3312) [@greg-finley](https://github.com/greg-finley)
* Hive: support `CLUSTER`, `DISTRIBUTE`, `SORT BY` [#3304](https://github.com/sqlfluff/sqlfluff/pull/3304) [@barunpuri](https://github.com/barunpuri)
* Fix typo in Configuration documentation [#3319](https://github.com/sqlfluff/sqlfluff/pull/3319) [@mdahlman](https://github.com/mdahlman)
* L011: Support `MERGE` statements [#3292](https://github.com/sqlfluff/sqlfluff/pull/3292) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Add workaround to fix false-positves of L063 [#3306](https://github.com/sqlfluff/sqlfluff/pull/3306) [@dmohns](https://github.com/dmohns)
* Snowflake: `REMOVE` statement rework [#3308](https://github.com/sqlfluff/sqlfluff/pull/3308) [@jmc-bbk](https://github.com/jmc-bbk)
* Snowflake: `PUT` statement [#3307](https://github.com/sqlfluff/sqlfluff/pull/3307) [@jmc-bbk](https://github.com/jmc-bbk)
* Snowflake: `GET` statement [#3305](https://github.com/sqlfluff/sqlfluff/pull/3305) [@jmc-bbk](https://github.com/jmc-bbk)
* Snowflake: Support `ALTER EXTERNAL TABLE` [#3302](https://github.com/sqlfluff/sqlfluff/pull/3302) [@jmc-bbk](https://github.com/jmc-bbk)
* T-SQL: Fix `PIVOT` placement [#3298](https://github.com/sqlfluff/sqlfluff/pull/3298) [@jpers36](https://github.com/jpers36)
* Cleanup role references [#3287](https://github.com/sqlfluff/sqlfluff/pull/3287) [@tunetheweb](https://github.com/tunetheweb)
* Adding Typeform and videoask into inthewild.rst [#3296](https://github.com/sqlfluff/sqlfluff/pull/3296) [@omonereo-tf](https://github.com/omonereo-tf)
* Snowflake: `LIST` statement enhancement [#3295](https://github.com/sqlfluff/sqlfluff/pull/3295) [@jmc-bbk](https://github.com/jmc-bbk)
* MySQL: Support `CREATE USER` [#3289](https://github.com/sqlfluff/sqlfluff/pull/3289) [@greg-finley](https://github.com/greg-finley)
* Snowflake: CREATE STAGE grammar enhancement for file formats [#3293](https://github.com/sqlfluff/sqlfluff/pull/3293) [@jmc-bbk](https://github.com/jmc-bbk)
* T-SQL: Complete support for `DELETE` statement [#3285](https://github.com/sqlfluff/sqlfluff/pull/3285) [@pguyot](https://github.com/pguyot)
* MySQL: Support account names [#3286](https://github.com/sqlfluff/sqlfluff/pull/3286) [@greg-finley](https://github.com/greg-finley)
* L028: In T-SQL dialect, table variables cannot be used to qualify references [#3283](https://github.com/sqlfluff/sqlfluff/pull/3283) [@barrywhart](https://github.com/barrywhart)
* L007: An operator on a line by itself is okay [#3281](https://github.com/sqlfluff/sqlfluff/pull/3281) [@barrywhart](https://github.com/barrywhart)
* L046 (spaces around Jinja tags) should check all slices in a segment [#3279](https://github.com/sqlfluff/sqlfluff/pull/3279) [@barrywhart](https://github.com/barrywhart)
* L003 bug fix: Not ignoring templated newline [#3278](https://github.com/sqlfluff/sqlfluff/pull/3278) [@barrywhart](https://github.com/barrywhart)

## New Contributors

* [@omonereo-tf](https://github.com/omonereo-tf) made their first contribution in [#3296](https://github.com/sqlfluff/sqlfluff/pull/3296)
* [@mdahlman](https://github.com/mdahlman) made their first contribution in [#3319](https://github.com/sqlfluff/sqlfluff/pull/3319)
* [@cgkoutzigiannis](https://github.com/cgkoutzigiannis) made their first contribution in [#3328](https://github.com/sqlfluff/sqlfluff/pull/3328)


## [0.13.1] - 2022-05-06

## Highlights
Major changes include:
* Addition of "rule groups" (currently `core` and `all`) to allow ease of turning on and off groups of rules.
* Addition of `db2` dialect
* PRS errors are now highlighted in red.
* Many bugs fixes and dialect improvements

## What’s Changed
* Allow optional `AS` in `MERGE` statements using `SELECT` [#3276](https://github.com/sqlfluff/sqlfluff/pull/3276) [@tunetheweb](https://github.com/tunetheweb)
* Add groups each rule is in to Rules documentation [#3272](https://github.com/sqlfluff/sqlfluff/pull/3272) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Enhanced `EXPORT DATA` statement [#3267](https://github.com/sqlfluff/sqlfluff/pull/3267) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: `CREATE TABLE` support for `COPY` and `LIKE` [#3266](https://github.com/sqlfluff/sqlfluff/pull/3266) [@tunetheweb](https://github.com/tunetheweb)
* Improve error on missing keywords [#3268](https://github.com/sqlfluff/sqlfluff/pull/3268) [@greg-finley](https://github.com/greg-finley)
* MySQL: Add `FLUSH` support [#3269](https://github.com/sqlfluff/sqlfluff/pull/3269) [@greg-finley](https://github.com/greg-finley)
* Postgres: Add `ALTER TYPE` support [#3265](https://github.com/sqlfluff/sqlfluff/pull/3265) [@greg-finley](https://github.com/greg-finley)
* Bug fix: L036 handle single-column `SELECT` with comment on same line as `SELECT` keyword [#3259](https://github.com/sqlfluff/sqlfluff/pull/3259) [@barrywhart](https://github.com/barrywhart)
* Put working example in the README [#3261](https://github.com/sqlfluff/sqlfluff/pull/3261) [@greg-finley](https://github.com/greg-finley)
* Snowflake: Add `CREATE FILE FORMAT` Support [#3104](https://github.com/sqlfluff/sqlfluff/pull/3104) [@jmc-bbk](https://github.com/jmc-bbk)
* Bug fix: Disable L059 in snowflake dialect [#3260](https://github.com/sqlfluff/sqlfluff/pull/3260) [@barrywhart](https://github.com/barrywhart)
* Remove redundant `Anything()` from `match_grammars` [#3258](https://github.com/sqlfluff/sqlfluff/pull/3258) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Add `DOMAIN` support [#3257](https://github.com/sqlfluff/sqlfluff/pull/3257) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Allow optional brackets with `EXECUTE` [#3255](https://github.com/sqlfluff/sqlfluff/pull/3255) [@pguyot](https://github.com/pguyot)
* Add rule groups and a core rules group [#3142](https://github.com/sqlfluff/sqlfluff/pull/3142) [@pwildenhain](https://github.com/pwildenhain)
* MySQL: Better `UNSIGNED` support [#3250](https://github.com/sqlfluff/sqlfluff/pull/3250) [@tunetheweb](https://github.com/tunetheweb)
* MySQL (and others): Support `DROP TEMPORARY TABLE` [#3251](https://github.com/sqlfluff/sqlfluff/pull/3251) [@tunetheweb](https://github.com/tunetheweb)
* Add Db2 dialect [#3231](https://github.com/sqlfluff/sqlfluff/pull/3231) [@ddresslerlegalplans](https://github.com/ddresslerlegalplans)
* BigQuery: Add `CREATE EXTERNAL TABLE` statement [#3241](https://github.com/sqlfluff/sqlfluff/pull/3241) [@dmohns](https://github.com/dmohns)
* SQLite: Add support for expressions in `CREATE INDEX` columns [#3240](https://github.com/sqlfluff/sqlfluff/pull/3240) [@tunetheweb](https://github.com/tunetheweb)
* Fix exception in `check_still_complete` and matching in `StartsWith` [#3236](https://github.com/sqlfluff/sqlfluff/pull/3236) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Add Support for `DROP` Statements [#3238](https://github.com/sqlfluff/sqlfluff/pull/3238) [@chrisalexeev](https://github.com/chrisalexeev)
* Allow YAML generation script to accept arguments when run through `tox` [#3233](https://github.com/sqlfluff/sqlfluff/pull/3233) [@tunetheweb](https://github.com/tunetheweb)
* Bug fix: Cleanly catch and report errors during `load_macros_from_path` [#3239](https://github.com/sqlfluff/sqlfluff/pull/3239) [@barrywhart](https://github.com/barrywhart)
* Indent procedure parameters [#3234](https://github.com/sqlfluff/sqlfluff/pull/3234) [@fdw](https://github.com/fdw)
* Enhance `apply_fixes()` to automatically fix violations of `can_start_end_non_code` [#3232](https://github.com/sqlfluff/sqlfluff/pull/3232) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Fix `for xml path` identifier [#3230](https://github.com/sqlfluff/sqlfluff/pull/3230) [@fdw](https://github.com/fdw)
* SparkSQL: Additional Delta Merge Test Cases [#3228](https://github.com/sqlfluff/sqlfluff/pull/3228) [@R7L208](https://github.com/R7L208)
* Fix bug where L018 warns inappropriately if CTE definition includes a column list [#3227](https://github.com/sqlfluff/sqlfluff/pull/3227) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Better `STRUCT` support [#3217](https://github.com/sqlfluff/sqlfluff/pull/3217) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug where L003 and L036 fixes caused a parse error [#3221](https://github.com/sqlfluff/sqlfluff/pull/3221) [@barrywhart](https://github.com/barrywhart)
* Make `IF EXISTS` work with `UNION` selects [#3218](https://github.com/sqlfluff/sqlfluff/pull/3218) [@fdw](https://github.com/fdw)
* Fix bug where the `fix_even_unparsable` setting was not being respected in `.sqlfluff` [#3220](https://github.com/sqlfluff/sqlfluff/pull/3220) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Better `DELETE` table support [#3224](https://github.com/sqlfluff/sqlfluff/pull/3224) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: `ALTER MATERIALIZED VIEW` statement [#3215](https://github.com/sqlfluff/sqlfluff/pull/3215) [@jmc-bbk](https://github.com/jmc-bbk)
* BigQuery: recognise `DATE`, `DATETIME` and `TIME` as a date parts for `EXTRACT` [#3209](https://github.com/sqlfluff/sqlfluff/pull/3209) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: enhanced `UPDATE` statement support [#3203](https://github.com/sqlfluff/sqlfluff/pull/3203) [@tunetheweb](https://github.com/tunetheweb)
* Prevent Date Constructors from being changed to double quotes by L064 [#3212](https://github.com/sqlfluff/sqlfluff/pull/3212) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Fix `DROP EXTENSION` syntax [#3213](https://github.com/sqlfluff/sqlfluff/pull/3213) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Handle `FLATTEN()` table function aliases correctly in L025, L027, L028 [#3194](https://github.com/sqlfluff/sqlfluff/pull/3194) [@barrywhart](https://github.com/barrywhart)
* Snowflake: Function `LANGUAGE SQL` [#3202](https://github.com/sqlfluff/sqlfluff/pull/3202) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Enhanced `CREATE MATERIALIZED VIEW` [#3204](https://github.com/sqlfluff/sqlfluff/pull/3204) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Support basic `FOR XML` statements [#3193](https://github.com/sqlfluff/sqlfluff/pull/3193) [@fdw](https://github.com/fdw)
* T-SQL: Fix cursor syntax [#3192](https://github.com/sqlfluff/sqlfluff/pull/3192) [@fdw](https://github.com/fdw)
* Snowflake: `REMOVE` statement enhancement [#3191](https://github.com/sqlfluff/sqlfluff/pull/3191) [@jmc-bbk](https://github.com/jmc-bbk)
* Snowflake: Moved `VIEW` to unreserved keywords [#3190](https://github.com/sqlfluff/sqlfluff/pull/3190) [@WittierDinosaur](https://github.com/WittierDinosaur)
* BigQuery: Support `EXPORT DATA` [#3177](https://github.com/sqlfluff/sqlfluff/pull/3177) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Fix exception when using variable names in `FROM` clause [#3175](https://github.com/sqlfluff/sqlfluff/pull/3175) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug where `encoding` setting in .sqlfluff file was not being respected [#3170](https://github.com/sqlfluff/sqlfluff/pull/3170) [@barrywhart](https://github.com/barrywhart)
* Highlight `PRS` errors in red [#3168](https://github.com/sqlfluff/sqlfluff/pull/3168) [@OTooleMichael](https://github.com/OTooleMichael)
* Remove unnecessary `StartsWith` and make `terminator` mandatory when using it [#3165](https://github.com/sqlfluff/sqlfluff/pull/3165) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Support Composite Types [#3167](https://github.com/sqlfluff/sqlfluff/pull/3167) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Support opening, closing, deallocating and fetching cursors [#3166](https://github.com/sqlfluff/sqlfluff/pull/3166) [@fdw](https://github.com/fdw)
* T-SQL: Add declaration of cursors [#3164](https://github.com/sqlfluff/sqlfluff/pull/3164) [@fdw](https://github.com/fdw)
* Missed #3151 from CHANGELOG [#3163](https://github.com/sqlfluff/sqlfluff/pull/3163) [@tunetheweb](https://github.com/tunetheweb)
* Bug fix: L028 sometimes makes incorrect fix when there are subqueries [#3156](https://github.com/sqlfluff/sqlfluff/pull/3156) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Support `OUTPUT INTO` [#3162](https://github.com/sqlfluff/sqlfluff/pull/3162) [@fdw](https://github.com/fdw)
* T-SQL: Add `CREATE TYPE` statement [#3154](https://github.com/sqlfluff/sqlfluff/pull/3154) [@fdw](https://github.com/fdw)
* Hive: Support`TABLESAMPLE` [#3159](https://github.com/sqlfluff/sqlfluff/pull/3159) [@barunpuri](https://github.com/barunpuri)
* Hive: Support back quoted identifier and literal [#3158](https://github.com/sqlfluff/sqlfluff/pull/3158) [@barunpuri](https://github.com/barunpuri)
* T-SQL: Add table hints to `INSERT` and `DELETE` [#3155](https://github.com/sqlfluff/sqlfluff/pull/3155) [@fdw](https://github.com/fdw)


## New Contributors
* [@ddresslerlegalplans](https://github.com/ddresslerlegalplans) made their first contribution in [#3231](https://github.com/sqlfluff/sqlfluff/pull/3231)
* [@greg-finley](https://github.com/greg-finley) made their first contribution in [#3261](https://github.com/sqlfluff/sqlfluff/pull/3261)


## [0.13.0] - 2022-04-22

## Highlights
Major changes include:
* New Rule (L064) for preferred quotes for quoted literals
* Rule speed improvements and fixing performance regression from 0.12.0
* Add configuration option to disallow hanging indents in L003
* Add `ignore_words_regex` configuration option for rules
* New GitHub Annotations option
* Many bug fixes and dialect improvements

## What’s Changed
* Redshift: Fix CREATE TABLE column constraints and COPY [#3151](https://github.com/sqlfluff/sqlfluff/pull/3151) [@tunetheweb](https://github.com/tunetheweb)
* New Rule L064: Consistent usage of preferred quotes for quoted literals [#3118](https://github.com/sqlfluff/sqlfluff/pull/3118) [@dmohns](https://github.com/dmohns)
* L025 bug fix: stop incorrectly flagging on nested inner joins [#3145](https://github.com/sqlfluff/sqlfluff/pull/3145) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Add labels, as well as `GRANT`/`DENY`/`REVOKE` [#3149](https://github.com/sqlfluff/sqlfluff/pull/3149) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: allow bracketless `VALUES` in `FROM` clauses [#3141](https://github.com/sqlfluff/sqlfluff/pull/3141) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Support `TRY_CONVERT` [#3143](https://github.com/sqlfluff/sqlfluff/pull/3143) [@fdw](https://github.com/fdw)
* T-SQL: Support `NVARCHAR(MAX)` [#3130](https://github.com/sqlfluff/sqlfluff/pull/3130) [@fdw](https://github.com/fdw)
* Allow column-less `INSERT INTO` with bracketed `SELECT` in ANSI and BigQuery [#3139](https://github.com/sqlfluff/sqlfluff/pull/3139) [@tunetheweb](https://github.com/tunetheweb)
* Hive: Support dynamic partition insert [#3126](https://github.com/sqlfluff/sqlfluff/pull/3126) [@barunpuri](https://github.com/barunpuri)
* T-SQL - `ALTER TABLE` - add support for `WITH CHECK ADD CONSTRAINT` and `CHECK CONSTRAINT` [#3132](https://github.com/sqlfluff/sqlfluff/pull/3132) [@nevado](https://github.com/nevado)
* TSQL: Support names for transactions [#3129](https://github.com/sqlfluff/sqlfluff/pull/3129) [@fdw](https://github.com/fdw)
* Snowflake: `StartsWith()` in `FromExpressionElementSegment` caused performance issues for large queries [#3128](https://github.com/sqlfluff/sqlfluff/pull/3128) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix parsing of Compound Statements [#3121](https://github.com/sqlfluff/sqlfluff/pull/3121) [@jonyscathe](https://github.com/jonyscathe)
* SparkSQL: Update to support all valid Literal Types [#3102](https://github.com/sqlfluff/sqlfluff/pull/3102) [@R7L208](https://github.com/R7L208)
* TSQL: Exclude non-function-name keywords from function names [#3112](https://github.com/sqlfluff/sqlfluff/pull/3112) [@jpers36](https://github.com/jpers36)
* ANSI `AT TIME ZONE` parsing improvements [#3115](https://github.com/sqlfluff/sqlfluff/pull/3115) [@tunetheweb](https://github.com/tunetheweb)
* When fixing a file, preserve the input file's permissions [#3114](https://github.com/sqlfluff/sqlfluff/pull/3114) [@barrywhart](https://github.com/barrywhart)
* Bug: L058 (flatten nested `CASE`) triggers incorrectly (the `ELSE` contains additional code) [#3113](https://github.com/sqlfluff/sqlfluff/pull/3113) [@barrywhart](https://github.com/barrywhart)
* Bug fix: Handle "lint" human-format file output correctly [#3109](https://github.com/sqlfluff/sqlfluff/pull/3109) [@barrywhart](https://github.com/barrywhart)
* L003: Add configuration option to disallow hanging indents [#3063](https://github.com/sqlfluff/sqlfluff/pull/3063) [@dmohns](https://github.com/dmohns)
* Add native Github-actions output [#3107](https://github.com/sqlfluff/sqlfluff/pull/3107) [@dmohns](https://github.com/dmohns)
* Improved signed literal parsing [#3108](https://github.com/sqlfluff/sqlfluff/pull/3108) [@tunetheweb](https://github.com/tunetheweb)
* Don't allow fixes to span template blocks [#3105](https://github.com/sqlfluff/sqlfluff/pull/3105) [@barrywhart](https://github.com/barrywhart)
* Add `ignore_words_regex` configuration option [#3098](https://github.com/sqlfluff/sqlfluff/pull/3098) [@dmohns](https://github.com/dmohns)
* Redshift: Better `AT TIME ZONE` support [#3087](https://github.com/sqlfluff/sqlfluff/pull/3087) [@tunetheweb](https://github.com/tunetheweb)
* Fix In The Wild typo [#3100](https://github.com/sqlfluff/sqlfluff/pull/3100) [@sivaraam](https://github.com/sivaraam)
* Snowflake: Add Create Storage Integration grammar. [#3075](https://github.com/sqlfluff/sqlfluff/pull/3075) [@jmc-bbk](https://github.com/jmc-bbk)
* ANSI: Allow `indented_using_on` in `MERGE` statements `ON` [#3096](https://github.com/sqlfluff/sqlfluff/pull/3096) [@dmohns](https://github.com/dmohns)
* Postgres: Support `COLLATE` in more clauses [#3095](https://github.com/sqlfluff/sqlfluff/pull/3095) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Support `NORMALIZE` function [#3086](https://github.com/sqlfluff/sqlfluff/pull/3086) [@tunetheweb](https://github.com/tunetheweb)
* ANSI (and other dialects): Add `DROP FUNCTION` support [#3082](https://github.com/sqlfluff/sqlfluff/pull/3082) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Support `DROP EXTENSION` [#3083](https://github.com/sqlfluff/sqlfluff/pull/3083) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Fix bug in Describe Statement [#3076](https://github.com/sqlfluff/sqlfluff/pull/3076) [@jmc-bbk](https://github.com/jmc-bbk)
* Update individual rules to take advantage of core rule processing changes [#3041](https://github.com/sqlfluff/sqlfluff/pull/3041) [@barrywhart](https://github.com/barrywhart)
* L003 forgives non misbalanced Jinja tags [#3065](https://github.com/sqlfluff/sqlfluff/pull/3065) [@OTooleMichael](https://github.com/OTooleMichael)
* Fix tsql dialect `EXEC = @Variable StoredProc` Failed Parsing Bug (#3070) [#3077](https://github.com/sqlfluff/sqlfluff/pull/3077) [@MartynJones87](https://github.com/MartynJones87)
* Snowflake Dialect: Add External Function DDL [#3071](https://github.com/sqlfluff/sqlfluff/pull/3071) [@chrisalexeev](https://github.com/chrisalexeev)
* SparkSQL: Support for Delta `UPDATE` statement syntax [#3073](https://github.com/sqlfluff/sqlfluff/pull/3073) [@R7L208](https://github.com/R7L208)
* SparkSQL: Test cases for Delta `DELETE FROM` syntax [#3072](https://github.com/sqlfluff/sqlfluff/pull/3072) [@R7L208](https://github.com/R7L208)
* Postgres: Support quoted `LANGUAGE` params [#3068](https://github.com/sqlfluff/sqlfluff/pull/3068) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug handling Jinja set with multiple vars, e.g.: `{% set a, b = 1, 2 %}` [#3066](https://github.com/sqlfluff/sqlfluff/pull/3066) [@barrywhart](https://github.com/barrywhart)
* L007 should ignore templated newlines [#3067](https://github.com/sqlfluff/sqlfluff/pull/3067) [@barrywhart](https://github.com/barrywhart)
* Allow aliases to pass L028 [#3062](https://github.com/sqlfluff/sqlfluff/pull/3062) [@tunetheweb](https://github.com/tunetheweb)
* Refactor core rule processing for flexibility and speed [#3061](https://github.com/sqlfluff/sqlfluff/pull/3061) [@barrywhart](https://github.com/barrywhart)
* Add editorconfig and precommit for SQL and YML files [#3058](https://github.com/sqlfluff/sqlfluff/pull/3058) [@tunetheweb](https://github.com/tunetheweb)
* Rule L003 performance: Cache the line number and last newline position [#3060](https://github.com/sqlfluff/sqlfluff/pull/3060) [@barrywhart](https://github.com/barrywhart)
* Fixed documentation for `sql_file_exts` example [#3059](https://github.com/sqlfluff/sqlfluff/pull/3059) [@KulykDmytro](https://github.com/KulykDmytro)
* BigQuery: Support `SAFE` functions [#3048](https://github.com/sqlfluff/sqlfluff/pull/3048) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Fix `UNNEST` for L025 [#3054](https://github.com/sqlfluff/sqlfluff/pull/3054) [@tunetheweb](https://github.com/tunetheweb)
* Exasol: `CREATE/DROP/ALTER USER/ROLE` clean up for consistency [#3045](https://github.com/sqlfluff/sqlfluff/pull/3045) [@tunetheweb](https://github.com/tunetheweb)
* Postgres add `ALTER ROLE`/`ALTER USER` support [#3043](https://github.com/sqlfluff/sqlfluff/pull/3043) [@mrf](https://github.com/mrf)
* Add CarePay to SQLFluff in the wild [#3038](https://github.com/sqlfluff/sqlfluff/pull/3038) [@pvonglehn](https://github.com/pvonglehn)
* Postgres: Add `ON CONFLICT` Grammar [#3027](https://github.com/sqlfluff/sqlfluff/pull/3027) [@jmc-bbk](https://github.com/jmc-bbk)
* Add dialect to Docker test [#3033](https://github.com/sqlfluff/sqlfluff/pull/3033) [@tunetheweb](https://github.com/tunetheweb)

## New Contributors
* [@chrisalexeev](https://github.com/chrisalexeev) made their first contribution in [#3071](https://github.com/sqlfluff/sqlfluff/pull/3071)
* [@MartynJones87](https://github.com/MartynJones87) made their first contribution in [#3077](https://github.com/sqlfluff/sqlfluff/pull/3077)
* [@sivaraam](https://github.com/sivaraam) made their first contribution in [#3100](https://github.com/sqlfluff/sqlfluff/pull/3100)
* [@jonyscathe](https://github.com/jonyscathe) made their first contribution in [#3121](https://github.com/sqlfluff/sqlfluff/pull/3121)
* [@barunpuri](https://github.com/barunpuri) made their first contribution in [#3126](https://github.com/sqlfluff/sqlfluff/pull/3126)


## [0.12.0] - 2022-04-07

## Highlights
Major changes include:
* Dialect is now mandatory, either in command line, or in config **BREAKING CHANGE**
* Rename `spark3` dialect to `sparksql` **BREAKING CHANGE**
* L027 now checks tables references exist **BREAKING CHANGE**
* New rule L063 to allow Datatypes to have a different capitalisation policy from L010. **BREAKING CHANGE**
* Refactor and performance improvements of Delimited and L003
* Many dialect improvements and fixes

## What’s Changed
* MySQL: Allow `JOIN`s in `UPDATE` expressions [#3031](https://github.com/sqlfluff/sqlfluff/pull/3031) [@zapion](https://github.com/zapion)
* Fix bug in patch generation for segments made of templated + literal fixes [#3030](https://github.com/sqlfluff/sqlfluff/pull/3030) [@barrywhart](https://github.com/barrywhart)
* Formatters code cleanup [#3029](https://github.com/sqlfluff/sqlfluff/pull/3029) [@barrywhart](https://github.com/barrywhart)
* Postgres better `CREATE USER`/`CREATE ROLE` support [#3016](https://github.com/sqlfluff/sqlfluff/pull/3016) [@mrf](https://github.com/mrf)
* SparkSQL: Add `MERGE` syntax [#3025](https://github.com/sqlfluff/sqlfluff/pull/3025) [@PhilippLange](https://github.com/PhilippLange)
* Remove Delimited workarounds [#3024](https://github.com/sqlfluff/sqlfluff/pull/3024) [@tunetheweb](https://github.com/tunetheweb)
* Add `exclude` option for `Ref` grammar [#3028](https://github.com/sqlfluff/sqlfluff/pull/3028) [@tunetheweb](https://github.com/tunetheweb)
* SparkSQL: Adding support for Delta Lake table schema updates [#3013](https://github.com/sqlfluff/sqlfluff/pull/3013) [@R7L208](https://github.com/R7L208)
* L027: Check table aliases exists [#2998](https://github.com/sqlfluff/sqlfluff/pull/2998) [@dmohns](https://github.com/dmohns)
* Snowflake: Added support for `REMOVE` statements [#3026](https://github.com/sqlfluff/sqlfluff/pull/3026) [@WittierDinosaur](https://github.com/WittierDinosaur)
* BigQuery: Support `WEEK` function with days of weeks [#3021](https://github.com/sqlfluff/sqlfluff/pull/3021) [@tunetheweb](https://github.com/tunetheweb)
* Sparksql quoted identifier in `STRUCT` [#3023](https://github.com/sqlfluff/sqlfluff/pull/3023) [@PhilippLange](https://github.com/PhilippLange)
* Force user to specify a dialect [#2995](https://github.com/sqlfluff/sqlfluff/pull/2995) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Parse `CREATE TABLE` with trailing comma [#3018](https://github.com/sqlfluff/sqlfluff/pull/3018) [@dmohns](https://github.com/dmohns)
* Snowflake: Add `IS (NOT) DISTINCT FROM` test cases [#3014](https://github.com/sqlfluff/sqlfluff/pull/3014) [@kd2718](https://github.com/kd2718)
* BigQuery: Add support for column `OPTIONS` in `STRUCT` definitions [#3017](https://github.com/sqlfluff/sqlfluff/pull/3017) [@dmohns](https://github.com/dmohns)
* PostgreSQL: added support for `CREATE ROLE` and `DROP ROLE` statements [#3010](https://github.com/sqlfluff/sqlfluff/pull/3010) [@dnim](https://github.com/dnim)
* Separate slow CI job to it's own workflow [#3012](https://github.com/sqlfluff/sqlfluff/pull/3012) [@tunetheweb](https://github.com/tunetheweb)
* SparkSQL: Test cases for Delta Variation of Writing a table [#3009](https://github.com/sqlfluff/sqlfluff/pull/3009) [@R7L208](https://github.com/R7L208)
* Snowflake: Added support for `CLUSTER BY` and other `CREATE TABLE` improvements [#3008](https://github.com/sqlfluff/sqlfluff/pull/3008) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Support `TRIM` function parameters [#3007](https://github.com/sqlfluff/sqlfluff/pull/3007) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Support `AT TIME ZONE` in `EXTRACT` [#3004](https://github.com/sqlfluff/sqlfluff/pull/3004) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Move some keywords to unreserved [#3002](https://github.com/sqlfluff/sqlfluff/pull/3002) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Allow quoted variable names in `DECLARE` [#3006](https://github.com/sqlfluff/sqlfluff/pull/3006) [@dmohns](https://github.com/dmohns)
* T-SQL: allow optional `AS` keyword in parameters def [#3001](https://github.com/sqlfluff/sqlfluff/pull/3001) [@pguyot](https://github.com/pguyot)
* T-SQL: add support for `RETURNS @var TABLE` syntax [#3000](https://github.com/sqlfluff/sqlfluff/pull/3000) [@pguyot](https://github.com/pguyot)
* T-SQL: add support for parenthesized nested joins [#2993](https://github.com/sqlfluff/sqlfluff/pull/2993) [@pguyot](https://github.com/pguyot)
* dbt: Read builtins from code [#2988](https://github.com/sqlfluff/sqlfluff/pull/2988) [@dmohns](https://github.com/dmohns)
* T-SQL: fix table type in `DECLARE` statements [#2999](https://github.com/sqlfluff/sqlfluff/pull/2999) [@pguyot](https://github.com/pguyot)
* T-SQL: allow leading `GO` [#2997](https://github.com/sqlfluff/sqlfluff/pull/2997) [@pguyot](https://github.com/pguyot)
* T-SQL: add support for assignment operators [#2996](https://github.com/sqlfluff/sqlfluff/pull/2996) [@pguyot](https://github.com/pguyot)
* BigQuery: Add more `MERGE` statement variants [#2989](https://github.com/sqlfluff/sqlfluff/pull/2989) [@dmohns](https://github.com/dmohns)
* L041: Fix bug when there is a newline after the select clause modifier [#2981](https://github.com/sqlfluff/sqlfluff/pull/2981) [@jmc-bbk](https://github.com/jmc-bbk)
* Rule L045 doesn't recognise CTE usage in a subquery when rule L042 is enabled [#2980](https://github.com/sqlfluff/sqlfluff/pull/2980) [@barrywhart](https://github.com/barrywhart)
* dbt: Make `is_incremental()` defaults consistent [#2985](https://github.com/sqlfluff/sqlfluff/pull/2985) [@dmohns](https://github.com/dmohns)
* Rename Grammars for consistency [#2986](https://github.com/sqlfluff/sqlfluff/pull/2986) [@tunetheweb](https://github.com/tunetheweb)
* Added support for MySQL `UPDATE` Statements [#2982](https://github.com/sqlfluff/sqlfluff/pull/2982) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Redshift: Added `CREATE EXTERNAL SCHEMA`, bugfix in `PARTITION BY` [#2983](https://github.com/sqlfluff/sqlfluff/pull/2983) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Added `ALTER INDEX` and `REINDEX` to Postgres, Some Grammar Cleaning [#2979](https://github.com/sqlfluff/sqlfluff/pull/2979) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL grammar deduplication [#2967](https://github.com/sqlfluff/sqlfluff/pull/2967) [@tunetheweb](https://github.com/tunetheweb)
* L003 Refactor [#2884](https://github.com/sqlfluff/sqlfluff/pull/2884) [@OTooleMichael](https://github.com/OTooleMichael)
* Delimited Refactor [#2831](https://github.com/sqlfluff/sqlfluff/pull/2831) [@WittierDinosaur](https://github.com/WittierDinosaur)
* SparkSQL: Support for querying snapshots when reading data with Delta Lake [#2972](https://github.com/sqlfluff/sqlfluff/pull/2972) [@R7L208](https://github.com/R7L208)
* Fix bug in L063 for BigQuery `STRUCT` params [#2975](https://github.com/sqlfluff/sqlfluff/pull/2975) [@tunetheweb](https://github.com/tunetheweb)
* Fix assertion error in dbt templater when file ends with whitespace strip (`-%}`) [#2976](https://github.com/sqlfluff/sqlfluff/pull/2976) [@barrywhart](https://github.com/barrywhart)
* Pass dbt vars to dbt [#2923](https://github.com/sqlfluff/sqlfluff/pull/2923) [@tcholewik](https://github.com/tcholewik)
* BigQuery: Add support for column `OPTIONS` [#2973](https://github.com/sqlfluff/sqlfluff/pull/2973) [@dmohns](https://github.com/dmohns)
* BigQuery: Allow expressions in `OPTIONS` clauses [#2971](https://github.com/sqlfluff/sqlfluff/pull/2971) [@dmohns](https://github.com/dmohns)
* Bump black to 22.3.0 on pre-commit [#2969](https://github.com/sqlfluff/sqlfluff/pull/2969) [@pguyot](https://github.com/pguyot)
* T-SQL: Redefine `DatatypeIdentifierSegment` [#2959](https://github.com/sqlfluff/sqlfluff/pull/2959) [@alanmcruickshank](https://github.com/alanmcruickshank)
* T-SQL: Add support for `WAITFOR` statement [#2968](https://github.com/sqlfluff/sqlfluff/pull/2968) [@pguyot](https://github.com/pguyot)
* T-SQL: Add `WHILE` statement support [#2966](https://github.com/sqlfluff/sqlfluff/pull/2966) [@pguyot](https://github.com/pguyot)
* T-SQL: `INTO` is optional within `INSERT` statement [#2963](https://github.com/sqlfluff/sqlfluff/pull/2963) [@pguyot](https://github.com/pguyot)
* Add basic `IS (NOT) DISTINCT FROM` support in most dialects [#2962](https://github.com/sqlfluff/sqlfluff/pull/2962) [@tunetheweb](https://github.com/tunetheweb)
* SparkSQL: Create Table Delta Lake Variant [#2954](https://github.com/sqlfluff/sqlfluff/pull/2954) [@R7L208](https://github.com/R7L208)
* T-SQL: Add support for `CREATE`/`DROP`/`DISABLE` `TRIGGER` [#2957](https://github.com/sqlfluff/sqlfluff/pull/2957) [@tunetheweb](https://github.com/tunetheweb)
* Bug: L042 modifies parse tree even during "lint" [#2955](https://github.com/sqlfluff/sqlfluff/pull/2955) [@barrywhart](https://github.com/barrywhart)
* Allow multiple post function clauses in Postgres and Redshift [#2952](https://github.com/sqlfluff/sqlfluff/pull/2952) [@aviv](https://github.com/aviv)
* Fix bug in L022 for trailing comments in CTE [#2946](https://github.com/sqlfluff/sqlfluff/pull/2946) [@tunetheweb](https://github.com/tunetheweb)
* More dialect checking, fixes, inheritance cleanup [#2942](https://github.com/sqlfluff/sqlfluff/pull/2942) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Support `OUTPUT` Params and `GOTO` Statements [#2949](https://github.com/sqlfluff/sqlfluff/pull/2949) [@tunetheweb](https://github.com/tunetheweb)
* BREAKING CHANGE: change existing dialect name from `spark3` to `sparksql` [#2924](https://github.com/sqlfluff/sqlfluff/pull/2924) [@R7L208](https://github.com/R7L208)
* Add Symend to SQLFluff In The Wild [#2940](https://github.com/sqlfluff/sqlfluff/pull/2940) [@HeyZiko](https://github.com/HeyZiko)
* Simplify segment creation and inheritance in dialects [#2933](https://github.com/sqlfluff/sqlfluff/pull/2933) [@barrywhart](https://github.com/barrywhart)
* Snowflake: Add `ALTER STREAM` support [#2939](https://github.com/sqlfluff/sqlfluff/pull/2939) [@HeyZiko](https://github.com/HeyZiko)
* T-SQL: Handle multiple nested joins [#2938](https://github.com/sqlfluff/sqlfluff/pull/2938) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Add `CREATE STREAM` support [#2936](https://github.com/sqlfluff/sqlfluff/pull/2936) [@HeyZiko](https://github.com/HeyZiko)
* T-SQL: Support nested joins [#2928](https://github.com/sqlfluff/sqlfluff/pull/2928) [@tunetheweb](https://github.com/tunetheweb)
* To replace base dialect segment class, must subclass or provide same stuff [#2930](https://github.com/sqlfluff/sqlfluff/pull/2930) [@barrywhart](https://github.com/barrywhart)
* Add new rule L063 to allow separate capitalisation policy for Datatypes [#2931](https://github.com/sqlfluff/sqlfluff/pull/2931) [@tunetheweb](https://github.com/tunetheweb)
* Adds support for column definitions in table alias expressions [#2932](https://github.com/sqlfluff/sqlfluff/pull/2932) [@derickl](https://github.com/derickl)
* BigQuery: support numeric aliases in `UNPIVOT` clauses [#2925](https://github.com/sqlfluff/sqlfluff/pull/2925) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Supported nested `MERGE` statements [#2926](https://github.com/sqlfluff/sqlfluff/pull/2926) [@tunetheweb](https://github.com/tunetheweb)

## New Contributors
* [@HeyZiko](https://github.com/HeyZiko) made their first contribution in [#2936](https://github.com/sqlfluff/sqlfluff/pull/2936)
* [@aviv](https://github.com/aviv) made their first contribution in [#2952](https://github.com/sqlfluff/sqlfluff/pull/2952)
* [@pguyot](https://github.com/pguyot) made their first contribution in [#2963](https://github.com/sqlfluff/sqlfluff/pull/2963)
* [@dmohns](https://github.com/dmohns) made their first contribution in [#2971](https://github.com/sqlfluff/sqlfluff/pull/2971)
* [@tcholewik](https://github.com/tcholewik) made their first contribution in [#2923](https://github.com/sqlfluff/sqlfluff/pull/2923)
* [@jmc-bbk](https://github.com/jmc-bbk) made their first contribution in [#2981](https://github.com/sqlfluff/sqlfluff/pull/2981)
* [@dnim](https://github.com/dnim) made their first contribution in [#3010](https://github.com/sqlfluff/sqlfluff/pull/3010)
* [@kd2718](https://github.com/kd2718) made their first contribution in [#3014](https://github.com/sqlfluff/sqlfluff/pull/3014)
* [@mrf](https://github.com/mrf) made their first contribution in [#3016](https://github.com/sqlfluff/sqlfluff/pull/3016)
* [@zapion](https://github.com/zapion) made their first contribution in [#3031](https://github.com/sqlfluff/sqlfluff/pull/3031)

## [0.11.2] - 2022-03-25

## What’s Changed
* Added Support For Snowflake Inline Comments [#2919](https://github.com/sqlfluff/sqlfluff/pull/2919) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Spark3: Fix bug which did not allow multiple joins [#2917](https://github.com/sqlfluff/sqlfluff/pull/2917) [@tunetheweb](https://github.com/tunetheweb)
* Added Snowflake Alter View Support [#2915](https://github.com/sqlfluff/sqlfluff/pull/2915) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Adjust L010 to ignore nulls and booleans covered by L040 [#2913](https://github.com/sqlfluff/sqlfluff/pull/2913) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug where L043 corrupts SQL [#2908](https://github.com/sqlfluff/sqlfluff/pull/2908) [@barrywhart](https://github.com/barrywhart)
* Jinja: Add support for Block Assignments [#2907](https://github.com/sqlfluff/sqlfluff/pull/2907) [@barrywhart](https://github.com/barrywhart)
* L042 fix fails with missing function `get_identifier()` on Postgres, Redshift dialects [#2899](https://github.com/sqlfluff/sqlfluff/pull/2899) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Better Set Operators support [#2901](https://github.com/sqlfluff/sqlfluff/pull/2901) [@tunetheweb](https://github.com/tunetheweb)
* Hive: support for complex types in `cast` `rowtype` definition [#2896](https://github.com/sqlfluff/sqlfluff/pull/2896) [@KulykDmytro](https://github.com/KulykDmytro)
* Hive: added `json` type support [#2894](https://github.com/sqlfluff/sqlfluff/pull/2894) [@KulykDmytro](https://github.com/KulykDmytro)
* Hive: fix incorrect L027 error for rowtype attribute name [#2893](https://github.com/sqlfluff/sqlfluff/pull/2893) [@KulykDmytro](https://github.com/KulykDmytro)
* Hive: Add `ARRAY` support [#2891](https://github.com/sqlfluff/sqlfluff/pull/2891) [@tunetheweb](https://github.com/tunetheweb)
* Implemented `PIVOT`/`UNPIVOT` Redshift + Fixed Snowflake Bug + Standardized `PIVOT`/`UNPIVOT` Parsing [#2888](https://github.com/sqlfluff/sqlfluff/pull/2888) [@PLBMR](https://github.com/PLBMR)
* Fix AssertionError in dbt templater when file ends with multiple newlines [#2887](https://github.com/sqlfluff/sqlfluff/pull/2887) [@barrywhart](https://github.com/barrywhart)
* Hive: Row typecasting in `cast` function [#2889](https://github.com/sqlfluff/sqlfluff/pull/2889) [@KulykDmytro](https://github.com/KulykDmytro)
* dbt templater should gracefully skip macro files [#2886](https://github.com/sqlfluff/sqlfluff/pull/2886) [@barrywhart](https://github.com/barrywhart)
* Disable L031 on BigQuery due to complex backtick / project name behavior [#2882](https://github.com/sqlfluff/sqlfluff/pull/2882) [@barrywhart](https://github.com/barrywhart)
* Documentation: Update dbt templater docs with more detail about pros and cons [#2885](https://github.com/sqlfluff/sqlfluff/pull/2885) [@barrywhart](https://github.com/barrywhart)
* BigQuery: Better `STRUCT` Array Support [#2881](https://github.com/sqlfluff/sqlfluff/pull/2881) [@tunetheweb](https://github.com/tunetheweb)
* L042: Detect violations when column is templated [#2879](https://github.com/sqlfluff/sqlfluff/pull/2879) [@barrywhart](https://github.com/barrywhart)
* Improve parsing of `BETWEEN` statements [#2878](https://github.com/sqlfluff/sqlfluff/pull/2878) [@MarcAntoineSchmidtQC](https://github.com/MarcAntoineSchmidtQC)

## [0.11.1] - 2022-03-17

## Highlights
Major changes include:
* A number of changes to `fix` code to make these more robust
* Improvements to templating blocks
* `generate_parse_fixture_yml` options to allow quicker, partial regeneration of YML files
* Numerous rule fixes including adding auto fix to L042
* Numerous grammar changes

## What’s Changed
* Spark3: Support for `SHOW` statements [#2864](https://github.com/sqlfluff/sqlfluff/pull/2864) [@R7L208](https://github.com/R7L208)
* Add Markerr to list of organizations using SQLFluff in the wild  [#2874](https://github.com/sqlfluff/sqlfluff/pull/2874) [@kdw2126](https://github.com/kdw2126)
* Refactor JinjaTracer: Split into two classes, break up `_slice_template()` function [#2870](https://github.com/sqlfluff/sqlfluff/pull/2870) [@barrywhart](https://github.com/barrywhart)
* BigQuery: support Parameterized Numeric Literals [#2872](https://github.com/sqlfluff/sqlfluff/pull/2872) [@tunetheweb](https://github.com/tunetheweb)
* L042 autofix [#2860](https://github.com/sqlfluff/sqlfluff/pull/2860) [@OTooleMichael](https://github.com/OTooleMichael)
* Redshift: transaction statement [#2852](https://github.com/sqlfluff/sqlfluff/pull/2852) [@rpr-ableton](https://github.com/rpr-ableton)
* JinjaTracer fix for endif/endfor inside "set" or "macro" blocks [#2868](https://github.com/sqlfluff/sqlfluff/pull/2868) [@barrywhart](https://github.com/barrywhart)
* L009: Handle adding newline after `{% endif %}` at end of file [#2862](https://github.com/sqlfluff/sqlfluff/pull/2862) [@barrywhart](https://github.com/barrywhart)
* Redshift: Add support for `AT TIME ZONE` [#2863](https://github.com/sqlfluff/sqlfluff/pull/2863) [@tunetheweb](https://github.com/tunetheweb)
* L032 bug fix and fix improvement [#2859](https://github.com/sqlfluff/sqlfluff/pull/2859) [@OTooleMichael](https://github.com/OTooleMichael)
* Refactor JinjaTracer; store lex output as individual strings where possible [#2856](https://github.com/sqlfluff/sqlfluff/pull/2856) [@barrywhart](https://github.com/barrywhart)
* Add ability to regenerate subsets of fixture YAMLs (by dialect, or new only) [#2850](https://github.com/sqlfluff/sqlfluff/pull/2850) [@OTooleMichael](https://github.com/OTooleMichael)
* Fix bug with Jinja and dbt `{% set %}` blocks [#2849](https://github.com/sqlfluff/sqlfluff/pull/2849) [@barrywhart](https://github.com/barrywhart)
* Bug fix: `ValueError: Position Not Found for lint/parse/fix` in JinjaTracer [#2846](https://github.com/sqlfluff/sqlfluff/pull/2846) [@barrywhart](https://github.com/barrywhart)
* Reduce unnecessary setting run ci [#2847](https://github.com/sqlfluff/sqlfluff/pull/2847) [@zhongjiajie](https://github.com/zhongjiajie)
* Spark3: statements to `SET` and `RESET` spark runtime configurations [#2839](https://github.com/sqlfluff/sqlfluff/pull/2839) [@R7L208](https://github.com/R7L208)
* BigQuery - prevent L006 flagging hyphenated table references [#2842](https://github.com/sqlfluff/sqlfluff/pull/2842) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL fix `CONVERT` function definition [#2843](https://github.com/sqlfluff/sqlfluff/pull/2843) [@tunetheweb](https://github.com/tunetheweb)
* Change rule test script from bash to python [#2840](https://github.com/sqlfluff/sqlfluff/pull/2840) [@OTooleMichael](https://github.com/OTooleMichael)
* Spark3: Support `DESCRIBE` statement [#2837](https://github.com/sqlfluff/sqlfluff/pull/2837) [@R7L208](https://github.com/R7L208)
* Spark3: Refactor `REFRESH` statements into one class [#2838](https://github.com/sqlfluff/sqlfluff/pull/2838) [@R7L208](https://github.com/R7L208)
* Prevent rules incorrectly returning conflicting fixes to same position [#2830](https://github.com/sqlfluff/sqlfluff/pull/2830) [@barrywhart](https://github.com/barrywhart)
* Redshift and BigQuery: Update dateparts values and functions  [#2829](https://github.com/sqlfluff/sqlfluff/pull/2829) [@rpr-ableton](https://github.com/rpr-ableton)
* MySQL add `NOW` support [#2825](https://github.com/sqlfluff/sqlfluff/pull/2825) [@tunetheweb](https://github.com/tunetheweb)
* MySQL `DELETE FROM` support [#2823](https://github.com/sqlfluff/sqlfluff/pull/2823) [@tunetheweb](https://github.com/tunetheweb)
* Rule L059 bug with `IF` [#2824](https://github.com/sqlfluff/sqlfluff/pull/2824) [@tunetheweb](https://github.com/tunetheweb)
* Prevent exceptions when running `fix` on dialect fixtures [#2818](https://github.com/sqlfluff/sqlfluff/pull/2818) [@tunetheweb](https://github.com/tunetheweb)
* Spark3: Support to handle `CACHE` AND `UNCACHE` auxiliary statements [#2814](https://github.com/sqlfluff/sqlfluff/pull/2814) [@R7L208](https://github.com/R7L208)
* Fix L036 error on `CREATE VIEW AS SELECT` [#2816](https://github.com/sqlfluff/sqlfluff/pull/2816) [@tunetheweb](https://github.com/tunetheweb)
* Fixes for the new post-fix parse check [#2813](https://github.com/sqlfluff/sqlfluff/pull/2813) [@barrywhart](https://github.com/barrywhart)
* Add initial `MERGE` syntax to most dialects [#2807](https://github.com/sqlfluff/sqlfluff/pull/2807) [@PhilippLange](https://github.com/PhilippLange)
* Automated tests should fail if a lint fix introduces a parse error [#2809](https://github.com/sqlfluff/sqlfluff/pull/2809) [@barrywhart](https://github.com/barrywhart)

## New Contributors
* [@kdw2126](https://github.com/kdw2126) made their first contribution in [#2874](https://github.com/sqlfluff/sqlfluff/pull/2874)

## [0.11.0] - 2022-03-07

## Highlights
Major changes include:
* Changes rule L030 to use `extended_capitalisation_policy` to support PascalCase **BREAKING CHANGE**
* Fixes dbt error on ephemeral models
* Log warnings for fixes that seem to corrupt the parse SQL as may cause incorrect fixes in other rules.
* Bug fix to rule L011 for `implicit` aliases
* Bug fix to rule L019 for commas besides templated code
* Rule L051 can now optionally be applied to `LEFT`/`RIGHT`/`OUTER JOIN`s
* Improvements to Test Suite
* Many dialect improvements

## What’s Changed
* Exasol: Fix `INTERVAL` literals / expression [#2804](https://github.com/sqlfluff/sqlfluff/pull/2804) [@sti0](https://github.com/sti0)
* Exasol: Add `IDLE_TIMEOUT` and `SNAPSHOT_MODE` [#2805](https://github.com/sqlfluff/sqlfluff/pull/2805) [@sti0](https://github.com/sti0)
* Exasol: Support value range clause within `INSERT` statements (7.1+) [#2802](https://github.com/sqlfluff/sqlfluff/pull/2802) [@sti0](https://github.com/sti0)
* Exasol: Add lua adapter scripts (7.1+) [#2801](https://github.com/sqlfluff/sqlfluff/pull/2801) [@sti0](https://github.com/sti0)
* Exasol: Add openid support for create/alter user (7.1+) [#2800](https://github.com/sqlfluff/sqlfluff/pull/2800) [@sti0](https://github.com/sti0)
* Exasol: New consumer group params and unreserved keywords (7.1+) [#2799](https://github.com/sqlfluff/sqlfluff/pull/2799) [@sti0](https://github.com/sti0)
* Snowflake: Complete `INSERT` grammar [#2798](https://github.com/sqlfluff/sqlfluff/pull/2798) [@jpy-git](https://github.com/jpy-git)
* Fix Postgres `VALUES`, make Spark3 `VALUES` consistent [#2797](https://github.com/sqlfluff/sqlfluff/pull/2797) [@jpy-git](https://github.com/jpy-git)
* Postgres: `INSERT DEFAULT` value [#2796](https://github.com/sqlfluff/sqlfluff/pull/2796) [@jpy-git](https://github.com/jpy-git)
* Postgres: Make `AS` optional in Postgres `DELETE` [#2794](https://github.com/sqlfluff/sqlfluff/pull/2794) [@jpy-git](https://github.com/jpy-git)
* BigQuery support `UNEST` aliases [#2793](https://github.com/sqlfluff/sqlfluff/pull/2793) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Add all range operators [#2789](https://github.com/sqlfluff/sqlfluff/pull/2789) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Complete `DELETE FROM` grammar [#2792](https://github.com/sqlfluff/sqlfluff/pull/2792) [@jpy-git](https://github.com/jpy-git)
* Postgres: Complete `DELETE FROM` grammar [#2791](https://github.com/sqlfluff/sqlfluff/pull/2791) [@jpy-git](https://github.com/jpy-git)
* Postgres: Add `RETURNING` grammar to `INSERT INTO` statement [#2790](https://github.com/sqlfluff/sqlfluff/pull/2790) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Complete `PATTERN` grammar [#2788](https://github.com/sqlfluff/sqlfluff/pull/2788) [@jpy-git](https://github.com/jpy-git)
* Redshift: add `[ALTER/CREATE/DROP] PROCEDURE` segments [#2774](https://github.com/sqlfluff/sqlfluff/pull/2774) [@rpr-ableton](https://github.com/rpr-ableton)
* Spark3: Support for `ANALYZE TABLE` statement [#2780](https://github.com/sqlfluff/sqlfluff/pull/2780) [@R7L208](https://github.com/R7L208)
* Snowflake: Add `MATCH_RECOGNIZE` clause [#2781](https://github.com/sqlfluff/sqlfluff/pull/2781) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Complete `LIMIT` grammar [#2784](https://github.com/sqlfluff/sqlfluff/pull/2784) [@jpy-git](https://github.com/jpy-git)
* Rough autofix for L028 [#2757](https://github.com/sqlfluff/sqlfluff/pull/2757) [@OTooleMichael](https://github.com/OTooleMichael)
* Spark3 bug: Create with complex data types (#2761) [#2782](https://github.com/sqlfluff/sqlfluff/pull/2782) [@PhilippLange](https://github.com/PhilippLange)
* Snowflake: Complete `LIKE` grammar [#2779](https://github.com/sqlfluff/sqlfluff/pull/2779) [@jpy-git](https://github.com/jpy-git)
* Spark3: Auxiliary`FILE` and `JAR` statements [#2778](https://github.com/sqlfluff/sqlfluff/pull/2778) [@R7L208](https://github.com/R7L208)
* Snowflake: Refine `SET`/`UNSET` `MASKING POLICY` grammar [#2775](https://github.com/sqlfluff/sqlfluff/pull/2775) [@jpy-git](https://github.com/jpy-git)
* L049 bug: correct over zealous `=` --> `IS` [#2760](https://github.com/sqlfluff/sqlfluff/pull/2760) [@OTooleMichael](https://github.com/OTooleMichael)
* Make extension case insensitive [#2773](https://github.com/sqlfluff/sqlfluff/pull/2773) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Add dollar quoted string literal [#2770](https://github.com/sqlfluff/sqlfluff/pull/2770) [@jpy-git](https://github.com/jpy-git)
* Bug fix: L036 corrupts `SELECT DISTINCT id` query [#2768](https://github.com/sqlfluff/sqlfluff/pull/2768) [@barrywhart](https://github.com/barrywhart)
* Snowflake: Add `CHANGES` clause [#2764](https://github.com/sqlfluff/sqlfluff/pull/2764) [@jpy-git](https://github.com/jpy-git)
* Spark3: Support for `EXPLAIN` statement [#2767](https://github.com/sqlfluff/sqlfluff/pull/2767) [@R7L208](https://github.com/R7L208)
* Snowflake: Add `CONNECT BY` clause [#2763](https://github.com/sqlfluff/sqlfluff/pull/2763) [@jpy-git](https://github.com/jpy-git)
* Spark3: Support for `TRANSFORM` clause [#2762](https://github.com/sqlfluff/sqlfluff/pull/2762) [@R7L208](https://github.com/R7L208)
* Snowflake: Fix `GROUP BY {CUBE|ROLLUP|GROUPING SETS}` parsing [#2759](https://github.com/sqlfluff/sqlfluff/pull/2759) [@jpy-git](https://github.com/jpy-git)
* BigQuery: allow identifiers starting with dash [#2756](https://github.com/sqlfluff/sqlfluff/pull/2756) [@tunetheweb](https://github.com/tunetheweb)
* Add `ignore_words` options to L057 and L059 [#2753](https://github.com/sqlfluff/sqlfluff/pull/2753) [@tunetheweb](https://github.com/tunetheweb)
* L012 bug fix for T-SQL alternative alias types [#2750](https://github.com/sqlfluff/sqlfluff/pull/2750) [@tunetheweb](https://github.com/tunetheweb)
* Spark3: Support for `PIVOT` clause [#2752](https://github.com/sqlfluff/sqlfluff/pull/2752) [@R7L208](https://github.com/R7L208)
* Update Redshift reserved keywords list [#2751](https://github.com/sqlfluff/sqlfluff/pull/2751) [@rpr-ableton](https://github.com/rpr-ableton)
* L007 autofix [#2735](https://github.com/sqlfluff/sqlfluff/pull/2735) [@OTooleMichael](https://github.com/OTooleMichael)
* L032 fixable in easy cases [#2737](https://github.com/sqlfluff/sqlfluff/pull/2737) [@OTooleMichael](https://github.com/OTooleMichael)
* Fix dbt templater runtime error in `inject_ctes_into_sql()` [#2748](https://github.com/sqlfluff/sqlfluff/pull/2748) [@barrywhart](https://github.com/barrywhart)
* L059: Exasol: Allow quotes around passwords in `CREATE USER` [#2744](https://github.com/sqlfluff/sqlfluff/pull/2744) [@sti0](https://github.com/sti0)
* Improve docs for `load_macros_from_path` [#2743](https://github.com/sqlfluff/sqlfluff/pull/2743) [@barrywhart](https://github.com/barrywhart)
* Make L045 (Query defines a CTE but does not use it) case insensitive [#2746](https://github.com/sqlfluff/sqlfluff/pull/2746) [@barrywhart](https://github.com/barrywhart)
* Add L049 test for T-SQL alternate alias syntax (`=`) [#2745](https://github.com/sqlfluff/sqlfluff/pull/2745) [@barrywhart](https://github.com/barrywhart)
* `BaseSegment.pos_marker` is typed as non optional but sometimes set to `None` [#2741](https://github.com/sqlfluff/sqlfluff/pull/2741) [@barrywhart](https://github.com/barrywhart)
* Support Pascal case for L030 [#2739](https://github.com/sqlfluff/sqlfluff/pull/2739) [@tunetheweb](https://github.com/tunetheweb)
* Postgres, Redshift: Support `SIMILAR TO` pattern matching expressions [#2732](https://github.com/sqlfluff/sqlfluff/pull/2732) [@PLBMR](https://github.com/PLBMR)
* Forgive shorthand cast only / bracket only expressions from L013 [#2729](https://github.com/sqlfluff/sqlfluff/pull/2729) [@OTooleMichael](https://github.com/OTooleMichael)
* L052: Refactor `_eval()` into individual functions to improve readability [#2733](https://github.com/sqlfluff/sqlfluff/pull/2733) [@barrywhart](https://github.com/barrywhart)
* L018: Move closing parenthesis to next line [#2734](https://github.com/sqlfluff/sqlfluff/pull/2734) [@barrywhart](https://github.com/barrywhart)
* Improve rule yaml tests: assert that `fix_str` passes the rule [#2624](https://github.com/sqlfluff/sqlfluff/pull/2624) [@juhoautio](https://github.com/juhoautio)
*  Extend rule L051 to `LEFT`/`RIGHT`/`OUTER` `JOIN`s [#2719](https://github.com/sqlfluff/sqlfluff/pull/2719) [@rpr-ableton](https://github.com/rpr-ableton)
* T-SQL: Allow aliases with `=` [#2727](https://github.com/sqlfluff/sqlfluff/pull/2727) [@fdw](https://github.com/fdw)
* T-SQL: Support table variables [#2728](https://github.com/sqlfluff/sqlfluff/pull/2728) [@fdw](https://github.com/fdw)
* Support for checking violations in YAML rule tests [#2718](https://github.com/sqlfluff/sqlfluff/pull/2718) [@juhoautio](https://github.com/juhoautio)
* Roll back PR #2610 [#2726](https://github.com/sqlfluff/sqlfluff/pull/2726) [@barrywhart](https://github.com/barrywhart)
* Redshift: Allow whitespace around cast operators [#2721](https://github.com/sqlfluff/sqlfluff/pull/2721) [@PLBMR](https://github.com/PLBMR)
* Support database links in Oracle [#2725](https://github.com/sqlfluff/sqlfluff/pull/2725) [@tunetheweb](https://github.com/tunetheweb)
* Rule L019: Ignore comma placement violations if the adjacent code is templated [#2717](https://github.com/sqlfluff/sqlfluff/pull/2717) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Add drop constraint syntax [#2724](https://github.com/sqlfluff/sqlfluff/pull/2724) [@fdw](https://github.com/fdw)
* ANSI: Support optionally bracketed CTE [#2716](https://github.com/sqlfluff/sqlfluff/pull/2716) [@OTooleMichael](https://github.com/OTooleMichael)
* Spark3: Test cases for `CASE` clause [#2714](https://github.com/sqlfluff/sqlfluff/pull/2714) [@R7L208](https://github.com/R7L208)
* Spark3: Support for `WINDOW` functions [#2711](https://github.com/sqlfluff/sqlfluff/pull/2711) [@R7L208](https://github.com/R7L208)
* T-SQL: Add variables as options for `RAISERROR` parameters [#2709](https://github.com/sqlfluff/sqlfluff/pull/2709) [@jpers36](https://github.com/jpers36)
* T-SQL: Add `OPTION` clause to `UPDATE` [#2707](https://github.com/sqlfluff/sqlfluff/pull/2707) [@jpers36](https://github.com/jpers36)
* Spark3: Test cases for `WHERE` clause [#2704](https://github.com/sqlfluff/sqlfluff/pull/2704) [@R7L208](https://github.com/R7L208)
* Spark3: test cases for Table-Valued Functions [#2703](https://github.com/sqlfluff/sqlfluff/pull/2703) [@R7L208](https://github.com/R7L208)
* T-SQL: Allow for optionally bracketed `PARTITION BY` elements [#2702](https://github.com/sqlfluff/sqlfluff/pull/2702) [@jpers36](https://github.com/jpers36)
* T-SQL: Fix `SET TRANSACTION ISOLATION LEVEL` parsing [#2701](https://github.com/sqlfluff/sqlfluff/pull/2701) [@jpers36](https://github.com/jpers36)
* Migrate tricky L004 tests to python [#2681](https://github.com/sqlfluff/sqlfluff/pull/2681) [@juhoautio](https://github.com/juhoautio)
* Core linter enhancement: Check for successful parse after applying fixes [#2657](https://github.com/sqlfluff/sqlfluff/pull/2657) [@barrywhart](https://github.com/barrywhart)
* Spark3: Support for `LATERAL VIEW` clause [#2687](https://github.com/sqlfluff/sqlfluff/pull/2687) [@R7L208](https://github.com/R7L208)
* Document python requirement for tox/mypy & remove basepython from conf [#2644](https://github.com/sqlfluff/sqlfluff/pull/2644) [@juhoautio](https://github.com/juhoautio)
* Fix rule L011 for implicit aliases [#2683](https://github.com/sqlfluff/sqlfluff/pull/2683) [@tunetheweb](https://github.com/tunetheweb)
* Pin markupsafe to prevent CI failures [#2685](https://github.com/sqlfluff/sqlfluff/pull/2685) [@tunetheweb](https://github.com/tunetheweb)
* Exasol: Allow `CROSS` joins [#2680](https://github.com/sqlfluff/sqlfluff/pull/2680) [@sti0](https://github.com/sti0)
* Exasol: Improve function formatting [#2678](https://github.com/sqlfluff/sqlfluff/pull/2678) [@sti0](https://github.com/sti0)
* T-SQL: Add indentation for `CREATE` `INDEX`/`STATISTICS` [#2679](https://github.com/sqlfluff/sqlfluff/pull/2679) [@jpers36](https://github.com/jpers36)
* Spark3: Support for `TABLESAMPLE` clause [#2674](https://github.com/sqlfluff/sqlfluff/pull/2674) [@R7L208](https://github.com/R7L208)
* T-SQL: Improve `RAISERROR` functionality [#2672](https://github.com/sqlfluff/sqlfluff/pull/2672) [@jpers36](https://github.com/jpers36)
* Snowflake dialect update for `MERGE INTO` predicates [#2670](https://github.com/sqlfluff/sqlfluff/pull/2670) [@The-Loud](https://github.com/The-Loud)
* Assert that fix_str is set [#2663](https://github.com/sqlfluff/sqlfluff/pull/2663) [@juhoautio](https://github.com/juhoautio)

## New Contributors
* [@The-Loud](https://github.com/The-Loud) made their first contribution in [#2670](https://github.com/sqlfluff/sqlfluff/pull/2670)
* [@OTooleMichael](https://github.com/OTooleMichael) made their first contribution in [#2716](https://github.com/sqlfluff/sqlfluff/pull/2716)
* [@PhilippLange](https://github.com/PhilippLange) made their first contribution in [#2782](https://github.com/sqlfluff/sqlfluff/pull/2782)

## [0.10.1] - 2022-02-15

## Highlights
Major changes include:
* Improvements to rules L023, L045, L048, L052, L059 to make them more accurate.
* If `sqlfluff fix` cannot find a stable fix after `runaway_limit` iterations (default 10) then no fixes will be applied.
* Addition of `--write-output` config to command line so prevent errors corrupting output.
* Various dialect improvements


## What’s Changed
* Redshift: Support DATETIME as a valid datatype [#2665](https://github.com/sqlfluff/sqlfluff/pull/2665) [@PLBMR](https://github.com/PLBMR)
* Support L033 for RedShift [#2661](https://github.com/sqlfluff/sqlfluff/pull/2661) [@tunetheweb](https://github.com/tunetheweb)
* Fix parsing types and add check to test in future [#2652](https://github.com/sqlfluff/sqlfluff/pull/2652) [@tunetheweb](https://github.com/tunetheweb)
* Spark3: Support for `SORT BY` Clause [#2651](https://github.com/sqlfluff/sqlfluff/pull/2651) [@R7L208](https://github.com/R7L208)
* Migrate issue template from markdown to yaml [#2626](https://github.com/sqlfluff/sqlfluff/pull/2626) [@zhongjiajie](https://github.com/zhongjiajie)
* L048 - handle more statements and exclude casting operators [#2642](https://github.com/sqlfluff/sqlfluff/pull/2642) [@tunetheweb](https://github.com/tunetheweb)
* MySQL support `CURRENT_TIMESTAMP()` in `CREATE TABLE` [#2648](https://github.com/sqlfluff/sqlfluff/pull/2648) [@tunetheweb](https://github.com/tunetheweb)
* Postgres enhanced `DELETE FROM` syntax [#2643](https://github.com/sqlfluff/sqlfluff/pull/2643) [@tunetheweb](https://github.com/tunetheweb)
* Bug fix: L025 should consider BigQuery `QUALIFY` clause [#2647](https://github.com/sqlfluff/sqlfluff/pull/2647) [@barrywhart](https://github.com/barrywhart)
* Bug fix: L025 overlooking `JOIN ON` clause if join expression in parentheses [#2645](https://github.com/sqlfluff/sqlfluff/pull/2645) [@barrywhart](https://github.com/barrywhart)
* L045 not reporting unused CTEs if the query uses templating [#2641](https://github.com/sqlfluff/sqlfluff/pull/2641) [@barrywhart](https://github.com/barrywhart)
* Fix IndexError in L001 [#2640](https://github.com/sqlfluff/sqlfluff/pull/2640) [@barrywhart](https://github.com/barrywhart)
* L052: If require_final_semicolon is set, ensure semicolon after ALL statements [#2610](https://github.com/sqlfluff/sqlfluff/pull/2610) [@barrywhart](https://github.com/barrywhart)
* L023 to also fix extra newlines in CTE [#2623](https://github.com/sqlfluff/sqlfluff/pull/2623) [@juhoautio](https://github.com/juhoautio)
* Spark3: Enhancements for Set Operators [#2622](https://github.com/sqlfluff/sqlfluff/pull/2622) [@R7L208](https://github.com/R7L208)
* Doc a better choice for default env [#2630](https://github.com/sqlfluff/sqlfluff/pull/2630) [@juhoautio](https://github.com/juhoautio)
* Ensure ordering of fix compatible and config in rules docs [#2620](https://github.com/sqlfluff/sqlfluff/pull/2620) [@zhongjiajie](https://github.com/zhongjiajie)
* Pin python version for tox -e mypy [#2629](https://github.com/sqlfluff/sqlfluff/pull/2629) [@juhoautio](https://github.com/juhoautio)
* Hitting the linter loop limit should be treated as an error [#2628](https://github.com/sqlfluff/sqlfluff/pull/2628) [@barrywhart](https://github.com/barrywhart)
* Allow file output directly from cli [#2625](https://github.com/sqlfluff/sqlfluff/pull/2625) [@alanmcruickshank](https://github.com/alanmcruickshank)
* BigQuery `UNPIVOT` and `PIVOT` fixes [#2619](https://github.com/sqlfluff/sqlfluff/pull/2619) [@tunetheweb](https://github.com/tunetheweb)
* L059 quoted identifiers bug [#2614](https://github.com/sqlfluff/sqlfluff/pull/2614) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake dialect: Adjust snowflake array access [#2621](https://github.com/sqlfluff/sqlfluff/pull/2621) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Spark3: Test Cases for `ORDER BY` in `SELECT` [#2618](https://github.com/sqlfluff/sqlfluff/pull/2618) [@R7L208](https://github.com/R7L208)
* Fix typos in 0.10.0 changelog [#2605](https://github.com/sqlfluff/sqlfluff/pull/2605) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Indent `IF` clause expression segments [#2615](https://github.com/sqlfluff/sqlfluff/pull/2615) [@jpers36](https://github.com/jpers36)
* Spark3: Enhancements for `LIMIT` Clause [#2612](https://github.com/sqlfluff/sqlfluff/pull/2612) [@R7L208](https://github.com/R7L208)
* Allow Bare Functions in column constraints [#2607](https://github.com/sqlfluff/sqlfluff/pull/2607) [@tunetheweb](https://github.com/tunetheweb)
* Add Oracle at and double at sign (execution symbol) [#2608](https://github.com/sqlfluff/sqlfluff/pull/2608) [@r0fls](https://github.com/r0fls)
* Spark3: Enhancements to `LIKE` clause [#2604](https://github.com/sqlfluff/sqlfluff/pull/2604) [@R7L208](https://github.com/R7L208)

## [0.10.0] - 2022-02-10

## Highlights
Major changes include:

* Dropping support of DBT < 0.20 **BREAKING CHANGE**
* `sqlfluff fix` no will no longer fix SQL containing parsing or templating errors **BREAKING CHANGE**
* New rule L062 to allow blocking of list of configurable words (e.g. syntax, or schemas, or tables you do not want people to use)
* Lots and lots of docs improvements
* Looser requirements for `click` python package

## What’s Changed
* L046: Detect Jinja spacing issues where segment begins with literal content [#2603](https://github.com/sqlfluff/sqlfluff/pull/2603) [@barrywhart](https://github.com/barrywhart)
* MySQL Add BINARY support [#2602](https://github.com/sqlfluff/sqlfluff/pull/2602) [@tunetheweb](https://github.com/tunetheweb)
* Support indenting WINDOWS clauses and (optionally) CTEs [#2601](https://github.com/sqlfluff/sqlfluff/pull/2601) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Support expressions in arrays [#2599](https://github.com/sqlfluff/sqlfluff/pull/2599) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery support Array of Structs [#2598](https://github.com/sqlfluff/sqlfluff/pull/2598) [@tunetheweb](https://github.com/tunetheweb)
* Support wildcards in triggers [#2597](https://github.com/sqlfluff/sqlfluff/pull/2597) [@tunetheweb](https://github.com/tunetheweb)
* Support CTEs in CREATE VIEW statements [#2596](https://github.com/sqlfluff/sqlfluff/pull/2596) [@tunetheweb](https://github.com/tunetheweb)
* SQLite Support more CREATE TRIGGER options [#2594](https://github.com/sqlfluff/sqlfluff/pull/2594) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Support Column Comments in Alter Table statements [#2593](https://github.com/sqlfluff/sqlfluff/pull/2593) [@tunetheweb](https://github.com/tunetheweb)
* Redshift: Add DATETIME as reserved keyword [#2591](https://github.com/sqlfluff/sqlfluff/pull/2591) [@tunetheweb](https://github.com/tunetheweb)
* Support LIMIT and ORDER BY clauses in Values clauses [#2590](https://github.com/sqlfluff/sqlfluff/pull/2590) [@tunetheweb](https://github.com/tunetheweb)
* L016: New option "ignore_comment_clause" to ignore column COMMENTs, etc. [#2589](https://github.com/sqlfluff/sqlfluff/pull/2589) [@barrywhart](https://github.com/barrywhart)
* Bug fix: L016 ("Line is too long") should consider length of prior fixes [#2587](https://github.com/sqlfluff/sqlfluff/pull/2587) [@barrywhart](https://github.com/barrywhart)
* Add mysql INSERT ON DUPLICATE KEY [#2494](https://github.com/sqlfluff/sqlfluff/pull/2494) [@rpr-ableton](https://github.com/rpr-ableton)
* Snowflake ALTER TABLE: Add multiple columns [#2578](https://github.com/sqlfluff/sqlfluff/pull/2578) [@erevear](https://github.com/erevear)
* MySQL: UNIQUE KEY in CREATE TABLE [#2525](https://github.com/sqlfluff/sqlfluff/pull/2525) [@jpy-git](https://github.com/jpy-git)
* Spark3: JOIN clause enhancements [#2570](https://github.com/sqlfluff/sqlfluff/pull/2570) [@R7L208](https://github.com/R7L208)
* Bug fix: L003 should fix indentation for templated code [#2580](https://github.com/sqlfluff/sqlfluff/pull/2580) [@barrywhart](https://github.com/barrywhart)
* Exasol: Improve `COMMENT` and `WITH [NO] DATA` clause usage. [#2583](https://github.com/sqlfluff/sqlfluff/pull/2583) [@sti0](https://github.com/sti0)
* Exasol: Allow multiple `LOCAL` keywords in `WHERE` clause [#2582](https://github.com/sqlfluff/sqlfluff/pull/2582) [@sti0](https://github.com/sti0)
* Exasol: Allow `LOCAL` keyword within `PREFERRING` clause [#2579](https://github.com/sqlfluff/sqlfluff/pull/2579) [@sti0](https://github.com/sti0)
* Add/Improve docs for config settings: "ignore", "ignore_templated_areas" [#2574](https://github.com/sqlfluff/sqlfluff/pull/2574) [@barrywhart](https://github.com/barrywhart)
* Look for .sqlfluffignore in current directory [#2573](https://github.com/sqlfluff/sqlfluff/pull/2573) [@barrywhart](https://github.com/barrywhart)
* Snowflake: L054 should ignore "WITHIN GROUP" clauses [#2571](https://github.com/sqlfluff/sqlfluff/pull/2571) [@barrywhart](https://github.com/barrywhart)
* Redshift: Support Redshift SUPER Data Types [#2564](https://github.com/sqlfluff/sqlfluff/pull/2564) [@PLBMR](https://github.com/PLBMR)
* Capitalization rules (L010, L014, L030, L040) should ignore templated code [#2566](https://github.com/sqlfluff/sqlfluff/pull/2566) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Add Frame clause unreserved keywords [#2562](https://github.com/sqlfluff/sqlfluff/pull/2562) [@jpers36](https://github.com/jpers36)
* Simple API: Fix bug where omitted parameters still override .sqlfluff [#2563](https://github.com/sqlfluff/sqlfluff/pull/2563) [@barrywhart](https://github.com/barrywhart)
* Spark3: Add Direct File Query [#2553](https://github.com/sqlfluff/sqlfluff/pull/2553) [@R7L208](https://github.com/R7L208)
* Redshift dialect: replace AnyNumberOf with AnySetOf where it makes sense [#2561](https://github.com/sqlfluff/sqlfluff/pull/2561) [@rpr-ableton](https://github.com/rpr-ableton)
* jinja and dbt templaters: More robust handling of whitespace control [#2559](https://github.com/sqlfluff/sqlfluff/pull/2559) [@barrywhart](https://github.com/barrywhart)
* Improve how "sqlfluff fix" handles templating and parse errors [#2546](https://github.com/sqlfluff/sqlfluff/pull/2546) [@barrywhart](https://github.com/barrywhart)
* Jinja and dbt templater: Fix "list index out of range" error [#2555](https://github.com/sqlfluff/sqlfluff/pull/2555) [@barrywhart](https://github.com/barrywhart)
* Fix typo in sqlfluffignore docs [#2551](https://github.com/sqlfluff/sqlfluff/pull/2551) [@tunetheweb](https://github.com/tunetheweb)
* Correct parsing for BigQuery `SELECT REPLACE` clauses. [#2550](https://github.com/sqlfluff/sqlfluff/pull/2550) [@elyobo](https://github.com/elyobo)
* Rules documentation improvements [#2542](https://github.com/sqlfluff/sqlfluff/pull/2542) [@tunetheweb](https://github.com/tunetheweb)
* Remove requirement for Click>=8 [#2547](https://github.com/sqlfluff/sqlfluff/pull/2547) [@tunetheweb](https://github.com/tunetheweb)
* Allow L059 to be configured to always prefer quoted identifiers [#2537](https://github.com/sqlfluff/sqlfluff/pull/2537) [@niconoe-](https://github.com/niconoe-)
* Adds new rule L062 to allow blocking of certain words [#2540](https://github.com/sqlfluff/sqlfluff/pull/2540) [@tunetheweb](https://github.com/tunetheweb)
* Update to latest Black, drop support for dbt < 0.20 [#2536](https://github.com/sqlfluff/sqlfluff/pull/2536) [@barrywhart](https://github.com/barrywhart)
* dbt templater: Fix bug where profile wasn't found if DBT_PROFILES_DIR contained uppercase letters [#2539](https://github.com/sqlfluff/sqlfluff/pull/2539) [@barrywhart](https://github.com/barrywhart)
* Spark3: Added segments & grammar needed for hints [#2528](https://github.com/sqlfluff/sqlfluff/pull/2528) [@R7L208](https://github.com/R7L208)
* Spark3: parse some VALUES clauses [#2245](https://github.com/sqlfluff/sqlfluff/pull/2245) [@mcannamela](https://github.com/mcannamela)
* T-SQL: Allow multiple params in SET statements [#2535](https://github.com/sqlfluff/sqlfluff/pull/2535) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Add indentation for SET statement [#2531](https://github.com/sqlfluff/sqlfluff/pull/2531) [@jpers36](https://github.com/jpers36)
* Add additional documentation on dbt-adapter in pre-commit [#2530](https://github.com/sqlfluff/sqlfluff/pull/2530) [@robertdefilippi](https://github.com/robertdefilippi)
* T-SQL: Add indentation for UPDATE statement [#2532](https://github.com/sqlfluff/sqlfluff/pull/2532) [@jpers36](https://github.com/jpers36)
* Fix Snowflake Unordered Select Clause [#2529](https://github.com/sqlfluff/sqlfluff/pull/2529) [@tunetheweb](https://github.com/tunetheweb)
* Fix Quoted Literals for Postgres and Redshift affecting rule L039 [#2526](https://github.com/sqlfluff/sqlfluff/pull/2526) [@tunetheweb](https://github.com/tunetheweb)
* Postgres specific CTEDefinitionSegment [#2524](https://github.com/sqlfluff/sqlfluff/pull/2524) [@jpy-git](https://github.com/jpy-git)

## New Contributors
* [@robertdefilippi](https://github.com/robertdefilippi) made their first contribution in [#2530](https://github.com/sqlfluff/sqlfluff/pull/2530)
* [@niconoe-](https://github.com/niconoe-) made their first contribution in [#2537](https://github.com/sqlfluff/sqlfluff/pull/2537)
* [@elyobo](https://github.com/elyobo) made their first contribution in [#2550](https://github.com/sqlfluff/sqlfluff/pull/2550)
* [@erevear](https://github.com/erevear) made their first contribution in [#2578](https://github.com/sqlfluff/sqlfluff/pull/2578)


## [0.9.4] - 2022-01-30

## Highlights
Major changes include:

* dbt performance improvements
* Fix `click` dependency error.
* Better datepart versus identifier parsing.
* Fix some Jinja errors.
* Various grammar fixes and improvements

## What’s Changed
* Spark3: test cases for HAVING clause in SELECT statement [#2518](https://github.com/sqlfluff/sqlfluff/pull/2517) [@R7L208](https://github.com/R7L208)
* Update click version requirement in setup.cfg to match that in requirements.txt [#2518](https://github.com/sqlfluff/sqlfluff/pull/2518) [@barrywhart](https://github.com/barrywhart)
* Postgres: Implement DO Statements + Refactored Language Clause [#2511](https://github.com/sqlfluff/sqlfluff/pull/2511) [@PLBMR](https://github.com/PLBMR)
* Spark3: Support for Grouping Sets, `CUBE` and `ROLLUP` in `GROUP BY` clause of `SELECT` statement [#2505](https://github.com/sqlfluff/sqlfluff/pull/2505) [@R7L208](https://github.com/R7L208)
* Refactor date part functions [#2510](https://github.com/sqlfluff/sqlfluff/pull/2510) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: EXPLAIN ANALYSE allows British spelling [#2507](https://github.com/sqlfluff/sqlfluff/pull/2507) [@jpy-git](https://github.com/jpy-git)
* "noqa": Add support for ignoring template (TMP) and parse (PRS) errors [#2509](https://github.com/sqlfluff/sqlfluff/pull/2509) [@barrywhart](https://github.com/barrywhart)
* Freeze Black due to incompatibility between 22.1 and flake8-black [#2513](https://github.com/sqlfluff/sqlfluff/pull/2513) [@tunetheweb](https://github.com/tunetheweb)
* Support NATURAL JOINS [#2506](https://github.com/sqlfluff/sqlfluff/pull/2506) [@tunetheweb](https://github.com/tunetheweb)
* dbt Docker environment: Mount the test profiles.yml at ~/.dbt [#2502](https://github.com/sqlfluff/sqlfluff/pull/2502) [@barrywhart](https://github.com/barrywhart)
* Add dbt_artifacts package to in the wild docs [#2504](https://github.com/sqlfluff/sqlfluff/pull/2504) [@NiallRees](https://github.com/NiallRees)
* Spark3: Support `DISTRIBUTE BY` clause in `SELECT` statement [#2503](https://github.com/sqlfluff/sqlfluff/pull/2503) [@R7L208](https://github.com/R7L208)
* dbt templater: For performance reasons, cache the database connection across models [#2498](https://github.com/sqlfluff/sqlfluff/pull/2498) [@barrywhart](https://github.com/barrywhart)
* Bug fix: Defining and using Jinja macro in the same file causes runtime error [#2499](https://github.com/sqlfluff/sqlfluff/pull/2499) [@barrywhart](https://github.com/barrywhart)
* Spark3: Support `CLUSTER BY` clause in `SELECT` statement [#2491](https://github.com/sqlfluff/sqlfluff/pull/2491) [@R7L208](https://github.com/R7L208)
* Grammar: Adds support for COPY statement for Postgres dialect [#2481](https://github.com/sqlfluff/sqlfluff/pull/2481) [@derickl](https://github.com/derickl)
* Add raiserror for T-SQL [#2490](https://github.com/sqlfluff/sqlfluff/pull/2490) [@fdw](https://github.com/fdw)
* Enforce parentheses for function definitions in T-SQL [#2489](https://github.com/sqlfluff/sqlfluff/pull/2489) [@fdw](https://github.com/fdw)
* Add guards to prevent rule crashes [#2488](https://github.com/sqlfluff/sqlfluff/pull/2488) [@barrywhart](https://github.com/barrywhart)

## New Contributors
* [@PLBMR](https://github.com/PLBMR) made their first contribution in [#2511](https://github.com/sqlfluff/sqlfluff/pull/2511)

## [0.9.3] - 2022-01-26

## Highlights
Major changes include:

* Add `ignore_words` option for rules L010, L014, L029, L030, L040
* Fix some issues in 0.9.2 preventing some queries linting

## What’s Changed
* Prevent L031 throwing exception on unparsable code [#2486](https://github.com/sqlfluff/sqlfluff/pull/2486) [@tunetheweb](https://github.com/tunetheweb)
* Add linting of fixtures SQL for critical rules errors to tox [#2473](https://github.com/sqlfluff/sqlfluff/pull/2473) [@tunetheweb](https://github.com/tunetheweb)
* Fix L039 for T-SQL comparison operator using space [#2485](https://github.com/sqlfluff/sqlfluff/pull/2485) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug in get_alias causing rule Critical errors for T-SQL [#2479](https://github.com/sqlfluff/sqlfluff/pull/2479) [@tunetheweb](https://github.com/tunetheweb)
* Tweak GitHub templates [#2471](https://github.com/sqlfluff/sqlfluff/pull/2471) [@tunetheweb](https://github.com/tunetheweb)
* Small speed improvement to L054 [#2476](https://github.com/sqlfluff/sqlfluff/pull/2476) [@tunetheweb](https://github.com/tunetheweb)
* L003: Revisit recent change to improve speed [#2474](https://github.com/sqlfluff/sqlfluff/pull/2474) [@barrywhart](https://github.com/barrywhart)
* Fix select_crawler issue with some Exasol statements [#2470](https://github.com/sqlfluff/sqlfluff/pull/2470) [@tunetheweb](https://github.com/tunetheweb)
* Cleanup date logic by removing DatePartClause and using DatetimeUnitSegment instead [#2464](https://github.com/sqlfluff/sqlfluff/pull/2464) [@tunetheweb](https://github.com/tunetheweb)
* Fix L044 exception when final statement has no SELECT [#2468](https://github.com/sqlfluff/sqlfluff/pull/2468) [@tunetheweb](https://github.com/tunetheweb)
* Support T-SQL system variables (e.g. @@rowcount) [#2463](https://github.com/sqlfluff/sqlfluff/pull/2463) [@tunetheweb](https://github.com/tunetheweb)
* Add base rule to developing rules page [#2462](https://github.com/sqlfluff/sqlfluff/pull/2462) [@tunetheweb](https://github.com/tunetheweb)
* L003: Ignore indentation of lines that only exist in templated space [#2460](https://github.com/sqlfluff/sqlfluff/pull/2460) [@barrywhart](https://github.com/barrywhart)
* Ignore words for various rules [#2459](https://github.com/sqlfluff/sqlfluff/pull/2459) [@tunetheweb](https://github.com/tunetheweb)
* Support Foreign Key options for MySQL [#2461](https://github.com/sqlfluff/sqlfluff/pull/2461) [@tunetheweb](https://github.com/tunetheweb)
* Exclude WINDOW clauses from L054 [#2455](https://github.com/sqlfluff/sqlfluff/pull/2455) [@tunetheweb](https://github.com/tunetheweb)
* Fix bug with L026 for simple deletes [#2458](https://github.com/sqlfluff/sqlfluff/pull/2458) [@tunetheweb](https://github.com/tunetheweb)
* Spark3: test cases for Common Table Expressions [#2454](https://github.com/sqlfluff/sqlfluff/pull/2454) [@R7L208](https://github.com/R7L208)
* Fix T-SQL's IDENTITY_INSERT syntax [#2452](https://github.com/sqlfluff/sqlfluff/pull/2452) [@fdw](https://github.com/fdw)
* T-SQL: Support stored procedures in insert statements [#2451](https://github.com/sqlfluff/sqlfluff/pull/2451) [@fdw](https://github.com/fdw)
* Spark3: Support for `LOAD DATA` statements [#2450](https://github.com/sqlfluff/sqlfluff/pull/2450) [@R7L208](https://github.com/R7L208)


## [0.9.2] - 2022-01-24

## Highlights
We are pleased to include 110 improvements and fixes in this release, and welcome 7 new contributors to the code.

Major changes include:

* Initial Oracle support (note: SQL, but not PL/SQL)
* Fix more dbt 1.0.0 connection issues
* Improved configuration documentation
* New rule (L059) to flag unnecessary quoted identifiers
* New rule (L060) to prefer `COALESCE` instead of `IFNULL` or `NVL`
* New rule (L061) to prefer `!=` over `<>`
* Many rule fixes
* Many dialect improvements

## What’s Changed
* Add Postgres DROP PROCEDURE support [#2446](https://github.com/sqlfluff/sqlfluff/pull/2446) [@rpr-ableton](https://github.com/rpr-ableton)
* MySQL Alter table ADD/DROP/RENAME INDEX support [#2443](https://github.com/sqlfluff/sqlfluff/pull/2443) [@tunetheweb](https://github.com/tunetheweb)
* Add basic CREATE PROCEDURE support to Postgres [#2441](https://github.com/sqlfluff/sqlfluff/pull/2441) [@tunetheweb](https://github.com/tunetheweb)
* Indent T-SQL DECLARE and EXEC statements [#2439](https://github.com/sqlfluff/sqlfluff/pull/2439) [@tunetheweb](https://github.com/tunetheweb)
* Hive alternative types: INTEGER, DEC, NUMERIC [#2438](https://github.com/sqlfluff/sqlfluff/pull/2438) [@tunetheweb](https://github.com/tunetheweb)
* Implement Snowflake Dateparts [#2437](https://github.com/sqlfluff/sqlfluff/pull/2437) [@tunetheweb](https://github.com/tunetheweb)
* Fix rule L028 for T-SQL for params [#2442](https://github.com/sqlfluff/sqlfluff/pull/2442) [@tunetheweb](https://github.com/tunetheweb)
* Support CREATE UNIQUE INDEX [#2440](https://github.com/sqlfluff/sqlfluff/pull/2440) [@tunetheweb](https://github.com/tunetheweb)
* Make BigQuery typeless STRUCTs Expressions [#2435](https://github.com/sqlfluff/sqlfluff/pull/2435) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL support default params and no RETURN value [#2434](https://github.com/sqlfluff/sqlfluff/pull/2434) [@tunetheweb](https://github.com/tunetheweb)
* "sqlfluff fix" should report any parse errors found [#2423](https://github.com/sqlfluff/sqlfluff/pull/2423) [@barrywhart](https://github.com/barrywhart)
* Redshift VACUUM support [#2433](https://github.com/sqlfluff/sqlfluff/pull/2433) [@rpr-ableton](https://github.com/rpr-ableton)
* Add Oracle PROMPT statement [#2413](https://github.com/sqlfluff/sqlfluff/pull/2413) [@r0fls](https://github.com/r0fls)
* Spark3: Support for `INSERT OVERWRITE DIRECTORY` with Hive Format [#2389](https://github.com/sqlfluff/sqlfluff/pull/2389) [@R7L208](https://github.com/R7L208)
* Exasol: Fix escaped identifiers [#2431](https://github.com/sqlfluff/sqlfluff/pull/2431) [@sti0](https://github.com/sti0)
* Exasol: Fix `LOCAL.ALIAS` Syntax [#2430](https://github.com/sqlfluff/sqlfluff/pull/2430) [@sti0](https://github.com/sti0)
* Exasol: Allow quoted identifier for various statements. [#2428](https://github.com/sqlfluff/sqlfluff/pull/2428) [@sti0](https://github.com/sti0)
* Misc grammar improvements for Snowflake [#2421](https://github.com/sqlfluff/sqlfluff/pull/2421) [@chwiese](https://github.com/chwiese)
* New rule L061 to use != over <> [#2409](https://github.com/sqlfluff/sqlfluff/pull/2409) [@sti0](https://github.com/sti0)
* Correct TRANS to TRAN [#2425](https://github.com/sqlfluff/sqlfluff/pull/2425) [@fdw](https://github.com/fdw)
* Remove the "heuristic" slicer, as it was replaced by JinjaTracer [#2422](https://github.com/sqlfluff/sqlfluff/pull/2422) [@barrywhart](https://github.com/barrywhart)
* L060: More specific description [#2419](https://github.com/sqlfluff/sqlfluff/pull/2419) [@jpy-git](https://github.com/jpy-git)
* Fix code formatting in Rule docs [#2418](https://github.com/sqlfluff/sqlfluff/pull/2418) [@tunetheweb](https://github.com/tunetheweb)
* Allow UPDATE SET statements in RedShift [#2417](https://github.com/sqlfluff/sqlfluff/pull/2417) [@tunetheweb](https://github.com/tunetheweb)
* Add Redshift cursor DECLARE, FETCH & CLOSE support [#2414](https://github.com/sqlfluff/sqlfluff/pull/2414) [@rpr-ableton](https://github.com/rpr-ableton)
* Add Redshift ANALYZE COMPRESSION support [#2412](https://github.com/sqlfluff/sqlfluff/pull/2412) [@rpr-ableton](https://github.com/rpr-ableton)
* ANSI Values statement fixes [#2404](https://github.com/sqlfluff/sqlfluff/pull/2404) [@jpy-git](https://github.com/jpy-git)
* Exasol: Overhaul drop statements [#2407](https://github.com/sqlfluff/sqlfluff/pull/2407) [@sti0](https://github.com/sti0)
* L044, L045: Handle Exasol VALUES clause [#2400](https://github.com/sqlfluff/sqlfluff/pull/2400) [@barrywhart](https://github.com/barrywhart)
* L060: Use COALESCE instead of IFNULL or NVL. [#2405](https://github.com/sqlfluff/sqlfluff/pull/2405) [@jpy-git](https://github.com/jpy-git)
* Postgres: Fix Values alias regression [#2401](https://github.com/sqlfluff/sqlfluff/pull/2401) [@jpy-git](https://github.com/jpy-git)
* Align line length in Python code to 88 characters [#2264](https://github.com/sqlfluff/sqlfluff/pull/2264) [@chwiese](https://github.com/chwiese)
* Jinja templater: Allow "load_macros_from_path" to be a comma-separated list of paths [#2387](https://github.com/sqlfluff/sqlfluff/pull/2387) [@barrywhart](https://github.com/barrywhart)
* Add "TRANS" keyword for T-SQL [#2399](https://github.com/sqlfluff/sqlfluff/pull/2399) [@fdw](https://github.com/fdw)
* Docstrings: Replace double backticks with single quote for lint results. [#2386](https://github.com/sqlfluff/sqlfluff/pull/2386) [@jpy-git](https://github.com/jpy-git)
* Spark3: Support for `INSERT OVERWRITE DIRECTORY` statements [#2385](https://github.com/sqlfluff/sqlfluff/pull/2385) [@R7L208](https://github.com/R7L208)
* Fix unnecessary white underline in doc site [#2383](https://github.com/sqlfluff/sqlfluff/pull/2383) [@tunetheweb](https://github.com/tunetheweb)
* Rolls back some code cleanup that caused coverage report to show gaps [#2384](https://github.com/sqlfluff/sqlfluff/pull/2384) [@barrywhart](https://github.com/barrywhart)
* Fix "connection already closed" issue with dbt 1.0 and dbt_utils [#2382](https://github.com/sqlfluff/sqlfluff/pull/2382) [@barrywhart](https://github.com/barrywhart)
* Spark3: Support for `INSERT [TABLE]` data manipulation statements [#2290](https://github.com/sqlfluff/sqlfluff/pull/2290) [@R7L208](https://github.com/R7L208)
* Comment out line in bug report template [#2378](https://github.com/sqlfluff/sqlfluff/pull/2378) [@jpy-git](https://github.com/jpy-git)
* Postgres: EXPLAIN statement updates [#2374](https://github.com/sqlfluff/sqlfluff/pull/2374) [@jpy-git](https://github.com/jpy-git)
* Make TABLE a non-reserved word in Postgres [#2377](https://github.com/sqlfluff/sqlfluff/pull/2377) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake COLUMN is not a reserved word [#2376](https://github.com/sqlfluff/sqlfluff/pull/2376) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Complete ASA Table Index Clause functionality [#2373](https://github.com/sqlfluff/sqlfluff/pull/2373) [@jpers36](https://github.com/jpers36)
* Add support for Jinja import and include [#2355](https://github.com/sqlfluff/sqlfluff/pull/2355) [@barrywhart](https://github.com/barrywhart)
* Add Redshift INTERVAL datatype support [#2366](https://github.com/sqlfluff/sqlfluff/pull/2366) [@rpr-ableton](https://github.com/rpr-ableton)
* Whitespace concatenated string literals for MySQL, Postgres and Redshift [#2356](https://github.com/sqlfluff/sqlfluff/pull/2356) [@jpy-git](https://github.com/jpy-git)
* Fix L026 false positive on "SELECT INTO" statement [#2371](https://github.com/sqlfluff/sqlfluff/pull/2371) [@barrywhart](https://github.com/barrywhart)
* Exclude EMIT clauses from rule L013 [#2364](https://github.com/sqlfluff/sqlfluff/pull/2364) [@tunetheweb](https://github.com/tunetheweb)
* Functional API: Segments.recursive_crawl [#2369](https://github.com/sqlfluff/sqlfluff/pull/2369) [@jpy-git](https://github.com/jpy-git)
* Complete Redshift CREATE EXTERNAL TABLE support [#2354](https://github.com/sqlfluff/sqlfluff/pull/2354) [@rpr-ableton](https://github.com/rpr-ableton)
* L041: Fix duplicate DISTINCT corruption [#2365](https://github.com/sqlfluff/sqlfluff/pull/2365) [@jpy-git](https://github.com/jpy-git)
* Bigquery Create View with Options [#2359](https://github.com/sqlfluff/sqlfluff/pull/2359) [@tunetheweb](https://github.com/tunetheweb)
* L026: Handle DML statements and multiple levels of nesting [#2336](https://github.com/sqlfluff/sqlfluff/pull/2336) [@barrywhart](https://github.com/barrywhart)
* Postgres & MySQL: cleanup AliasExpressionSegment [#2353](https://github.com/sqlfluff/sqlfluff/pull/2353) [@jpy-git](https://github.com/jpy-git)
* Redefine MySQL Interval segment [#2351](https://github.com/sqlfluff/sqlfluff/pull/2351) [@rpr-ableton](https://github.com/rpr-ableton)
* Postgres: INSERT INTO table alias [#2349](https://github.com/sqlfluff/sqlfluff/pull/2349) [@jpy-git](https://github.com/jpy-git)
* L043: Remove redundant CASE statement replacing NULLS with NULLS [#2346](https://github.com/sqlfluff/sqlfluff/pull/2346) [@jpy-git](https://github.com/jpy-git)
* Add RedShift DATASHARE support [#2350](https://github.com/sqlfluff/sqlfluff/pull/2350) [@rpr-ableton](https://github.com/rpr-ableton)
* Various documentation updates [#2347](https://github.com/sqlfluff/sqlfluff/pull/2347) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake ALTER TABLE: Drop multiple columns [#2348](https://github.com/sqlfluff/sqlfluff/pull/2348) [@jpy-git](https://github.com/jpy-git)
* Configuration doc: add rule configuration section [#2291](https://github.com/sqlfluff/sqlfluff/pull/2291) [@juhoautio](https://github.com/juhoautio)
* Redshift: create model, show model & data types  [#2338](https://github.com/sqlfluff/sqlfluff/pull/2338) [@rpr-ableton](https://github.com/rpr-ableton)
* L059: Unnecessary quoted identifier [#2341](https://github.com/sqlfluff/sqlfluff/pull/2341) [@jpy-git](https://github.com/jpy-git)
* L043: Use simple replace to apply fixes [#2343](https://github.com/sqlfluff/sqlfluff/pull/2343) [@jpy-git](https://github.com/jpy-git)
* T-SQL: Add functionality to PARTITION BY clause [#2335](https://github.com/sqlfluff/sqlfluff/pull/2335) [@jpers36](https://github.com/jpers36)
* L039 casting operator postgres fix [#2334](https://github.com/sqlfluff/sqlfluff/pull/2334) [@jpy-git](https://github.com/jpy-git)
* `AnySetOf` grammar [#2326](https://github.com/sqlfluff/sqlfluff/pull/2326) [@jpy-git](https://github.com/jpy-git)
* Redshift: update CREATE TABLE AS match_grammar [#2333](https://github.com/sqlfluff/sqlfluff/pull/2333) [@rpr-ableton](https://github.com/rpr-ableton)
* Redshift CREATE EXTERNAL TABLE: TABLE PROPERTIES [#2330](https://github.com/sqlfluff/sqlfluff/pull/2330) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Flush out `ALTER TABLE`'s `tableColumnAction` grammar [#2332](https://github.com/sqlfluff/sqlfluff/pull/2332) [@wong-codaio](https://github.com/wong-codaio)
* Snowflake ALTER TABLE: Add clusteringAction [#2329](https://github.com/sqlfluff/sqlfluff/pull/2329) [@jpy-git](https://github.com/jpy-git)
* Snowflake ALTER TABLE: Add searchOptimizationAction [#2328](https://github.com/sqlfluff/sqlfluff/pull/2328) [@jpy-git](https://github.com/jpy-git)
* Fix numeric literal grammar for Postgres/MySQL/Exasol [#2324](https://github.com/sqlfluff/sqlfluff/pull/2324) [@jpy-git](https://github.com/jpy-git)
* L039: Remove spaces between comparison operators (T-SQL) [#2325](https://github.com/sqlfluff/sqlfluff/pull/2325) [@jpy-git](https://github.com/jpy-git)
* Enable setting a target of a dbt profile [#2236](https://github.com/sqlfluff/sqlfluff/pull/2236) [@yu-iskw](https://github.com/yu-iskw)
* Snowflake: Add support for column rename [#2327](https://github.com/sqlfluff/sqlfluff/pull/2327) [@wong-codaio](https://github.com/wong-codaio)
* Snowflake: Added `AlterTableStatement` specific for Snowflake [#2267](https://github.com/sqlfluff/sqlfluff/pull/2267) [@wong-codaio](https://github.com/wong-codaio)
* Full REFERENCES grammar for CREATE TABLE statement [#2315](https://github.com/sqlfluff/sqlfluff/pull/2315) [@jpy-git](https://github.com/jpy-git)
* Fix Spark numeric literals [#2317](https://github.com/sqlfluff/sqlfluff/pull/2317) [@jpy-git](https://github.com/jpy-git)
* Change type of Snowflake stage paths to fix issues with L044 [#2320](https://github.com/sqlfluff/sqlfluff/pull/2320) [@chwiese](https://github.com/chwiese)
* Add Bytes Quoted Literals to Spark dialect [#2312](https://github.com/sqlfluff/sqlfluff/pull/2312) [@jpy-git](https://github.com/jpy-git)
* Fix L044 assertion failure with delete stmt & cte [#2321](https://github.com/sqlfluff/sqlfluff/pull/2321) [@barrywhart](https://github.com/barrywhart)
* L003 should consider only *literal* leading whitespace (ignore templated) [#2304](https://github.com/sqlfluff/sqlfluff/pull/2304) [@barrywhart](https://github.com/barrywhart)
* Redshift: update reserved keywords [#2318](https://github.com/sqlfluff/sqlfluff/pull/2318) [@rpr-ableton](https://github.com/rpr-ableton)
* docs: Document how to run SQLFluff with local changes to test them [#2316](https://github.com/sqlfluff/sqlfluff/pull/2316) [@kayman-mk](https://github.com/kayman-mk)
* Update redshift unreserved keywords [#2310](https://github.com/sqlfluff/sqlfluff/pull/2310) [@jpy-git](https://github.com/jpy-git)
* Fix spark and hive quoted literals [#2311](https://github.com/sqlfluff/sqlfluff/pull/2311) [@jpy-git](https://github.com/jpy-git)
* Oracle Dialect [#2293](https://github.com/sqlfluff/sqlfluff/pull/2293) [@r0fls](https://github.com/r0fls)
* Redshift dialect: add COPY and UNLOAD statements [#2307](https://github.com/sqlfluff/sqlfluff/pull/2307) [@rpr-ableton](https://github.com/rpr-ableton)
* L052: Fix case where no preceding segments and mulitline [#2279](https://github.com/sqlfluff/sqlfluff/pull/2279) [@jpy-git](https://github.com/jpy-git)
* Update rule L049 to handle EXEC assignments [#2308](https://github.com/sqlfluff/sqlfluff/pull/2308) [@tunetheweb](https://github.com/tunetheweb)
* Remove DATE, DATETIME and TIME from BigQuery DatePart [#2283](https://github.com/sqlfluff/sqlfluff/pull/2283) [@tunetheweb](https://github.com/tunetheweb)
* Fix #1292: nocolor and verbose can work in config files [#2300](https://github.com/sqlfluff/sqlfluff/pull/2300) [@cympfh](https://github.com/cympfh)
* Allow pyproject.toml as extra_config_path [#2305](https://github.com/sqlfluff/sqlfluff/pull/2305) [@jpy-git](https://github.com/jpy-git)
* L009: Handle adding newline after trailing templated code [#2298](https://github.com/sqlfluff/sqlfluff/pull/2298) [@barrywhart](https://github.com/barrywhart)
* added missing "t" in doc for Rule_L020 [#2294](https://github.com/sqlfluff/sqlfluff/pull/2294) [@Xilorole](https://github.com/Xilorole)
* docs: Document configuration keyword for rule L054 [#2288](https://github.com/sqlfluff/sqlfluff/pull/2288) [@tomasfarias](https://github.com/tomasfarias)
* Update L009 to operate in raw, not templated space [#2285](https://github.com/sqlfluff/sqlfluff/pull/2285) [@barrywhart](https://github.com/barrywhart)
* Redshift CREATE LIBRARY statements [#2277](https://github.com/sqlfluff/sqlfluff/pull/2277) [@rpr-ableton](https://github.com/rpr-ableton)
* L025 with 'bigquery' dialect: Correctly interpret calling functions with a table as a parameter [#2278](https://github.com/sqlfluff/sqlfluff/pull/2278) [@barrywhart](https://github.com/barrywhart)
* Spark3: Coverage for `REFRESH` auxiliary statements [#2282](https://github.com/sqlfluff/sqlfluff/pull/2282) [@R7L208](https://github.com/R7L208)
* Spark3: Coverage for `USE DATABASE` statement. [#2276](https://github.com/sqlfluff/sqlfluff/pull/2276) [@R7L208](https://github.com/R7L208)
* Fix link for editing 'In The Wild' page with new base branch, `main` [#2280](https://github.com/sqlfluff/sqlfluff/pull/2280) [@barnett](https://github.com/barnett)
* Optionally allow additional configurable characters in L057 [#2274](https://github.com/sqlfluff/sqlfluff/pull/2274) [@tunetheweb](https://github.com/tunetheweb)
* L025 should look at subqueries [#2273](https://github.com/sqlfluff/sqlfluff/pull/2273) [@barrywhart](https://github.com/barrywhart)
* Add coverage for `TRUNCATE` statement in Spark3 dialect [#2272](https://github.com/sqlfluff/sqlfluff/pull/2272) [@R7L208](https://github.com/R7L208)
* Upgrade `click` version to 8.0+ to support `click.shell_completion` [#2271](https://github.com/sqlfluff/sqlfluff/pull/2271) [@wong-codaio](https://github.com/wong-codaio)
* Improve release checklist to make releases easier [#2263](https://github.com/sqlfluff/sqlfluff/pull/2263) [@tunetheweb](https://github.com/tunetheweb)

## New Contributors
* [@barnett](https://github.com/barnett) made their first contribution in [#2280](https://github.com/sqlfluff/sqlfluff/pull/2280)
* [@tomasfarias](https://github.com/tomasfarias) made their first contribution in [#2288](https://github.com/sqlfluff/sqlfluff/pull/2288)
* [@Xilorole](https://github.com/Xilorole) made their first contribution in [#2294](https://github.com/sqlfluff/sqlfluff/pull/2294)
* [@cympfh](https://github.com/cympfh) made their first contribution in [#2300](https://github.com/sqlfluff/sqlfluff/pull/2300)
* [@r0fls](https://github.com/r0fls) made their first contribution in [#2293](https://github.com/sqlfluff/sqlfluff/pull/2293)
* [@yu-iskw](https://github.com/yu-iskw) made their first contribution in [#2236](https://github.com/sqlfluff/sqlfluff/pull/2236)
* [@fdw](https://github.com/fdw) made their first contribution in [#2399](https://github.com/sqlfluff/sqlfluff/pull/2399)


## [0.9.1] - 2022-01-08

## Highlights
* Fix dbt 1.0.0 connection issue
* Fix some SQL corruption issues with templated code
* New components to simplify creating rules
* Remove support for Python 3.6

## What’s Changed
* Fix delimited identifier parsing for spark3 [#2111](https://github.com/sqlfluff/sqlfluff/pull/2111) [@mcannamela](https://github.com/mcannamela)
* Stop numeric literal from splitting valid naked identifiers. [#2114](https://github.com/sqlfluff/sqlfluff/pull/2114) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add CREATE USER/GROUP statement to Redshift dialect [#2115](https://github.com/sqlfluff/sqlfluff/pull/2115) [@jpy-git](https://github.com/jpy-git)
* Fix mypy type raise in L003 [#2127](https://github.com/sqlfluff/sqlfluff/pull/2127) [@barrywhart](https://github.com/barrywhart)
* Add ability to parse multiple GO/semicolon delimiters [#2124](https://github.com/sqlfluff/sqlfluff/pull/2124) [@jpy-git](https://github.com/jpy-git)
* Allowed array/struct values in `default` definition of `declare` [#2120](https://github.com/sqlfluff/sqlfluff/pull/2120) [@KulykDmytro](https://github.com/KulykDmytro)
* Normalise input newlines [#2128](https://github.com/sqlfluff/sqlfluff/pull/2128) [@jpy-git](https://github.com/jpy-git)
* Clean up all files using the pre-commit hook [#2123](https://github.com/sqlfluff/sqlfluff/pull/2123) [@kayman-mk](https://github.com/kayman-mk)
* Refined LintFix API [#2133](https://github.com/sqlfluff/sqlfluff/pull/2133) [@jpy-git](https://github.com/jpy-git)
* Hotfix for LintFix comparisons [#2138](https://github.com/sqlfluff/sqlfluff/pull/2138) [@jpy-git](https://github.com/jpy-git)
* Lint spaces in qualified names [#2130](https://github.com/sqlfluff/sqlfluff/pull/2130) [@jpers36](https://github.com/jpers36)
* Remove support for Python 3.6 (it's "end of life" December 23, 2021) [#2141](https://github.com/sqlfluff/sqlfluff/pull/2141) [@barrywhart](https://github.com/barrywhart)
* Fully remove python3.6 references [#2142](https://github.com/sqlfluff/sqlfluff/pull/2142) [@jpy-git](https://github.com/jpy-git)
* Fix L022 to not flag CTE column definitions [#2139](https://github.com/sqlfluff/sqlfluff/pull/2139) [@jpy-git](https://github.com/jpy-git)
* docs: set `dbt_modules` to `dbt_packages` [#2143](https://github.com/sqlfluff/sqlfluff/pull/2143) [@ciklista](https://github.com/ciklista)
* Hive: add INTERVAL syntax [#2144](https://github.com/sqlfluff/sqlfluff/pull/2144) [@juhoautio](https://github.com/juhoautio)
* Fix mypy error on python 3.7 [#2147](https://github.com/sqlfluff/sqlfluff/pull/2147) [@juhoautio](https://github.com/juhoautio)
* Update PR template to reference tox generate-fixture-yml command [#2148](https://github.com/sqlfluff/sqlfluff/pull/2148) [@jpy-git](https://github.com/jpy-git)
* Update index.rst notable changes with 0.9.0 details [#2132](https://github.com/sqlfluff/sqlfluff/pull/2132) [@jpy-git](https://github.com/jpy-git)
* Add ALTER USER and ALTER GROUP to redshift dialect [#2131](https://github.com/sqlfluff/sqlfluff/pull/2131) [@jpy-git](https://github.com/jpy-git)
* Add complete DESCRIBE grammar to Snowflake dialect [#2149](https://github.com/sqlfluff/sqlfluff/pull/2149) [@jpy-git](https://github.com/jpy-git)
* Fix bug with BigQuery UNPIVOT [#2156](https://github.com/sqlfluff/sqlfluff/pull/2156) [@tunetheweb](https://github.com/tunetheweb)
* Make L057 compatible with BigQuery [#2151](https://github.com/sqlfluff/sqlfluff/pull/2151) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Proper Indentation of ELSE IF [#2157](https://github.com/sqlfluff/sqlfluff/pull/2157) [@jpers36](https://github.com/jpers36)
* Linter Test Name Duplication [#2158](https://github.com/sqlfluff/sqlfluff/pull/2158) [@jpers36](https://github.com/jpers36)
* Add struct support for `hive` and `redshift` (L026, L028) [#2154](https://github.com/sqlfluff/sqlfluff/pull/2154) [@KulykDmytro](https://github.com/KulykDmytro)
* Postgres - Support functions prepended with _ and containing $ [#2159](https://github.com/sqlfluff/sqlfluff/pull/2159) [@jpy-git](https://github.com/jpy-git)
* T-SQL: function parsing/linting [#2155](https://github.com/sqlfluff/sqlfluff/pull/2155) [@jpers36](https://github.com/jpers36)
* T-SQL: Add THROW statement [#2163](https://github.com/sqlfluff/sqlfluff/pull/2163) [@jpers36](https://github.com/jpers36)
* Add yamllint to project [#2162](https://github.com/sqlfluff/sqlfluff/pull/2162) [@tunetheweb](https://github.com/tunetheweb)
* Fix outdated docstring in dialects_test [#2166](https://github.com/sqlfluff/sqlfluff/pull/2166) [@juhoautio](https://github.com/juhoautio)
* Minor comment fixes [#2179](https://github.com/sqlfluff/sqlfluff/pull/2179) [@juhoautio](https://github.com/juhoautio)
* L010 to apply to date_part (capitalization policy for time units) [#2167](https://github.com/sqlfluff/sqlfluff/pull/2167) [@juhoautio](https://github.com/juhoautio)
* ALTER GROUP fix to accommodate quoted objects [#2188](https://github.com/sqlfluff/sqlfluff/pull/2188) [@tdstark](https://github.com/tdstark)
* Lexer: add non-breaking spaces to whitespace [#2189](https://github.com/sqlfluff/sqlfluff/pull/2189) [@jpers36](https://github.com/jpers36)
* Grammar: Add COMMENT statement to Snowflake [#2173](https://github.com/sqlfluff/sqlfluff/pull/2173) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add DISCARD statement to Postgres dialect [#2175](https://github.com/sqlfluff/sqlfluff/pull/2175) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add UNDROP statement to Snowflake dialect [#2177](https://github.com/sqlfluff/sqlfluff/pull/2177) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add UNSET statement to Snowflake dialect [#2181](https://github.com/sqlfluff/sqlfluff/pull/2181) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add RESET statement to Postgres dialect [#2182](https://github.com/sqlfluff/sqlfluff/pull/2182) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add LOAD statement to Postgres dialect [#2183](https://github.com/sqlfluff/sqlfluff/pull/2183) [@jpy-git](https://github.com/jpy-git)
* Grammar: Fix TRUNCATE statement in Snowflake dialect [#2184](https://github.com/sqlfluff/sqlfluff/pull/2184) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add HELP statement to MySQL dialect [#2191](https://github.com/sqlfluff/sqlfluff/pull/2191) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add PURGE BINARY LOGS statement to MySQL dialect [#2193](https://github.com/sqlfluff/sqlfluff/pull/2193) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add RESET MASTER statement to MySQL dialect [#2194](https://github.com/sqlfluff/sqlfluff/pull/2194) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add RENAME TABLE statement to MySQL dialect [#2195](https://github.com/sqlfluff/sqlfluff/pull/2195) [@jpy-git](https://github.com/jpy-git)
* Grammar: Tidy up transaction statements in Snowflake dialect [#2196](https://github.com/sqlfluff/sqlfluff/pull/2196) [@jpy-git](https://github.com/jpy-git)
* Modifying Redshift USER/GROUP Statements To Use `ObjectReferenceSegment` [#2190](https://github.com/sqlfluff/sqlfluff/pull/2190) [@tdstark](https://github.com/tdstark)
* Grammar: Fix TRUNCATE statement in Postgres dialect [#2185](https://github.com/sqlfluff/sqlfluff/pull/2185) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add LISTEN, NOTIFY, and UNLISTEN statements to Postgres dialect [#2174](https://github.com/sqlfluff/sqlfluff/pull/2174) [@jpy-git](https://github.com/jpy-git)
* Grammar: Tidy up Snowflake/MySQL/HIVE USE statements [#2187](https://github.com/sqlfluff/sqlfluff/pull/2187) [@jpy-git](https://github.com/jpy-git)
* Make Snowflake keywords unreserved: account, organization, pivot [#2172](https://github.com/sqlfluff/sqlfluff/pull/2172) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add SET sql_log_bin statement to MySQL dialect [#2192](https://github.com/sqlfluff/sqlfluff/pull/2192) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add CALL statement to Snowflake dialect [#2176](https://github.com/sqlfluff/sqlfluff/pull/2176) [@jpy-git](https://github.com/jpy-git)
* L027 Fix self referring column alias edge case [#2171](https://github.com/sqlfluff/sqlfluff/pull/2171) [@jpy-git](https://github.com/jpy-git)
* T-SQL: Remove dependency on ANSI keyword lists [#2170](https://github.com/sqlfluff/sqlfluff/pull/2170) [@jpers36](https://github.com/jpers36)
* Grammar: Add Table Maintenance Statements to MySQL dialect [#2198](https://github.com/sqlfluff/sqlfluff/pull/2198) [@jpy-git](https://github.com/jpy-git)
* Adding CREATE TABLE AS to Redshift [#2205](https://github.com/sqlfluff/sqlfluff/pull/2205) [@tdstark](https://github.com/tdstark)
* T-SQL: Add support for ALTER TABLE ALTER COLUMN [#2208](https://github.com/sqlfluff/sqlfluff/pull/2208) [@jpers36](https://github.com/jpers36)
* Remove oyaml in favour of pyyaml [#2210](https://github.com/sqlfluff/sqlfluff/pull/2210) [@jpy-git](https://github.com/jpy-git)
* Support Spark `CREATE TABLE LIKE` syntax [#2207](https://github.com/sqlfluff/sqlfluff/pull/2207) [@R7L208](https://github.com/R7L208)
* Add override for linguist to include SQL in language statistics [#2214](https://github.com/sqlfluff/sqlfluff/pull/2214) [@jpy-git](https://github.com/jpy-git)
* Add type stubs for appdirs and colorama to improve mypy coverage [#2211](https://github.com/sqlfluff/sqlfluff/pull/2211) [@jpy-git](https://github.com/jpy-git)
* Remove cached-property in favour of stdlib functools implementation [#2212](https://github.com/sqlfluff/sqlfluff/pull/2212) [@jpy-git](https://github.com/jpy-git)
* Restructure CASE segment (extract WHEN and ELSE into their own segment types) [#2213](https://github.com/sqlfluff/sqlfluff/pull/2213) [@barrywhart](https://github.com/barrywhart)
* Add types-regex package for type checking [#2216](https://github.com/sqlfluff/sqlfluff/pull/2216) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Split out `CREATE VIEW` into its own segment [#2217](https://github.com/sqlfluff/sqlfluff/pull/2217) [@wong-codaio](https://github.com/wong-codaio)
* Grammar: Fix multi-character comparison operators [#2197](https://github.com/sqlfluff/sqlfluff/pull/2197) [@jpy-git](https://github.com/jpy-git)
* Snowflake: Support TOP N select clause modifier [#2222](https://github.com/sqlfluff/sqlfluff/pull/2222) [@wong-codaio](https://github.com/wong-codaio)
* Fix CLI arguments to allow for autocompletion [#2218](https://github.com/sqlfluff/sqlfluff/pull/2218) [@jpy-git](https://github.com/jpy-git)
* Simplify rule creation by adding a functional API to RuleContext [#2126](https://github.com/sqlfluff/sqlfluff/pull/2126) [@barrywhart](https://github.com/barrywhart)
* Simplify nested cases [#2223](https://github.com/sqlfluff/sqlfluff/pull/2223) [@barrywhart](https://github.com/barrywhart)
* Reword lint message for L058 per review [#2226](https://github.com/sqlfluff/sqlfluff/pull/2226) [@barrywhart](https://github.com/barrywhart)
* Update BaseRule.discard_unsafe_fixes() to avoid touching templated code [#2220](https://github.com/sqlfluff/sqlfluff/pull/2220) [@barrywhart](https://github.com/barrywhart)
* Add L059 - Capitalization on Data Types [#2227](https://github.com/sqlfluff/sqlfluff/pull/2227) [@tdstark](https://github.com/tdstark)
* T-SQL: Table valued functions [#2233](https://github.com/sqlfluff/sqlfluff/pull/2233) [@jpers36](https://github.com/jpers36)
* Don't allow fixes to COPY code from templated regions [#2231](https://github.com/sqlfluff/sqlfluff/pull/2231) [@barrywhart](https://github.com/barrywhart)
* Fix several small issues with rule docs [#2234](https://github.com/sqlfluff/sqlfluff/pull/2234) [@barrywhart](https://github.com/barrywhart)
* postgres: Add datatypes [#2121](https://github.com/sqlfluff/sqlfluff/pull/2121) [@kayman-mk](https://github.com/kayman-mk)
* Combine L059 and L010 [#2238](https://github.com/sqlfluff/sqlfluff/pull/2238) [@tdstark](https://github.com/tdstark)
* Fix L044 assertion failure: "SELECT *" with no "FROM" clause [#2239](https://github.com/sqlfluff/sqlfluff/pull/2239) [@barrywhart](https://github.com/barrywhart)
* Docs: Make Specific Rules docstring more user friendly [#2241](https://github.com/sqlfluff/sqlfluff/pull/2241) [@jpy-git](https://github.com/jpy-git)
* Fix a bug handling Jinja "{% set %}" blocks with a templated block inside [#2240](https://github.com/sqlfluff/sqlfluff/pull/2240) [@barrywhart](https://github.com/barrywhart)
* Redshift lint create external table statements [#2229](https://github.com/sqlfluff/sqlfluff/pull/2229) [@tinder-albertyue](https://github.com/tinder-albertyue)
* Update tox.ini for best practices [#2243](https://github.com/sqlfluff/sqlfluff/pull/2243) [@jpy-git](https://github.com/jpy-git)
* Docs: Make code blocks consistent [#2242](https://github.com/sqlfluff/sqlfluff/pull/2242) [@jpy-git](https://github.com/jpy-git)
* Add support for nested Jinja macros [#2246](https://github.com/sqlfluff/sqlfluff/pull/2246) [@barrywhart](https://github.com/barrywhart)
* Support `DROP` DDL statements for Spark3 [#2215](https://github.com/sqlfluff/sqlfluff/pull/2215) [@R7L208](https://github.com/R7L208)
* Docker Compose environment for SQLFluff developers [#2254](https://github.com/sqlfluff/sqlfluff/pull/2254) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Add OFFSET unreserved keyword [#2258](https://github.com/sqlfluff/sqlfluff/pull/2258) [@jpers36](https://github.com/jpers36)
* Fix connection issue in dbt 1.0.0 [#2230](https://github.com/sqlfluff/sqlfluff/pull/2230) [@NiallRees](https://github.com/NiallRees)
* Redshift CREATE SCHEMA statements [#2252](https://github.com/sqlfluff/sqlfluff/pull/2252) [@rpr-ableton](https://github.com/rpr-ableton)
* Enhance Snowflake COPY INTO [#2250](https://github.com/sqlfluff/sqlfluff/pull/2250) [@chwiese](https://github.com/chwiese)
* Coverage for 'REPAIR' Statements for Hive & Spark3 dialect [#2256](https://github.com/sqlfluff/sqlfluff/pull/2256) [@R7L208](https://github.com/R7L208)

## New Contributors
* [@mcannamela](https://github.com/mcannamela) made their first contribution in [#2111](https://github.com/sqlfluff/sqlfluff/pull/2111)
* [@ciklista](https://github.com/ciklista) made their first contribution in [#2143](https://github.com/sqlfluff/sqlfluff/pull/2143)
* [@juhoautio](https://github.com/juhoautio) made their first contribution in [#2144](https://github.com/sqlfluff/sqlfluff/pull/2144)
* [@tinder-albertyue](https://github.com/tinder-albertyue) made their first contribution in [#2229](https://github.com/sqlfluff/sqlfluff/pull/2229)
* [@rpr-ableton](https://github.com/rpr-ableton) made their first contribution in [#2252](https://github.com/sqlfluff/sqlfluff/pull/2252)

## [0.9.0] - 2021-12-13

## What’s Changed

This release brings about several great new additions including:
- dbt 1.0.0 compatibility.
- CLI and Simple API parameters to provide custom paths to config files.
- Refinement to Simple API to return parse output in JSON format rather than as an internal SQLFluff object (**BREAKING CHANGE**).
- An [Official SQLFluff Docker Image](https://hub.docker.com/r/sqlfluff/sqlfluff).
- Grammar improvements across various dialects.
- A new rule (L057) to check for non-alphanumeric values in identifiers.

There have also been many bug fixes and improvements to the CI and development processes.

## 🚀 Enhancements

* T-SQL: Reserved Keyword cleanup [#2100](https://github.com/sqlfluff/sqlfluff/pull/2100) [@jpers36](https://github.com/jpers36)
* Add wiki links to CONTRIBUTING.md [#2106](https://github.com/sqlfluff/sqlfluff/pull/2106) [@tunetheweb](https://github.com/tunetheweb)
* Add snowflake create stage and alter stage statements + RegexParser case fix [#2098](https://github.com/sqlfluff/sqlfluff/pull/2098) [@chwiese](https://github.com/chwiese)
* Allow for more value types in ALTER TABLE ALTER COLUMN SET DEFAULT statement [#2101](https://github.com/sqlfluff/sqlfluff/pull/2101) [@derickl](https://github.com/derickl)
* Grammar: Adds support for ALTER VIEW statement for Postgres dialect [#2096](https://github.com/sqlfluff/sqlfluff/pull/2096) [@derickl](https://github.com/derickl)
* Add example for using JSON output of Simple API parse function [#2099](https://github.com/sqlfluff/sqlfluff/pull/2099) [@jpy-git](https://github.com/jpy-git)
* Allow optional keywords in create table unique constraints [#2077](https://github.com/sqlfluff/sqlfluff/pull/2077) [@kayman-mk](https://github.com/kayman-mk)
* Grammar: Adds support for ALTER FUNCTION statement for Postgres dialect [#2090](https://github.com/sqlfluff/sqlfluff/pull/2090) [@derickl](https://github.com/derickl)
* Grammar: adds support for CREATE/ALTER/DROP DATABASE for Postgres dialect [#2081](https://github.com/sqlfluff/sqlfluff/pull/2081) [@derickl](https://github.com/derickl)
* Update parse method of Simple API to output JSON parse tree [#2082](https://github.com/sqlfluff/sqlfluff/pull/2082) [@jpy-git](https://github.com/jpy-git)
* T-SQL dialect: add parsing for MERGE statement [#2057](https://github.com/sqlfluff/sqlfluff/pull/2057) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
* Simple API config path [#2080](https://github.com/sqlfluff/sqlfluff/pull/2080) [@jpy-git](https://github.com/jpy-git)
* dbt 1.0.0 compatibility [#2079](https://github.com/sqlfluff/sqlfluff/pull/2079) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Parse `on delete` and `on update` clause for create table constraints [#2076](https://github.com/sqlfluff/sqlfluff/pull/2076) [@kayman-mk](https://github.com/kayman-mk)
* Pre-commit: Add hook for doc8 [#2074](https://github.com/sqlfluff/sqlfluff/pull/2074) [@jpy-git](https://github.com/jpy-git)
* Grammar: Fix typo in Alter Table parser in Postgres dialect [#2072](https://github.com/sqlfluff/sqlfluff/pull/2072) [@derickl](https://github.com/derickl)
* Grammar: Adds support for materialized views for postgres dialect [#2041](https://github.com/sqlfluff/sqlfluff/pull/2041) [@derickl](https://github.com/derickl)
* Add basic pre-commit config [#2067](https://github.com/sqlfluff/sqlfluff/pull/2067) [@jpy-git](https://github.com/jpy-git)
* CLI: Add --ignore-local-config flag [#2061](https://github.com/sqlfluff/sqlfluff/pull/2061) [@jpy-git](https://github.com/jpy-git)
* T-SQL: INSERT INTO [#2054](https://github.com/sqlfluff/sqlfluff/pull/2054) [@jpers36](https://github.com/jpers36)
* Add --disable-noqa option to CLI and config [#2043](https://github.com/sqlfluff/sqlfluff/pull/2043) [@jpy-git](https://github.com/jpy-git)
* T-SQL: TRY/CATCH [#2044](https://github.com/sqlfluff/sqlfluff/pull/2044) [@jpers36](https://github.com/jpers36)
* enabled arrays support in `declare` and `set` statements for `bigquery` dialect [#2038](https://github.com/sqlfluff/sqlfluff/pull/2038) [@KulykDmytro](https://github.com/KulykDmytro)
* L008 refactor [#2004](https://github.com/sqlfluff/sqlfluff/pull/2004) [@jpy-git](https://github.com/jpy-git)
* Support __init__.py for library_path [#1976](https://github.com/sqlfluff/sqlfluff/pull/1976) [@Tonkonozhenko](https://github.com/Tonkonozhenko)
* L052: Redefine semi-colon newline to multiline newline [#2022](https://github.com/sqlfluff/sqlfluff/pull/2022) [@jpy-git](https://github.com/jpy-git)
* Grammar: Remove hash inline comment from Postgres [#2035](https://github.com/sqlfluff/sqlfluff/pull/2035) [@jpy-git](https://github.com/jpy-git)
* `noqa` enhancement: Enable glob rule matching for inline comments [#2002](https://github.com/sqlfluff/sqlfluff/pull/2002) [@jpy-git](https://github.com/jpy-git)
* T-SQL (ASA): Allow for table identifier in DELETE clause [#2031](https://github.com/sqlfluff/sqlfluff/pull/2031) [@jpers36](https://github.com/jpers36)
* T-SQL (ASA): Fix CTAS with WITH statement [#2028](https://github.com/sqlfluff/sqlfluff/pull/2028) [@jpers36](https://github.com/jpers36)
* Grammar: Parse multiple grants [#2023](https://github.com/sqlfluff/sqlfluff/pull/2023) [@jpy-git](https://github.com/jpy-git)
* Add tsql nested block comment support and add regex package dependency [#2027](https://github.com/sqlfluff/sqlfluff/pull/2027) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add complete Snowflake datetime units [#2026](https://github.com/sqlfluff/sqlfluff/pull/2026) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add DROP POLICY statement to postgres dialect [#2024](https://github.com/sqlfluff/sqlfluff/pull/2024) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add complete datetime units to postgres dialect [#2025](https://github.com/sqlfluff/sqlfluff/pull/2025) [@jpy-git](https://github.com/jpy-git)
* Grammar: Postgres CREATE POLICY [#2021](https://github.com/sqlfluff/sqlfluff/pull/2021) [@jpy-git](https://github.com/jpy-git)
* Speed up CI [#1957](https://github.com/sqlfluff/sqlfluff/pull/1957) [@pwildenhain](https://github.com/pwildenhain)
* Add support for Snowflake create/alter SQL and js UDF [#1993](https://github.com/sqlfluff/sqlfluff/pull/1993) [@chwiese](https://github.com/chwiese)
* Add encoding CLI argument [#1994](https://github.com/sqlfluff/sqlfluff/pull/1994) [@jpy-git](https://github.com/jpy-git)
* T-SQL: Spaces allowed in comparison operators [#1965](https://github.com/sqlfluff/sqlfluff/pull/1965) [@jpers36](https://github.com/jpers36)
* Add Snowflake schema options [#1950](https://github.com/sqlfluff/sqlfluff/pull/1950) [@chwiese](https://github.com/chwiese)
* CLI/`.sqlfluff` enhancement: Rule globs [#1972](https://github.com/sqlfluff/sqlfluff/pull/1972) [@jpy-git](https://github.com/jpy-git)
* Add config CLI argument to lint, fix, and parse [#1986](https://github.com/sqlfluff/sqlfluff/pull/1986) [@jpy-git](https://github.com/jpy-git)
* Add type hints to simple API [#1951](https://github.com/sqlfluff/sqlfluff/pull/1951) [@jpy-git](https://github.com/jpy-git)
* New rule to flag special characters in identifiers [#1958](https://github.com/sqlfluff/sqlfluff/pull/1958) [@jpers36](https://github.com/jpers36)
* Allow column references in IN statement [#1971](https://github.com/sqlfluff/sqlfluff/pull/1971) [@tunetheweb](https://github.com/tunetheweb)
* Remove config.ini in favor of setup.cfg [#1966](https://github.com/sqlfluff/sqlfluff/pull/1966) [@jpy-git](https://github.com/jpy-git)
* Convert sqlfluff-templater-dbt setup.py to setup.cfg [#1963](https://github.com/sqlfluff/sqlfluff/pull/1963) [@jpy-git](https://github.com/jpy-git)
* Official Docker image: Dockerfile and Github Actions workflow [#1945](https://github.com/sqlfluff/sqlfluff/pull/1945) [@jpy-git](https://github.com/jpy-git)
* Move package metadata to setup.cfg [#1960](https://github.com/sqlfluff/sqlfluff/pull/1960) [@jpy-git](https://github.com/jpy-git)

## 🐛 Bug Fixes

* Fix tsql block comment close [#2095](https://github.com/sqlfluff/sqlfluff/pull/2095) [@jpy-git](https://github.com/jpy-git)
* Fix PlaceholderTemplater slice_type for templated code (substitutions) [#2085](https://github.com/sqlfluff/sqlfluff/pull/2085) [@barrywhart](https://github.com/barrywhart)
* Exasol: Fix UDF script syntax [#2083](https://github.com/sqlfluff/sqlfluff/pull/2083) [@sti0](https://github.com/sti0)
* Fix issues with placeholder templating docs [#2078](https://github.com/sqlfluff/sqlfluff/pull/2078) [@jpy-git](https://github.com/jpy-git)
* Update dbt templater docs to clarify that the profiles_dir setting is optional [#2070](https://github.com/sqlfluff/sqlfluff/pull/2070) [@barrywhart](https://github.com/barrywhart)
* Bug fix of L054 for Snowflake and Exasol [#2069](https://github.com/sqlfluff/sqlfluff/pull/2069) [@tunetheweb](https://github.com/tunetheweb)
* Fix L043 issue when trying to autofix functions [#2059](https://github.com/sqlfluff/sqlfluff/pull/2059) [@jpy-git](https://github.com/jpy-git)
* Add request for users dbt version in bug_report issue template [#2058](https://github.com/sqlfluff/sqlfluff/pull/2058) [@jpy-git](https://github.com/jpy-git)
* Fix parameters for Snowflake create tasks statement [#2037](https://github.com/sqlfluff/sqlfluff/pull/2037) [@chwiese](https://github.com/chwiese)
* Linguist: Include test/** in language statistics to better reflect use of SQL [#2034](https://github.com/sqlfluff/sqlfluff/pull/2034) [@jpy-git](https://github.com/jpy-git)
* L044 should handle nested CTEs [#1991](https://github.com/sqlfluff/sqlfluff/pull/1991) [@barrywhart](https://github.com/barrywhart)
* Add dbt adapter install advice to configuration documentation [#2011](https://github.com/sqlfluff/sqlfluff/pull/2011) [@jpy-git](https://github.com/jpy-git)
* Update pre-commit dbt instructions to reference separate dbt package [#2005](https://github.com/sqlfluff/sqlfluff/pull/2005) [@jpy-git](https://github.com/jpy-git)
* Fix config.get for iterable sections [#2020](https://github.com/sqlfluff/sqlfluff/pull/2020) [@jpy-git](https://github.com/jpy-git)
* Fix inline comment interactions with L052 [#2019](https://github.com/sqlfluff/sqlfluff/pull/2019) [@jpy-git](https://github.com/jpy-git)
* Make Snowflake tags DRY [#1992](https://github.com/sqlfluff/sqlfluff/pull/1992) [@chwiese](https://github.com/chwiese)
* Rename whitelist/blacklist to allowlist/denylist [#1989](https://github.com/sqlfluff/sqlfluff/pull/1989) [@jpy-git](https://github.com/jpy-git)
* Fix issue with inline ignores not respecting comment lines [#1985](https://github.com/sqlfluff/sqlfluff/pull/1985) [@jpy-git](https://github.com/jpy-git)
* Fix L009 FileSegment child + new create_before/create_after edit types [#1979](https://github.com/sqlfluff/sqlfluff/pull/1979) [@jpy-git](https://github.com/jpy-git)
* Adds extra check to L054 to avoid weird error messages [#1988](https://github.com/sqlfluff/sqlfluff/pull/1988) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Allow keywords in column reference components [#1987](https://github.com/sqlfluff/sqlfluff/pull/1987) [@tunetheweb](https://github.com/tunetheweb)
* L027: Remove unnecessary crawl in get_select_statement_info [#1974](https://github.com/sqlfluff/sqlfluff/pull/1974) [@jpy-git](https://github.com/jpy-git)
* Add __all__ attributes to __init__.py files to resolve F401 [#1949](https://github.com/sqlfluff/sqlfluff/pull/1949) [@jpy-git](https://github.com/jpy-git)
* Fix incorrect comment on L055 [#1967](https://github.com/sqlfluff/sqlfluff/pull/1967) [@jpy-git](https://github.com/jpy-git)
* Docs: fix docker hub link to public URL [#1964](https://github.com/sqlfluff/sqlfluff/pull/1964) [@kevinmarsh](https://github.com/kevinmarsh)
* Fix issue releasing dbt package: tox commands run relative to repo root [#1962](https://github.com/sqlfluff/sqlfluff/pull/1962) [@jpy-git](https://github.com/jpy-git)

## [0.8.2] - 2021-11-22

## What’s Changed

One of the biggest new features in this release is the support for SQLAlchemy and other "placeholder" templating within SQL queries. Check out [the documentation on how to set it up](https://docs.sqlfluff.com/en/latest/configuration.html#placeholder-templating).

This release also adds **seven** new rules. Get some help with your leading whitespace, semi-colon placement, inconsistent column references in `GROUP BY/ORDER BY`, and getting rid of `RIGHT JOIN`'s among other useful lints with our new rules! See our [rules documentation](https://docs.sqlfluff.com/en/stable/rules.html) for more details.

On top of those, we have made loads of grammar improvements across many dialects, improvements to the dbt templater (including issues where `sqlfluff fix` would corrupt the code :scream:), more fix routines, and lots more improvements.

## 🚀 Enhancements

* [many dialects] Implement generic placeholder templating [#1887](https://github.com/sqlfluff/sqlfluff/pull/1887) [@jacopofar](https://github.com/jacopofar)
* [many dialects] Add support for SQLAlchemy templating [#1878](https://github.com/sqlfluff/sqlfluff/pull/1878) [@jacopofar](https://github.com/jacopofar)
* Add DROP PROCEDURE statement to T-SQL [#1921](https://github.com/sqlfluff/sqlfluff/pull/1921) [@jpy-git](https://github.com/jpy-git)
* T-SQL dialect: fix index/tables creation options [#1955](https://github.com/sqlfluff/sqlfluff/pull/1955) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
* Add DROP TYPE statement to ANSI dialect [#1919](https://github.com/sqlfluff/sqlfluff/pull/1919) [@jpy-git](https://github.com/jpy-git)
* Add INSERT INTO statements to Redshift Dialect [#1896](https://github.com/sqlfluff/sqlfluff/pull/1896) [@tdstark](https://github.com/tdstark)
* Added TABLESAMPLE support to Bigquery [#1897](https://github.com/sqlfluff/sqlfluff/pull/1897) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add [LEFT] ANTI and [LEFT] SEMI joins to the Spark3 dialect [#1942](https://github.com/sqlfluff/sqlfluff/pull/1942) [@jpy-git](https://github.com/jpy-git)
* Parse UPDATE/INSERT within WITH clause [#1889](https://github.com/sqlfluff/sqlfluff/pull/1889) [@jpy-git](https://github.com/jpy-git)
* Add OVERRIDING SYSTEM/USER VALUE to insert statement in postgres dialect [#1869](https://github.com/sqlfluff/sqlfluff/pull/1869) [@jpy-git](https://github.com/jpy-git)
* Add support for DROP SCHEMA [IF EXISTS] name [ CASCADE | RESTRICT ] [#1865](https://github.com/sqlfluff/sqlfluff/pull/1865) [@gimmyxd](https://github.com/gimmyxd)
* Add CREATE TABLE Statement To Redshift [#1855](https://github.com/sqlfluff/sqlfluff/pull/1855) [@tdstark](https://github.com/tdstark)
* Add DROP TYPE statement in postgres dialect [#1870](https://github.com/sqlfluff/sqlfluff/pull/1870) [@jpy-git](https://github.com/jpy-git)
* Add SEQUENCE NAME to postgres sequence options [#1866](https://github.com/sqlfluff/sqlfluff/pull/1866) [@jpy-git](https://github.com/jpy-git)
* Added SET Statement to Postgres [#1877](https://github.com/sqlfluff/sqlfluff/pull/1877) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Allow use of quoted identifiers to ALTER TABLE OWNER TO [#1856](https://github.com/sqlfluff/sqlfluff/pull/1856) [@markpolyak](https://github.com/markpolyak)
* Updates to COPY INTO grammar in Snowflake [#1884](https://github.com/sqlfluff/sqlfluff/pull/1884) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres & T-SQL: Drop Function [#1924](https://github.com/sqlfluff/sqlfluff/pull/1924) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Add Expressions to SET syntax [#1852](https://github.com/sqlfluff/sqlfluff/pull/1852) [@tunetheweb](https://github.com/tunetheweb)
* Update DbtTemplater to use JinjaTracer [#1788](https://github.com/sqlfluff/sqlfluff/pull/1788) [@barrywhart](https://github.com/barrywhart)
* L043 refinement: Add autofix for common use of CASE to fill NULL values. [#1923](https://github.com/sqlfluff/sqlfluff/pull/1923) [@jpy-git](https://github.com/jpy-git)
* New Rule L050: No leading whitespace [#1840](https://github.com/sqlfluff/sqlfluff/pull/1840) [@jpy-git](https://github.com/jpy-git)
* L050: updating to target jinja templates [#1885](https://github.com/sqlfluff/sqlfluff/pull/1885) [@jpy-git](https://github.com/jpy-git)
* New rule L051 to forbid lone JOIN [#1879](https://github.com/sqlfluff/sqlfluff/pull/1879) [@jpy-git](https://github.com/jpy-git)
* New Rule L052: Semi colon alignment [#1902](https://github.com/sqlfluff/sqlfluff/pull/1902) [@jpy-git](https://github.com/jpy-git)
* New Rule L053: Remove outer brackets from top-level statements. [#1916](https://github.com/sqlfluff/sqlfluff/pull/1916) [@jpy-git](https://github.com/jpy-git)
* New Rule L054: Inconsistent column references in GROUP BY/ORDER BY clauses. [#1917](https://github.com/sqlfluff/sqlfluff/pull/1917) [@jpy-git](https://github.com/jpy-git)
* New Rule L055: Use LEFT JOIN instead of RIGHT JOIN. [#1931](https://github.com/sqlfluff/sqlfluff/pull/1931) [@jpy-git](https://github.com/jpy-git)
* New Rule L056: 'SP_' prefix should not be used for user-defined stored procedures [#1930](https://github.com/sqlfluff/sqlfluff/pull/1930) [@jpy-git](https://github.com/jpy-git)
* Tsql partition by multiple columns [#1906](https://github.com/sqlfluff/sqlfluff/pull/1906) [@jpers36](https://github.com/jpers36)
* Added bare functions to values clause [#1876](https://github.com/sqlfluff/sqlfluff/pull/1876) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remove unnecessary context section, from code and the docs [#1905](https://github.com/sqlfluff/sqlfluff/pull/1905) [@jacopofar](https://github.com/jacopofar)
* L036 docstring refinements [#1903](https://github.com/sqlfluff/sqlfluff/pull/1903) [@jpy-git](https://github.com/jpy-git)
* Add `exclude_rules` option for the Simple API [#1850](https://github.com/sqlfluff/sqlfluff/pull/1850) [@tunetheweb](https://github.com/tunetheweb)
* Tox improvements: Streamline development/testing environments. [#1860](https://github.com/sqlfluff/sqlfluff/pull/1860) [@jpy-git](https://github.com/jpy-git)
* Add Tox publish commands [#1853](https://github.com/sqlfluff/sqlfluff/pull/1853) [@jpy-git](https://github.com/jpy-git)
* Documentation: Change inheritance dialect example to Redshift [#1900](https://github.com/sqlfluff/sqlfluff/pull/1900) [@chwiese](https://github.com/chwiese)
* Remove failing requires.io badge [#1898](https://github.com/sqlfluff/sqlfluff/pull/1898) [@jpy-git](https://github.com/jpy-git)
* [Snowflake] Allow naked AUTOINCREMENT [#1883](https://github.com/sqlfluff/sqlfluff/pull/1883) [@gordonhart](https://github.com/gordonhart)
* Add support for curly brackets in SnowSQL ampersand variables [#1901](https://github.com/sqlfluff/sqlfluff/pull/1901) [@chwiese](https://github.com/chwiese)
* Add short form help option (-h) [#1947](https://github.com/sqlfluff/sqlfluff/pull/1947) [@jpy-git](https://github.com/jpy-git)
* Remove plaintext API key from benchmark utility [#1863](https://github.com/sqlfluff/sqlfluff/pull/1863) [@jpy-git](https://github.com/jpy-git)
* Add `skip_install` to static analysis sections of tox.ini [#1851](https://github.com/sqlfluff/sqlfluff/pull/1851) [@jpy-git](https://github.com/jpy-git)
* Move typing_extensions from `requirements_dev.txt` to `requirements.txt` [#1956](https://github.com/sqlfluff/sqlfluff/pull/1956) [@jpy-git](https://github.com/jpy-git)

## 🐛 Bug Fixes

* Fix bug where "sqlfluff fix" deletes dbt "{% snapshot %}" line [#1907](https://github.com/sqlfluff/sqlfluff/pull/1907) [@barrywhart](https://github.com/barrywhart)
* Fix subquery bug in L026 [#1948](https://github.com/sqlfluff/sqlfluff/pull/1948) [@jpy-git](https://github.com/jpy-git)
* Fix bug where L041 was confused by L016's placement of newlines in the parse tree [#1904](https://github.com/sqlfluff/sqlfluff/pull/1904) [@barrywhart](https://github.com/barrywhart)
* Fix progressbar artifacts within linter errors [#1873](https://github.com/sqlfluff/sqlfluff/pull/1873) [@adam-tokarski](https://github.com/adam-tokarski)
* Correct Snowflake warehouse sizes [#1872](https://github.com/sqlfluff/sqlfluff/pull/1872) [@jpy-git](https://github.com/jpy-git)
* Fixed Delimited() logic, added T-SQL grammar [#1894](https://github.com/sqlfluff/sqlfluff/pull/1894) [@WittierDinosaur](https://github.com/WittierDinosaur)
* L036 refinement - FROM clause interaction [#1893](https://github.com/sqlfluff/sqlfluff/pull/1893) [@jpy-git](https://github.com/jpy-git)
* Add missing chardet install in setup.py [#1928](https://github.com/sqlfluff/sqlfluff/pull/1928) [@jpy-git](https://github.com/jpy-git)
* Fix misplaced TableAliasInfo in L031 documentation [#1946](https://github.com/sqlfluff/sqlfluff/pull/1946) [@jpy-git](https://github.com/jpy-git)
* Fix broken link to external SQL style guide [#1918](https://github.com/sqlfluff/sqlfluff/pull/1918) [@kevinmarsh](https://github.com/kevinmarsh)



## [0.8.1] - 2021-11-07

## What’s Changed

Fixes missing dependency issue with 0.8.0 for `tqdm`, plus add a test to ensure this does not happen again.

## 🐛 Bug Fixes

* Fix: add tqdm to setup.py installation requirements [#1842](https://github.com/sqlfluff/sqlfluff/pull/1842) [@skykasko](https://github.com/skykasko)
* Add test to ensure pip install works [#1843](https://github.com/sqlfluff/sqlfluff/pull/1843) [@tunetheweb](https://github.com/tunetheweb)


## [0.8.0] - 2021-11-07

## What’s Changed

This release brings an improvement to the performance of the parser, a rebuild of the Jinja Templater, and a progress bar for the CLI. Lots of dialect improvements have also been done. Full list of changes below:

## 🚀 Enhancements

* Updated L009 logic to only allow a single trailing newline. [#1838](https://github.com/sqlfluff/sqlfluff/pull/1838) [@jpy-git](https://github.com/jpy-git)
* Progressbar utility [#1609](https://github.com/sqlfluff/sqlfluff/pull/1609) [@adam-tokarski](https://github.com/adam-tokarski)
* Teradata dialect: Add support for SEL form of SELECT [#1776](https://github.com/sqlfluff/sqlfluff/pull/1776) [@samlader](https://github.com/samlader)
* Added trigger support in ANSI - and extended it in Postgres [#1818](https://github.com/sqlfluff/sqlfluff/pull/1818) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Exasol: Make references more strict [#1829](https://github.com/sqlfluff/sqlfluff/pull/1829) [@sti0](https://github.com/sti0)
* Hive: INSERT statement support [#1828](https://github.com/sqlfluff/sqlfluff/pull/1828) [@mifercre](https://github.com/mifercre)
* ANSI: Add TABLESAMPLE support [#1811](https://github.com/sqlfluff/sqlfluff/pull/1811) [@CrossNox](https://github.com/CrossNox)
* T-SQL: Support trailing commas in CREATE TABLE [#1817](https://github.com/sqlfluff/sqlfluff/pull/1817) [@tommydb](https://github.com/tommydb)
* Spark3: Add CREATE VIEW support [#1813](https://github.com/sqlfluff/sqlfluff/pull/1813) [@DipeshCS](https://github.com/DipeshCS)
* BigQuery: Support PIVOT and UNPIVOT [#1794](https://github.com/sqlfluff/sqlfluff/pull/1794) [@tunetheweb](https://github.com/tunetheweb)
* L029: Optionally check quoted identifiers in addition to naked identifiers [#1775](https://github.com/sqlfluff/sqlfluff/pull/1775) [@jpers36](https://github.com/jpers36)
* Add sysdate to Redshift as a bare function [#1789](https://github.com/sqlfluff/sqlfluff/pull/1789) [@tdstark](https://github.com/tdstark)
* Robust Jinja raw/template mapping [#1678](https://github.com/sqlfluff/sqlfluff/pull/1678) [@barrywhart](https://github.com/barrywhart)
* Add CREATE TABLE AS to Postgres and Redshift [#1785](https://github.com/sqlfluff/sqlfluff/pull/1785) [@tdstark](https://github.com/tdstark)
* Improve Parser Performance By Caching Values [#1744](https://github.com/sqlfluff/sqlfluff/pull/1744) [@WittierDinosaur](https://github.com/WittierDinosaur)
* templater-dbt: Change dbt dependency to dbt-core [#1786](https://github.com/sqlfluff/sqlfluff/pull/1786) [@amardeep](https://github.com/amardeep)
* T-SQL: Create Schema definition [#1773](https://github.com/sqlfluff/sqlfluff/pull/1773) [@jpers36](https://github.com/jpers36)
* T-SQL: allow optional brackets for column default constraints [#1760](https://github.com/sqlfluff/sqlfluff/pull/1760) [@nevado](https://github.com/nevado)
* Postgres: Support parameters and identifiers prepended with _ and containing $ [#1765](https://github.com/sqlfluff/sqlfluff/pull/1765) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Added support for double precision [#1764](https://github.com/sqlfluff/sqlfluff/pull/1764) [@WittierDinosaur](https://github.com/WittierDinosaur)
* "sqlfluff fix": Write to a temporary .sql file first [#1763](https://github.com/sqlfluff/sqlfluff/pull/1763) [@barrywhart](https://github.com/barrywhart)
* Update older dbt dependency [#1756](https://github.com/sqlfluff/sqlfluff/pull/1756) [@alanmcruickshank](https://github.com/alanmcruickshank)
* T-SQL: add IDENTITY column constraint [#1757](https://github.com/sqlfluff/sqlfluff/pull/1757) [@nevado](https://github.com/nevado)
* Update CI to run under Python 3.10 [#1739](https://github.com/sqlfluff/sqlfluff/pull/1739) [@rooterkyberian](https://github.com/rooterkyberian)
* MySQL: Add drop index support [#1738](https://github.com/sqlfluff/sqlfluff/pull/1738) [@fatelei](https://github.com/fatelei)
* Snowflake dialect improvements [#1737](https://github.com/sqlfluff/sqlfluff/pull/1737) [@tunetheweb](https://github.com/tunetheweb)
* Add missing test case [#1735](https://github.com/sqlfluff/sqlfluff/pull/1735) [@tunetheweb](https://github.com/tunetheweb)

## 🐛 Bug Fixes

* Fix: Add missing init file to sqlfluff.core.templaters.slicers [#1826](https://github.com/sqlfluff/sqlfluff/pull/1826) [@CrossNox](https://github.com/CrossNox)
* Hive: Fix order of CREATE TEMPORARY EXTERNAL TABLE [#1825](https://github.com/sqlfluff/sqlfluff/pull/1825) [@mifercre](https://github.com/mifercre)
* T-SQL: add AS keyword as optional in PIVOT-UNPIVOT [#1807](https://github.com/sqlfluff/sqlfluff/pull/1807) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
* Prevent L019 plus L034 corrupting SQL [#1803](https://github.com/sqlfluff/sqlfluff/pull/1803) [@barrywhart](https://github.com/barrywhart)
* L028 fix - Allow SELECT column alias in WHERE clauses for certain dialects [#1796](https://github.com/sqlfluff/sqlfluff/pull/1796) [@tunetheweb](https://github.com/tunetheweb)
* Comment out instructions in GitHub templates [#1792](https://github.com/sqlfluff/sqlfluff/pull/1792) [@tunetheweb](https://github.com/tunetheweb)
* Fix internal error in L016 when template/whitespace-only line too long [#1795](https://github.com/sqlfluff/sqlfluff/pull/1795) [@barrywhart](https://github.com/barrywhart)
* Fix L049 to allow = NULL in SET clauses [#1791](https://github.com/sqlfluff/sqlfluff/pull/1791) [@tunetheweb](https://github.com/tunetheweb)
* Hive: Fix bug in CREATE TABLE WITH syntax [#1790](https://github.com/sqlfluff/sqlfluff/pull/1790) [@iajoiner](https://github.com/iajoiner)
* Fixed encoding error when linting to file [#1787](https://github.com/sqlfluff/sqlfluff/pull/1787) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix L012 documentation [#1782](https://github.com/sqlfluff/sqlfluff/pull/1782) [@jpers36](https://github.com/jpers36)
* T-SQL: fix quote alias [#1766](https://github.com/sqlfluff/sqlfluff/pull/1766) [@jpers36](https://github.com/jpers36)
* Fix incorrect indentation issue [#1733](https://github.com/sqlfluff/sqlfluff/pull/1733) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Fix OVER functionality for functions [#1731](https://github.com/sqlfluff/sqlfluff/pull/1731) [@jpers36](https://github.com/jpers36)

## [0.7.1] - 2021-10-22

## What’s Changed

Highlights of this release contains a lot of T-SQL dialect improvements (shout out to @jpers36 for most of these!). We also added Spark3 as a new dialect thanks to @R7L208. The complete list of changes are shown below.

## 🚀 Enhancements

* T-SQL: Add rank functions  [#1725](https://github.com/sqlfluff/sqlfluff/pull/1725) [@jpers36](https://github.com/jpers36)
* Spark3 Dialect Support [#1706](https://github.com/sqlfluff/sqlfluff/pull/1706) [@R7L208](https://github.com/R7L208)
* Postgres Array Support [#1722](https://github.com/sqlfluff/sqlfluff/pull/1722) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Hive: Add LEFT SEMI JOIN support [#1718](https://github.com/sqlfluff/sqlfluff/pull/1718) [@fatelei](https://github.com/fatelei)
* MySQL: Change and drop column in alter table [#1670](https://github.com/sqlfluff/sqlfluff/pull/1670) [@MontealegreLuis](https://github.com/MontealegreLuis)
* Added type hints to some rule files [#1616](https://github.com/sqlfluff/sqlfluff/pull/1616) [@ttomasz](https://github.com/ttomasz)
* Added Redshift to README [#1720](https://github.com/sqlfluff/sqlfluff/pull/1720) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Exasol: Fix create table statement [#1700](https://github.com/sqlfluff/sqlfluff/pull/1700) [@sti0](https://github.com/sti0)
* T-SQL: Add optional delimiter to SET [#1717](https://github.com/sqlfluff/sqlfluff/pull/1717) [@jpers36](https://github.com/jpers36)
* T-SQL: Escaped quotes [#1715](https://github.com/sqlfluff/sqlfluff/pull/1715) [@jpers36](https://github.com/jpers36)
* T-SQL: SELECT INTO [#1714](https://github.com/sqlfluff/sqlfluff/pull/1714) [@jpers36](https://github.com/jpers36)
* Postgres: Added support for psql variables [#1709](https://github.com/sqlfluff/sqlfluff/pull/1709) [@WittierDinosaur](https://github.com/WittierDinosaur)
* T-SQL: split location clause out from index clause [#1711](https://github.com/sqlfluff/sqlfluff/pull/1711) [@jpers36](https://github.com/jpers36)
* T-SQL: Override ANSI HAVING [#1707](https://github.com/sqlfluff/sqlfluff/pull/1707) [@jpers36](https://github.com/jpers36)
* T-SQL: Add UPDATE STATISTICS [#1703](https://github.com/sqlfluff/sqlfluff/pull/1703) [@jpers36](https://github.com/jpers36)
* T-SQL: CTAS Option Clause [#1705](https://github.com/sqlfluff/sqlfluff/pull/1705) [@jpers36](https://github.com/jpers36)
* T-SQL: DECLARE has optional AS [#1704](https://github.com/sqlfluff/sqlfluff/pull/1704) [@jpers36](https://github.com/jpers36)
* T-SQL: DROP STATISTICS and INDEX [#1698](https://github.com/sqlfluff/sqlfluff/pull/1698) [@jpers36](https://github.com/jpers36)
* T-SQL: CTAS select can be optionally bracketed [#1697](https://github.com/sqlfluff/sqlfluff/pull/1697) [@jpers36](https://github.com/jpers36)
* Exasol: Make function_script_terminator more strict [#1696](https://github.com/sqlfluff/sqlfluff/pull/1696) [@sti0](https://github.com/sti0)
* T-SQL distribution index location [#1695](https://github.com/sqlfluff/sqlfluff/pull/1695) [@jpers36](https://github.com/jpers36)
* T-SQL: allow for non-alphanumeric initial characters in delimited identifiers [#1693](https://github.com/sqlfluff/sqlfluff/pull/1693) [@jpers36](https://github.com/jpers36)
* T-SQL: allow for semi-colon after BEGIN in a BEGIN/END block [#1694](https://github.com/sqlfluff/sqlfluff/pull/1694) [@jpers36](https://github.com/jpers36)
* Exasol: Fix adapter script syntax [#1692](https://github.com/sqlfluff/sqlfluff/pull/1692) [@sti0](https://github.com/sti0)
* T-SQL: Basic EXECUTE functionality [#1691](https://github.com/sqlfluff/sqlfluff/pull/1691) [@jpers36](https://github.com/jpers36)
* T-SQL: Add #, @ to valid identifier characters [#1690](https://github.com/sqlfluff/sqlfluff/pull/1690) [@jpers36](https://github.com/jpers36)
* T-SQL - add support for Filegroups in table create [#1689](https://github.com/sqlfluff/sqlfluff/pull/1689) [@nevado](https://github.com/nevado)
* Exclude Exasol scripts from rule L003 [#1684](https://github.com/sqlfluff/sqlfluff/pull/1684) [@tunetheweb](https://github.com/tunetheweb)
* Added PostGIS keyword data types to Postgres [#1686](https://github.com/sqlfluff/sqlfluff/pull/1686) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Indent LIMIT values if on separate line [#1683](https://github.com/sqlfluff/sqlfluff/pull/1683) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Added support for SELECT INTO statements [#1676](https://github.com/sqlfluff/sqlfluff/pull/1676) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Allow :: casting of CASE statements [#1657](https://github.com/sqlfluff/sqlfluff/pull/1657) [@tunetheweb](https://github.com/tunetheweb)
* Add more keywords to Redhift and BigQuery to avoid errors [#1671](https://github.com/sqlfluff/sqlfluff/pull/1671) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL begin end delimiter [#1664](https://github.com/sqlfluff/sqlfluff/pull/1664) [@jpers36](https://github.com/jpers36)
* Teradata: Added date as bare function for [#1663](https://github.com/sqlfluff/sqlfluff/pull/1663) [@anzelpwj](https://github.com/anzelpwj)
* T-SQL: CREATE STATISTICS [#1662](https://github.com/sqlfluff/sqlfluff/pull/1662) [@jpers36](https://github.com/jpers36)
* T-SQL table and query hints [#1661](https://github.com/sqlfluff/sqlfluff/pull/1661) [@jpers36](https://github.com/jpers36)
* T-SQL: Allow spaces in qualified names [#1654](https://github.com/sqlfluff/sqlfluff/pull/1654) [@jpers36](https://github.com/jpers36)

## 🐛 Bug Fixes

* EXASOL: Fix typo in alter_table_statement [#1726](https://github.com/sqlfluff/sqlfluff/pull/1726) [@sti0](https://github.com/sti0)
* Fix markdown links in production.rst [#1721](https://github.com/sqlfluff/sqlfluff/pull/1721) [@asottile](https://github.com/asottile)
* Correct contributing testing information [#1702](https://github.com/sqlfluff/sqlfluff/pull/1702) [@adam-tokarski](https://github.com/adam-tokarski)
* More ORDER BY clarifications [#1681](https://github.com/sqlfluff/sqlfluff/pull/1681) [@tunetheweb](https://github.com/tunetheweb)
* Fix T-SQL L025 linter exception [#1677](https://github.com/sqlfluff/sqlfluff/pull/1677) [@tunetheweb](https://github.com/tunetheweb)
* Improve Jinja whitespace handling in rules [#1647](https://github.com/sqlfluff/sqlfluff/pull/1647) [@barrywhart](https://github.com/barrywhart)


## [0.7.0] - 2021-10-14

**BREAKING CHANGE**

This release extracts the dbt templater to a separately installable plugin
[sqlfluff-templater-dbt](https://pypi.org/project/sqlfluff-templater-dbt/).
For users who take advantage of the dbt templater see the
[updated docs on how to migrate](https://docs.sqlfluff.com/en/latest/configuration.html#installation-configuration).
It also adds the `redshift` dialect and removes the `exasol_fs` dialect which has been merged
into the `exasol` dialect.

## What’s Changed
* src/sqlfluff/core/linter: Improve ignore file processing [#1650](https://github.com/sqlfluff/sqlfluff/pull/1650) [@CyberShadow](https://github.com/CyberShadow)
* Misc documentation updates [#1644](https://github.com/sqlfluff/sqlfluff/pull/1644) [@tunetheweb](https://github.com/tunetheweb)
* Segregate dbt plugin tests [#1610](https://github.com/sqlfluff/sqlfluff/pull/1610) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Add initial Redshift support [#1641](https://github.com/sqlfluff/sqlfluff/pull/1641) [@tunetheweb](https://github.com/tunetheweb)
* Update docs for dbt templater, improve error messages when not installed. [#1583](https://github.com/sqlfluff/sqlfluff/pull/1583) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Make templaters pluggable and move the dbt templater into a plugin [#1264](https://github.com/sqlfluff/sqlfluff/pull/1264) [@alanmcruickshank](https://github.com/alanmcruickshank)

## 🚀 Enhancements

* T-SQL: CTAS delimiter [#1652](https://github.com/sqlfluff/sqlfluff/pull/1652) [@jpers36](https://github.com/jpers36)
* T-SQL: Allow for multiple variables DECLAREd in the same statement [#1651](https://github.com/sqlfluff/sqlfluff/pull/1651) [@jpers36](https://github.com/jpers36)
* T-SQL: Allow DECLARE/SET statements to parse using ExpressionStatement [#1649](https://github.com/sqlfluff/sqlfluff/pull/1649) [@jpers36](https://github.com/jpers36)
* T-SQL PRINT statement parsing [#1648](https://github.com/sqlfluff/sqlfluff/pull/1648) [@jpers36](https://github.com/jpers36)
* Better date function for tsql [#1636](https://github.com/sqlfluff/sqlfluff/pull/1636) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Allow for multiple statements in a procedure [#1637](https://github.com/sqlfluff/sqlfluff/pull/1637) [@jpers36](https://github.com/jpers36)
* T-SQL: Allow for !>, !< operators [#1640](https://github.com/sqlfluff/sqlfluff/pull/1640) [@jpers36](https://github.com/jpers36)
* T-SQL: Fix GROUP BY delimiter [#1635](https://github.com/sqlfluff/sqlfluff/pull/1635) [@jpers36](https://github.com/jpers36)
* T-SQL: Fix DROP delimiter [#1633](https://github.com/sqlfluff/sqlfluff/pull/1633) [@jpers36](https://github.com/jpers36)
* T-SQL: +RENAME statement for Azure Synapse Analytics [#1631](https://github.com/sqlfluff/sqlfluff/pull/1631) [@jpers36](https://github.com/jpers36)
* T-SQL: Fix CASTing variables [#1627](https://github.com/sqlfluff/sqlfluff/pull/1627) [@jpers36](https://github.com/jpers36)
* Snowflake: Add implementation for CREATE TASK statement [#1597](https://github.com/sqlfluff/sqlfluff/pull/1597) [#1603](https://github.com/sqlfluff/sqlfluff/pull/1603) [@JoeHut](https://github.com/JoeHut)
* Allow global config for rule testcases [#1580](https://github.com/sqlfluff/sqlfluff/pull/1580) [@sti0](https://github.com/sti0)
* Snowflake dollar sign literals [#1591](https://github.com/sqlfluff/sqlfluff/pull/1591) [@myschkyna](https://github.com/myschkyna)
* Rename test/fixtures/parser directory to test/fixtures/dialects [#1585](https://github.com/sqlfluff/sqlfluff/pull/1585) [@tunetheweb](https://github.com/tunetheweb)
* Rename keyword files [#1584](https://github.com/sqlfluff/sqlfluff/pull/1584) [@tunetheweb](https://github.com/tunetheweb)
* Add some more unreserved keywords to BigQuery [#1588](https://github.com/sqlfluff/sqlfluff/pull/1588) [@tunetheweb](https://github.com/tunetheweb)
* Increase minimum runs before coverage report is issued [#1596](https://github.com/sqlfluff/sqlfluff/pull/1596) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Support CURRENT_TIMESTAMP as a column default value [#1578](https://github.com/sqlfluff/sqlfluff/pull/1578) [@wong-codaio](https://github.com/wong-codaio)
* T-SQL temp tables [#1574](https://github.com/sqlfluff/sqlfluff/pull/1574) [@jpers36](https://github.com/jpers36)

## 🐛 Bug Fixes

* Fix NoneType exception in L031 [#1643](https://github.com/sqlfluff/sqlfluff/pull/1643) [@tunetheweb](https://github.com/tunetheweb)
* Stop rule L048 complaining if literal is followed by a semicolon [#1638](https://github.com/sqlfluff/sqlfluff/pull/1638) [@tunetheweb](https://github.com/tunetheweb)
* L031 desc updated to cover both 'from' and 'join' [#1625](https://github.com/sqlfluff/sqlfluff/pull/1625) [@nevado](https://github.com/nevado)
* Snowflake auto increments fixes [#1620](https://github.com/sqlfluff/sqlfluff/pull/1620) [@myschkyna](https://github.com/myschkyna)
* Fix DECLARE Delimitation [#1615](https://github.com/sqlfluff/sqlfluff/pull/1615) [@jpers36](https://github.com/jpers36)
* Snowflake drop column fixes [#1618](https://github.com/sqlfluff/sqlfluff/pull/1618) [@myschkyna](https://github.com/myschkyna)
* T-SQL: fix statement delimitation [#1612](https://github.com/sqlfluff/sqlfluff/pull/1612) [@jpers36](https://github.com/jpers36)
* Snowflake: Fixed data type casting not working in `SET` statement [#1604](https://github.com/sqlfluff/sqlfluff/pull/1604) [@wong-codaio](https://github.com/wong-codaio)
* Postgres dialect: Fix parse error for "on delete", "on update" clauses in column constraints [#1586](https://github.com/sqlfluff/sqlfluff/pull/1586) [@samlader](https://github.com/samlader)
* Fix AttributeError: 'NoneType' object has no attribute 'get_child' error with rule L031 [#1595](https://github.com/sqlfluff/sqlfluff/pull/1595) [@barrywhart](https://github.com/barrywhart)
* Fix zero length templated file bug. [#1577](https://github.com/sqlfluff/sqlfluff/pull/1577) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Fully remove exasol_fs dialect and bump version [#1573](https://github.com/sqlfluff/sqlfluff/pull/1573) [@alanmcruickshank](https://github.com/alanmcruickshank)


## [0.6.9] - 2021-10-08

Another dbt bugfix from 0.6.7 and 0.6.8, plus a host of dialect and syntax improvements.

## 🚀 Enhancements
* Correct and expand Snowflake CREATE TABLE syntax [#1567] [@tunetheweb](https://github.com/tunetheweb)
* Support brackets in Postgres Meta commands [#1548](https://github.com/sqlfluff/sqlfluff/pull/1548) [@tunetheweb](https://github.com/tunetheweb)
* added type hints to rule files [#1515](https://github.com/sqlfluff/sqlfluff/pull/1515) [@ttomasz](https://github.com/ttomasz)
* Update Rule L028 to handle T-SQL PIVOT columns [#1545](https://github.com/sqlfluff/sqlfluff/pull/1545) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL IF/ELSE [#1564](https://github.com/sqlfluff/sqlfluff/pull/1564) [@jpers36](https://github.com/jpers36)
* Enums for format types and colors added [#1558](https://github.com/sqlfluff/sqlfluff/pull/1558) [@adam-tokarski](https://github.com/adam-tokarski)
* Add dbt 0.21.0 to the test suite [#1566](https://github.com/sqlfluff/sqlfluff/pull/1566) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Merge EXASOL_FS dialect into EXASOL dialect [#1498](https://github.com/sqlfluff/sqlfluff/pull/1498) [@sti0](https://github.com/sti0)
* T-SQL - BEGIN/END blocks [#1553](https://github.com/sqlfluff/sqlfluff/pull/1553) [@jpers36](https://github.com/jpers36)
* Small refactor with type hints and string formatting [#1525](https://github.com/sqlfluff/sqlfluff/pull/1525) [@adam-tokarski](https://github.com/adam-tokarski)
* Add Github Preview Image [#1557](https://github.com/sqlfluff/sqlfluff/pull/1557) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Support SETOF in Postgres [#1522](https://github.com/sqlfluff/sqlfluff/pull/1522) [@tunetheweb](https://github.com/tunetheweb)
* Support Double Precision in ANSI [#1524](https://github.com/sqlfluff/sqlfluff/pull/1524) [@tunetheweb](https://github.com/tunetheweb)
* Support LATERAL joins in Postgres [#1519](https://github.com/sqlfluff/sqlfluff/pull/1519) [@adam-tokarski](https://github.com/adam-tokarski)
* Add a rule to warn on "= NULL" or "<> NULL" comparisons [#1527](https://github.com/sqlfluff/sqlfluff/pull/1527) [@barrywhart](https://github.com/barrywhart)
* Support Group and Groups as table names [#1546](https://github.com/sqlfluff/sqlfluff/pull/1546) [@tunetheweb](https://github.com/tunetheweb)
* Support more complex IN (...) expressions [#1550](https://github.com/sqlfluff/sqlfluff/pull/1550) [@tunetheweb](https://github.com/tunetheweb)
* Support CROSS APPLY and OUTER APPLY and TOP in T-SQL [#1551](https://github.com/sqlfluff/sqlfluff/pull/1551) [@tunetheweb](https://github.com/tunetheweb)
* Add support for WITHOUT ROWID to SQLite [#1531](https://github.com/sqlfluff/sqlfluff/pull/1531) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: add `CONCURRENTLY` and `FINALIZE` keywords to `DETACH PARTITION` [#1529](https://github.com/sqlfluff/sqlfluff/pull/1529) [@kevinmarsh](https://github.com/kevinmarsh)
* Better support of MySQL CREATE TABLE TIMESTAMP/DATESTAMP [#1530](https://github.com/sqlfluff/sqlfluff/pull/1530) [@tunetheweb](https://github.com/tunetheweb)
* "Found unparsable section" instead of stack trace when multiple semicolons provided [#1517](https://github.com/sqlfluff/sqlfluff/pull/1517) [@adam-tokarski](https://github.com/adam-tokarski)

## 🐛 Bug Fixes
* Fix test coverage [#1569](https://github.com/sqlfluff/sqlfluff/pull/1569) [@tunetheweb](https://github.com/tunetheweb)
* Remove lint_templated_tokens as no longer does anything [#1570](https://github.com/sqlfluff/sqlfluff/pull/1570) [@tunetheweb](https://github.com/tunetheweb)
* Fix broken block comments in exasol [#1565](https://github.com/sqlfluff/sqlfluff/pull/1565) [@sti0](https://github.com/sti0)
* Rethink sequence_files in dbt templater. [#1563](https://github.com/sqlfluff/sqlfluff/pull/1563) [@alanmcruickshank](https://github.com/alanmcruickshank)
* T-SQL: fix STRING_AGG() WITHIN GROUP clause [#1559](https://github.com/sqlfluff/sqlfluff/pull/1559) [@jpers36](https://github.com/jpers36)
* fix spelling: occurrence>occurrence [#1507](https://github.com/sqlfluff/sqlfluff/pull/1507) [@jpers36](https://github.com/jpers36)


## [0.6.8] - 2021-10-05

Fixed a DBT bug introduced in 0.6.7 - apologies!

## What’s Changed

SQLFluff can't find dbt models [#1513](https://github.com/sqlfluff/sqlfluff/pull/1513) [@barrywhart](https://github.com/barrywhart)
T-SQL: Support for unicode literals [#1511](https://github.com/sqlfluff/sqlfluff/pull/1511) [@adam-tokarski](https://github.com/adam-tokarski)


## [0.6.7] - 2021-10-04

Lots of fixes to our rules (particularly when running `sqlfluff fix`, and particularly for Jinja and DBT templates). We also have good improvements to Exasol, Snowflake, and T-SQL dialects amongst others. Plus we added Hive and SQLite as supported dialects!

## What’s Changed
* Snowflake better WAREHOUSE and CREATE (EXTERNAL) TABLES support [#1508](https://github.com/sqlfluff/sqlfluff/pull/1508) [@tunetheweb](https://github.com/tunetheweb)
* Exasol: Fix typo in `REORGANIZE` statement [#1509](https://github.com/sqlfluff/sqlfluff/pull/1509) [@sti0](https://github.com/sti0)
* Fix bug that can prevent linting ephemeral dbt models [#1496](https://github.com/sqlfluff/sqlfluff/pull/1496) [@barrywhart](https://github.com/barrywhart)
* Disable rules L026 and L028 for BigQuery by default, with option to re-enable [#1504](https://github.com/sqlfluff/sqlfluff/pull/1504) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery keywords [#1506](https://github.com/sqlfluff/sqlfluff/pull/1506) [@tunetheweb](https://github.com/tunetheweb)
* Inline --noqa not always honoured by "sqlfluff fix" [#1502](https://github.com/sqlfluff/sqlfluff/pull/1502) [@barrywhart](https://github.com/barrywhart)
* Snowflake - fix parsing of UNPIVOT [#1505](https://github.com/sqlfluff/sqlfluff/pull/1505) [@michael-the1](https://github.com/michael-the1)
* Better parsing of DATEADD function [#1486](https://github.com/sqlfluff/sqlfluff/pull/1486) [@jpers36](https://github.com/jpers36)
* Fix handling of ISNULL and NOTNULL keywords [#1483](https://github.com/sqlfluff/sqlfluff/pull/1483) [@leamingrad](https://github.com/leamingrad)
* Improved test cases names [#1501](https://github.com/sqlfluff/sqlfluff/pull/1501) [@ttomasz](https://github.com/ttomasz)
* Exasol: Fix CREATE TABLE in-/outline constraint / Adjusted DISTRIBUTE/PARTITION clause [#1491](https://github.com/sqlfluff/sqlfluff/pull/1491) [@sti0](https://github.com/sti0)
* Add support for SnowSQL variables [#1497](https://github.com/sqlfluff/sqlfluff/pull/1497) [@samlader](https://github.com/samlader)
* Ignore erroneous newline segments in L016 (e.g. Jinja for loops) [#1494](https://github.com/sqlfluff/sqlfluff/pull/1494) [@tunetheweb](https://github.com/tunetheweb)
* Indentation error on Jinja templated test case [#1444](https://github.com/sqlfluff/sqlfluff/pull/1444) [@barrywhart](https://github.com/barrywhart)
* Improve EXASOL dialect [#1484](https://github.com/sqlfluff/sqlfluff/pull/1484) [@sti0](https://github.com/sti0)
* T-SQL dialect - +support for CONVERT() special function [#1489](https://github.com/sqlfluff/sqlfluff/pull/1489) [@jpers36](https://github.com/jpers36)
* Allow Postgres column references to use `AT TIME ZONE` [#1485](https://github.com/sqlfluff/sqlfluff/pull/1485) [@leamingrad](https://github.com/leamingrad)
* T-SQL dialect - provide alternate ASA PR incorporating ASA into T-SQL [#1478](https://github.com/sqlfluff/sqlfluff/pull/1478) [@jpers36](https://github.com/jpers36)
* Modest parser performance improvement [#1475](https://github.com/sqlfluff/sqlfluff/pull/1475) [@NathanHowell](https://github.com/NathanHowell)
* Disable rule L033 for dialects that do not support it (e.g. Exasol, Postgres) [#1482](https://github.com/sqlfluff/sqlfluff/pull/1482) [@tunetheweb](https://github.com/tunetheweb)
* Adding a new BaseFileSegment class for FileSegments to inherit from [#1473](https://github.com/sqlfluff/sqlfluff/pull/1473) [@sti0](https://github.com/sti0)
* EXASOL_FS: Fix adapter script type [#1480](https://github.com/sqlfluff/sqlfluff/pull/1480) [@sti0](https://github.com/sti0)
* Dialect/tsql update - added pivot / unpivot, view support, sequence support on table creation [#1469](https://github.com/sqlfluff/sqlfluff/pull/1469) [@ericmuijs](https://github.com/ericmuijs)
* Correct typo in SQLFluff name [#1470](https://github.com/sqlfluff/sqlfluff/pull/1470) [@tunetheweb](https://github.com/tunetheweb)
* Stop L008 from adding spaces for simple SELECTs [#1461](https://github.com/sqlfluff/sqlfluff/pull/1461) [@CyberShadow](https://github.com/CyberShadow)
* Add SQLite dialect [#1453](https://github.com/sqlfluff/sqlfluff/pull/1453) [@tunetheweb](https://github.com/tunetheweb)
* Fix Windows Clause for Exasol [#1463](https://github.com/sqlfluff/sqlfluff/pull/1463) [@tunetheweb](https://github.com/tunetheweb)
* Add CHECK constraint syntax to ANSI SQL [#1451](https://github.com/sqlfluff/sqlfluff/pull/1451) [@tunetheweb](https://github.com/tunetheweb)
* Move Exasol test statements fixtures from Python to SQL files [#1449](https://github.com/sqlfluff/sqlfluff/pull/1449) [@tunetheweb](https://github.com/tunetheweb)
* fix spelling of "preceding" [#1455](https://github.com/sqlfluff/sqlfluff/pull/1455) [@jpers36](https://github.com/jpers36)
* Add NORMALIZE to Teradata dialect [#1448](https://github.com/sqlfluff/sqlfluff/pull/1448) [@tunetheweb](https://github.com/tunetheweb)
* Add @ and $ symbols to Exasol to avoid lexing errors [#1447](https://github.com/sqlfluff/sqlfluff/pull/1447) [@tunetheweb](https://github.com/tunetheweb)
* Stop fix adding then removing whitespace [#1443](https://github.com/sqlfluff/sqlfluff/pull/1443) [@barrywhart](https://github.com/barrywhart)
* Stop exception in L016 for long Jinja comments [#1440](https://github.com/sqlfluff/sqlfluff/pull/1440) [@tunetheweb](https://github.com/tunetheweb)
* Fix some issues where the SQL file is corrupted by lint "fixes" in or near Jinja loops [#1431](https://github.com/sqlfluff/sqlfluff/pull/1431) [@barrywhart](https://github.com/barrywhart)
* T-SQL: Remove Limit and NamedWindow segments as not supported in T-SQL [#1420](https://github.com/sqlfluff/sqlfluff/pull/1420) [@jpers36](https://github.com/jpers36)
* Fix runtime error (IndexError ) when linting file with jinja "if" [#1430](https://github.com/sqlfluff/sqlfluff/pull/1430) [@barrywhart](https://github.com/barrywhart)
* Add Hive dialect (#985) [@satish-ravi](https://github.com/satish-ravi)
* Further fix for L036 [#1428](https://github.com/sqlfluff/sqlfluff/pull/1428) [@tunetheweb](https://github.com/tunetheweb)
* Add default parameter to dbt "var" macro stub [#1426](https://github.com/sqlfluff/sqlfluff/pull/1426) [@CyberShadow](https://github.com/CyberShadow)


## [0.6.6] - 2021-09-20

Fixed some of our autofix rules where running `fix` sometimes made unintended changes. Added config to rules L011 and L012 to allow preferring implicit aliasing. Also further improved our Postgres support and documentation.

### What’s Changed
* Rule L036 bug fixes [#1427](https://github.com/sqlfluff/sqlfluff/pull/1427) [@tunetheweb](https://github.com/tunetheweb)
* Added support for psql meta commands to Postgres [#1423](https://github.com/sqlfluff/sqlfluff/pull/1423) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remaining line endings [#1415](https://github.com/sqlfluff/sqlfluff/pull/1415) [@tunetheweb](https://github.com/tunetheweb)
* T-SQL: Remove match possibilities for segments with no T-SQL equivalent [#1416](https://github.com/sqlfluff/sqlfluff/pull/1416) [@jpers36](https://github.com/jpers36)
* Fix generate error on test file with just a comment [#1413](https://github.com/sqlfluff/sqlfluff/pull/1413) [@tunetheweb](https://github.com/tunetheweb)
* Misc fixes to workflow files [#1412](https://github.com/sqlfluff/sqlfluff/pull/1412) [@tunetheweb](https://github.com/tunetheweb)
* Added support for escape character strings to Postgres [#1409](https://github.com/sqlfluff/sqlfluff/pull/1409) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Issue 845: L016 should compute line length prior to template expansion [#1411](https://github.com/sqlfluff/sqlfluff/pull/1411) [@barrywhart](https://github.com/barrywhart)
* Add .editorconfig config and enforce style rules [#1410](https://github.com/sqlfluff/sqlfluff/pull/1410) [@tunetheweb](https://github.com/tunetheweb)
* Allow optional enforcing of implicit aliasing of tables (L011) and columns (L012) [#1402](https://github.com/sqlfluff/sqlfluff/pull/1402) [@tunetheweb](https://github.com/tunetheweb)
* Better error messages on error [#1407](https://github.com/sqlfluff/sqlfluff/pull/1407) [@tunetheweb](https://github.com/tunetheweb)
* Add README on how to generate docs [#1403](https://github.com/sqlfluff/sqlfluff/pull/1403) [@tunetheweb](https://github.com/tunetheweb)
* Fix extra underscores in case rules (L010 and L014) [#1396](https://github.com/sqlfluff/sqlfluff/pull/1396) [@tunetheweb](https://github.com/tunetheweb)
* Remove unused deps in tox test docbuild [#1406](https://github.com/sqlfluff/sqlfluff/pull/1406) [@zhongjiajie](https://github.com/zhongjiajie)
* Prevent CodeCov commenting on coverage differences too early [#1404](https://github.com/sqlfluff/sqlfluff/pull/1404) [@tunetheweb](https://github.com/tunetheweb)
* Fix "sqlfluff fix compatible" rules indenting to much in documentation [#1405](https://github.com/sqlfluff/sqlfluff/pull/1405) [@tunetheweb](https://github.com/tunetheweb)
* Fix documentation SQL highlight error [#1393](https://github.com/sqlfluff/sqlfluff/pull/1393) [@zhongjiajie](https://github.com/zhongjiajie)
* Support TIMESTAMPTZ in TIME ZONE queries for Postgres [#1398](https://github.com/sqlfluff/sqlfluff/pull/1398) [@tunetheweb](https://github.com/tunetheweb)
* Improve datatypes: CHARACTER VARYING for ANSI, and Postgres and also TIMESTAMP AT TIME ZONE for Postgres [#1378](https://github.com/sqlfluff/sqlfluff/pull/1378) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Improve rules L003 and L019 by processing multi-line fixes in one pass. [#1391](https://github.com/sqlfluff/sqlfluff/pull/1391) [@barrywhart](https://github.com/barrywhart)
* Correct codecov badge for Docs website [#1390](https://github.com/sqlfluff/sqlfluff/pull/1390) [@tunetheweb](https://github.com/tunetheweb)
* Change fix to use non-zero exit code if unfixable [#1389](https://github.com/sqlfluff/sqlfluff/pull/1389) [@tunetheweb](https://github.com/tunetheweb)
* Bugfix, frame clauses in window functions were not working [#1381](https://github.com/sqlfluff/sqlfluff/pull/1381) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Handle template and unfixable errors when fixing stdin [#1385](https://github.com/sqlfluff/sqlfluff/pull/1385) [@nolanbconaway](https://github.com/nolanbconaway)
* CREATE, ALTER, DROP SEQUENCE support, with Postgres extensions [#1380](https://github.com/sqlfluff/sqlfluff/pull/1380) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres analyze [#1377](https://github.com/sqlfluff/sqlfluff/pull/1377) [@WittierDinosaur](https://github.com/WittierDinosaur)
* L016: "sqlfluff fix" adds too many newlines [#1382](https://github.com/sqlfluff/sqlfluff/pull/1382) [@barrywhart](https://github.com/barrywhart)
* L003 fix mixes hanging and clean indents [#1383](https://github.com/sqlfluff/sqlfluff/pull/1383) [@barrywhart](https://github.com/barrywhart)
* L034 should not fix inside "INSERT" or "CREATE TABLE AS SELECT" [#1384](https://github.com/sqlfluff/sqlfluff/pull/1384) [@barrywhart](https://github.com/barrywhart)

## [0.6.5] - 2021-09-10

### What’s Changed

This release includes initial support of Transact-SQL (T-SQL), much better Postgres and Snowflake support, improvements to our documentation, 100% coverage for Python code (with a small number of accepted exceptions), along with numerous other bug fixes and improvements.

Many thanks to all the [contributors](https://github.com/sqlfluff/sqlfluff/graphs/contributors) helping to improve SQLFluff!

### Complete list of changes

* Simplify rule L030 and fix recursion bug ([#1376](https://github.com/sqlfluff/sqlfluff/pull/1376)) ([@tunetheweb](https://github.com/tunetheweb)
* Move from CircleCI to GitHub Actions for Continuous Integration ([#1361](https://github.com/sqlfluff/sqlfluff/pull/1361)) ([@tunetheweb](https://github.com/tunetheweb)
* Postgres enhance create index ([#1375](https://github.com/sqlfluff/sqlfluff/pull/1375)) ([@WittierDinosaur](https://github.com/WittierDinosaur)
* Initial support for Transact-SQL (T-SQL) dialect ([#1313](https://github.com/sqlfluff/sqlfluff/pull/1313)) ([@ericmuijs](https://github.com/ericmuijs)
* Handle initial whitespace lines in rule L001 ([#1372](https://github.com/sqlfluff/sqlfluff/pull/1372)) ([@tunetheweb](https://github.com/tunetheweb)
* Postgres Improved DEFAULT column constraint support ([#1373](https://github.com/sqlfluff/sqlfluff/pull/1373)) ([@WittierDinosaur](https://github.com/WittierDinosaur)
* Minor grammar, spelling, and readability fixes ([#1370](https://github.com/sqlfluff/sqlfluff/pull/1370)) ([@WittierDinosaur](https://github.com/Fdawgs)
* Issues 854, 1321: Handle Jinja leading whitespace-only lines ([#1364](https://github.com/sqlfluff/sqlfluff/pull/1364)) ([@barrywhart](https://github.com/barrywhart)
* Enhanced the Postgres grammar for create table ([#1369](https://github.com/sqlfluff/sqlfluff/pull/1369)) ([@WittierDinosaur](https://github.com/WittierDinosaur)
* Added ability to Grant and Revoke Grant to multiple users ([#1367](https://github.com/sqlfluff/sqlfluff/pull/1367)) ([@WittierDinosaur](https://github.com/WittierDinosaur)
* Add BigQuery Parameter Lexing and Parsing ([#1363](https://github.com/sqlfluff/sqlfluff/pull/1363)) ([@rileyrunnoe](https://github.com/rileyrunnoe)
* Rule L030 bugfix ([#1360](https://github.com/sqlfluff/sqlfluff/pull/1360)) ([@WittierDinosaur](https://github.com/WittierDinosaur)
* Add Postgres dialect for COMMENT ON ([#1358](https://github.com/sqlfluff/sqlfluff/pull/1358)) ([@miketheman](https://github.com/miketheman)
* Allow ORDER BY and LIMIT after QUALIFY in BigQuery ([#1362](https://github.com/sqlfluff/sqlfluff/pull/1362)) ([@tunetheweb](https://github.com/tunetheweb)
* Correct CircleCI badge reference ([#1359](https://github.com/sqlfluff/sqlfluff/pull/1359)) [@miketheman](https://github.com/miketheman)
* Minor grammar corrections to documentation ([#1355](https://github.com/sqlfluff/sqlfluff/pull/1355)) [@miketheman](https://github.com/miketheman)
* Pytest coverage exceptions to get us to 100% coverage! ([#1346](https://github.com/sqlfluff/sqlfluff/pull/1346)) [@tunetheweb](https://github.com/tunetheweb)
* Greatly improved Snowflake syntax support ([#1353](https://github.com/sqlfluff/sqlfluff/pull/1353)) [@tunetheweb](https://github.com/tunetheweb)
* Postgres keyword support ([#1347](https://github.com/sqlfluff/sqlfluff/pull/1347)) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Added full support for postgres's ALTER DEFAULT PRIVILEGES. ([#1350](https://github.com/sqlfluff/sqlfluff/pull/1350)) [@creste](https://github.com/creste)
* Show all LintResult in Rule_L020 ([#1348](https://github.com/sqlfluff/sqlfluff/pull/1348)) [@zhongjiajie](https://github.com/zhongjiajie)
* Enhance error message L010 base on configure ([#1351](https://github.com/sqlfluff/sqlfluff/pull/1351)) [@zhongjiajie](https://github.com/zhongjiajie)
* Remove unused variable insert_str ([#1352](https://github.com/sqlfluff/sqlfluff/pull/1352)) [@zhongjiajie](https://github.com/zhongjiajie)
* Pytest coverage exceptions for Core code - part 1 ([#1343](https://github.com/sqlfluff/sqlfluff/pull/1343)) [@tunetheweb](https://github.com/tunetheweb)
* BigQuery: Allow Qualify Clause for UnorderedSelectStatements ([#1341](https://github.com/sqlfluff/sqlfluff/pull/1341)) [@tunetheweb](https://github.com/tunetheweb)
* Postgres "ALTER TABLE" enhancement, and timestamp bug fix ([#1338](https://github.com/sqlfluff/sqlfluff/pull/1338)) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Improve pytest coverage for non-core code ([#1319](https://github.com/sqlfluff/sqlfluff/pull/1319)) [@tunetheweb](https://github.com/tunetheweb)
* Support additional GRANTs in Postgres ([#1339](https://github.com/sqlfluff/sqlfluff/pull/1339)) [@creste](https://github.com/creste)
* Allow optional alias for BigQuery WITH OFFSET ([#1330](https://github.com/sqlfluff/sqlfluff/pull/1330)) [@tunetheweb](https://github.com/tunetheweb)
* Improve function support in Postgres dialect ([#1336](https://github.com/sqlfluff/sqlfluff/pull/1336)) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Using github star instead of watch in docs ([#1337](https://github.com/sqlfluff/sqlfluff/pull/1337)) [@zhongjiajie](https://github.com/zhongjiajie)
* Add unittest for rules docstring ([#1335](https://github.com/sqlfluff/sqlfluff/pull/1335)) [@zhongjiajie](https://github.com/zhongjiajie)
* Bugfix PR, fixes issue [#1333](https://github.com/sqlfluff/sqlfluff/issues/#1333), wherein test___main___help() defaults to your default Python installation ([#1334](https://github.com/sqlfluff/sqlfluff/pull/1334)) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Improve wording of L007 now the before/after is configurable ([#1325](https://github.com/sqlfluff/sqlfluff/pull/1325)) [@tunetheweb](https://github.com/tunetheweb)
* Fix a couple of small issues with CI jobs ([#1326](https://github.com/sqlfluff/sqlfluff/pull/1326)) [@tunetheweb](https://github.com/tunetheweb)
* Add updated sqlfluff graphics and source. ([#1315](https://github.com/sqlfluff/sqlfluff/pull/1315)) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Issue 1277: Enforce that YML test files are computer generated and not edited ([#1279](https://github.com/sqlfluff/sqlfluff/pull/1279)) [@barrywhart](https://github.com/barrywhart)
* Fix typo in README ([#1320](https://github.com/sqlfluff/sqlfluff/pull/1320)) [@tunetheweb](https://github.com/tunetheweb)
* Fix link in README ([#1316](https://github.com/sqlfluff/sqlfluff/pull/1316)) [@jmks](https://github.com/jmks)
* Update documentation to make the project more discoverable ([#1311](https://github.com/sqlfluff/sqlfluff/pull/1311)) [@tunetheweb](https://github.com/tunetheweb)
* Show latest version number on unsupported Python error message ([#1307](https://github.com/sqlfluff/sqlfluff/pull/1307)) [@zhongjiajie](https://github.com/zhongjiajie)
* Fix typo in github PR template ([#1308](https://github.com/sqlfluff/sqlfluff/pull/1308)) [@zhongjiajie](https://github.com/zhongjiajie)

## [0.6.4] - 2021-08-20

### Added
* Added support for empty WINDOWS specifications ([#1293](https://github.com/sqlfluff/sqlfluff/pull/1293)) [@matthieucan](https://github.com/matthieucan)
* Added auto release drafter ([#1287](https://github.com/sqlfluff/sqlfluff/pull/1287)) [@tunetheweb](https://github.com/tunetheweb)

### Changed
* Fix typo in the in the wild page ([#1285](https://github.com/sqlfluff/sqlfluff/pull/1285)) [@tunetheweb](https://github.com/tunetheweb)
* Fix spacing issue for BigQuery UNNEST statement for rules L003 and L025 ([#1303](https://github.com/sqlfluff/sqlfluff/pull/1303)) [@tunetheweb](https://github.com/tunetheweb)
* Update GitHub templates ([#1297](https://github.com/sqlfluff/sqlfluff/pull/1297)) [@tunetheweb](https://github.com/tunetheweb)
* Allow BigQuery UDF with triple quoted bodies to pass rule L048 ([#1300](https://github.com/sqlfluff/sqlfluff/pull/1300)) [@tunetheweb](https://github.com/tunetheweb)
* Add Parameterless Functions and more function names support to BigQuery ([#1299](https://github.com/sqlfluff/sqlfluff/pull/1299)) [@tunetheweb](https://github.com/tunetheweb)
* Add release drafter ([#1295](https://github.com/sqlfluff/sqlfluff/pull/1295)) [@tunetheweb](https://github.com/tunetheweb)
* Support empty OVER() clause in Window Specification ([#1294](https://github.com/sqlfluff/sqlfluff/pull/1294)) [@tunetheweb](https://github.com/tunetheweb)
* Fix typo on the In the Wild page ([#1285](https://github.com/sqlfluff/sqlfluff/pull/1285)) [@tunetheweb](https://github.com/tunetheweb)

## [0.6.3] - 2021-08-16
### Added

- Support for primary index name, collect stats improvement, COMMENT statement for teradata dialect [#1232](https://github.com/sqlfluff/sqlfluff/issues/1232)
- Support config for L007 to prefer end of line operators [#1261](https://github.com/sqlfluff/sqlfluff/issues/1261)
- Support for DETERMINISTIC user defined functions in BigQuery dialect [#1251](https://github.com/sqlfluff/sqlfluff/issues/1251)
- Support more identifiers in BigQuery dialect [#1253](https://github.com/sqlfluff/sqlfluff/issues/1253)
- Support function member field references in BigQuery dialect [#1255](https://github.com/sqlfluff/sqlfluff/issues/1255)
- Support alternative indentation for USING and ON clauses [#1250](https://github.com/sqlfluff/sqlfluff/issues/1250)
- Support COUNT(0) preference over COUNT(*) or COUNT(1) [#1260](https://github.com/sqlfluff/sqlfluff/issues/1260)
- Support for BigQuery "CREATE table OPTIONS ( description = 'desc' )" [#1205](https://github.com/sqlfluff/sqlfluff/issues/1205)
- Support wildcard member field references in BigQuery dialect [#1269](https://github.com/sqlfluff/sqlfluff/issues/1269)
- Support ARRAYS of STRUCTs in BigQuery dialect [#1271](https://github.com/sqlfluff/sqlfluff/issues/1271)
- Support fields of field references in BigQuery dialect [#1276](https://github.com/sqlfluff/sqlfluff/issues/1276)
- Support OFFSET and ORDINAL clauses of Array Functions in BigQuery dialect [#1171](https://github.com/sqlfluff/sqlfluff/issues/1171)
- Added check for generated YML files [#1277](https://github.com/sqlfluff/sqlfluff/issues/1277)
- Support QUALIFY to BigQuery dialect [#1242](https://github.com/sqlfluff/sqlfluff/issues/1242)

### Changed

- Fix comma removed by L019 [#939](https://github.com/sqlfluff/sqlfluff/issues/939)
- Update L019 (leading/trailng comma rule) so it doesn't run on unparsable code.
- The `--nocolor` command-line option should suppress emoji output [#1246](https://github.com/sqlfluff/sqlfluff/issues/1246)
- Added HTTP Archive to the [In The Wild page](https://docs.sqlfluff.com/en/stable/inthewild.html)

## [0.6.2] - 2021-07-22
### Added

- Support for looping statements (loop, while, repeat) and supporting statements to mysql dialect [#1180](https://github.com/sqlfluff/sqlfluff/issues/1180)

### Changed

- Added dbt 0.20.* to the default test suite.
- Updated manifest loading in dbt 0.20.* to use the new `ManifestLoader` [#1220](https://github.com/sqlfluff/sqlfluff/pull/1220)
- Handle newlines in rule list configuration in .sqlfluff [#1215](https://github.com/sqlfluff/sqlfluff/issues/1215)
- Fix looping interaction between L008 and L030 [#1207](https://github.com/sqlfluff/sqlfluff/issues/1207)

## [0.6.1] - 2021-07-16
### Added

- Linting output now supports GitHub Actions [#1190](https://github.com/sqlfluff/sqlfluff/issues/1190)
- Support for QUALIFY syntax specific to teradata dialect [#1184](https://github.com/sqlfluff/sqlfluff/issues/1184)
- Support for TRUNCATE statement [#1194](https://github.com/sqlfluff/sqlfluff/pull/1194)
- Support for prepared statement syntaxes specific to mysql dialect [#1147](https://github.com/sqlfluff/sqlfluff/issues/1147)
- Support for GET DIAGNOSTICS statement syntax specific to mysql dialect [#1148](https://github.com/sqlfluff/sqlfluff/issues/1148)
- Support for cursor syntax specific to mysql dialect [#1145](https://github.com/sqlfluff/sqlfluff/issues/1145)
- Support sequential shorthand casts [#1178](https://github.com/sqlfluff/sqlfluff/pull/1178)
- Support for select statement syntax specific to mysql dialect [#1175](https://github.com/sqlfluff/sqlfluff/issues/1175)
- Support for the CALL statement for the mysql dialect [#1144](https://github.com/sqlfluff/sqlfluff/issues/1144)
- Support for OVERLAPS predicate [#1091](https://github.com/sqlfluff/sqlfluff/issues/1091)
- Support for the CREATE/DROP PROCEDURE statement for the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901)
- Specific allowed/required syntaxes for CREATE/DROP FUNCTION within the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901)
- Support for DECLARE statement for the mysql dialect [#1140](https://github.com/sqlfluff/sqlfluff/issues/1140)
- Support for the IF-THEN-ELSEIF-ELSE syntax for the mysql dialect [#1140](https://github.com/sqlfluff/sqlfluff/issues/1140)
- Support for the DEFINER syntax for the mysql dialect [#1131](https://github.com/sqlfluff/sqlfluff/issues/1131)
- Preserve existing file encoding in the "fix" command. Partially addresses [#654](https://github.com/sqlfluff/sqlfluff/issues/654)
- Support for DECLARE and SET variable syntax for the BigQuery dialect [#1127](https://github.com/sqlfluff/sqlfluff/issues/1127)
- Support for ALTER TASK statement on Snowflake [#1211](https://github.com/sqlfluff/sqlfluff/pull/1211)

### Changed

- Fix runtime error in diff-cover plugin caused by new diff-cover release 6.1.0 [#1195](https://github.com/sqlfluff/sqlfluff/pull/1195)
- Resolved an issue with the snowflake dialect where backslash escaped single
  quoted strings led to fatal lexing errors [#1200](https://github.com/sqlfluff/sqlfluff/pull/1200)

### Contributors

- [@GitHub-Username](Link to GitHub profile) ([#PR-Number](Link to PR))
- [@dflss](https://github.com/dflss) ([#1154](https://github.com/sqlfluff/sqlfluff/pull/1154))
- [@barrywhart](https://github.com/barrywhart) ([#1177](https://github.com/sqlfluff/sqlfluff/pull/1177), [#1195](https://github.com/sqlfluff/sqlfluff/pull/1195))
- [@niallrees](https://github.com/niallrees) ([#1178](https://github.com/sqlfluff/sqlfluff/pull/1178))
- [@barnabyshearer](https://github.com/barnabyshearer) ([#1194](https://github.com/sqlfluff/sqlfluff/pull/1194))
- [@silverbullettruck2001](https://github.com/silverbullettruck2001) ([#1141](https://github.com/sqlfluff/sqlfluff/pull/1141), [#1159](https://github.com/sqlfluff/sqlfluff/pull/1159), [#1161](https://github.com/sqlfluff/sqlfluff/pull/1161), [#1176](https://github.com/sqlfluff/sqlfluff/pull/1176), [#1179](https://github.com/sqlfluff/sqlfluff/pull/1179), [#1181](https://github.com/sqlfluff/sqlfluff/pull/1181), [#1193](https://github.com/sqlfluff/sqlfluff/pull/1193), [#1203](https://github.com/sqlfluff/sqlfluff/pull/1203))

## [0.6.0] - 2021-06-06

### Added

- Respect XDG base dirs on Mac OS ([#889](https://github.com/sqlfluff/sqlfluff/issues/889)).
- Added support for additional delimiters by creating a new DelimiterSegment in the
  ANSI dialect which defaults to the semicolon, but allows it to be more intuitive
  when overridden in a specific child dialect (mysql) [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added support for the DELIMITER statement in the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added support for additional delimiters by creating a new DelimiterSegment in the
  ANSI dialect which defaults to the semicolon, but allows it to be more intuitive
  when overridden in a specific child dialect (mysql) [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added support for function as a default column value [#849](https://github.com/sqlfluff/sqlfluff/issues/849).
- Add an `--include-metas` option for parse output to show the meta
  segments in the parse tree.
- Allow CREATE FUNCTION syntax without arguments [@bolajiwahab](https://github.com/bolajiwahab) [#1063](https://github.com/sqlfluff/sqlfluff/pull/1063).
- Added support for the CREATE/DROP PROCEDURE statement for the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added specific allowed/required syntaxes for CREATE/DROP FUNCTION within the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Now possible to run sqlfluff commands outside the project root when using the dbt templater.

### Changed

- Renamed --parallel CLI argument to --processes to be more accurate.
- L034 now ignores select statements which contain macros.
- L034 now ignores select statements part of a set expression, most commonly a union.
- Fix bug [#1082](https://github.com/sqlfluff/sqlfluff/issues/1082), adding
  support for BigQuery `select as struct '1' as bb, 2 as aa` syntax.
- Rationalisation of the placement of meta segments within templated
  queries to support more reliable indentation. This includes prioritising
  _longer_ invariant sections first and then dropping any shorter ones
  which then are relatively out of place.
- Additional logging within the lexer and templater engines.
- Allow meta segments to parse within `Delimited` grammars which otherwise
  don't allow gaps. This is facilitated through an optional argument to
  `trim_non_code_segments`.
- Fix bug [#1079](https://github.com/sqlfluff/sqlfluff/issues/1079), addressing
  issues with L025 and L026 with BigQuery column references involving `STRUCT`.
- [#1080](https://github.com/sqlfluff/sqlfluff/issues/1080) Add
  SET SCHEMA and DROP SCHEMA support to ANSI dialect.

### Contributors

- [@bolajiwahab](https://github.com/bolajiwahab) ([#1063](https://github.com/sqlfluff/sqlfluff/pull/1063))
- [@silverbullettruck2001](https://github.com/silverbullettruck2001) ([#1126](https://github.com/sqlfluff/sqlfluff/pull/1126), [#1099](https://github.com/sqlfluff/sqlfluff/pull/1099), [#1141](https://github.com/sqlfluff/sqlfluff/pull/1141))

## [0.6.0a2] - 2021-05-27

### Changed

- Better exception handling for the simple parsing API (`sqlfluff.parse`)
  which now raises an exception which holds all potential parsing issues
  and prints nicely with more than one issue.
- Fix bug [#1037](https://github.com/sqlfluff/sqlfluff/issues/1037), in which fix
  logging had been sent to stdout when reading data from stdin.
- Add a little bit of fun on CLI exit 🎉!
- Disabled models in the dbt templater are now skipped entirely rather than
  returning an untemplated file.
- Add a changelog check to SQLFluff continuous integration.
- Fix bug [#1083](https://github.com/sqlfluff/sqlfluff/issues/1083), adding
  support for BigQuery named function arguments, used with functions such as
  [ST_GEOGFROMGEOJSON()](https://cloud.google.com/bigquery/docs/reference/standard-sql/geography_functions#st_geogfromgeojson)
- Update documentation links to sqlfluff-online.

## [0.6.0a1] - 2021-05-15

### Added

- Lint and fix parallelism using `--parallel` CLI argument
- Fix [1051](https://github.com/sqlfluff/sqlfluff/issues/1051), adding support
  for bitwise operators `&`, `|`, `^`, `<<`, `>>`

## [0.5.6] - 2021-05-14

- Bugfix release for an issue in `L016` introduced in `0.5.4`.
- Fix for `L016` issue where `DISTINCT` keywords were mangled during
  fixing [#1024](https://github.com/sqlfluff/sqlfluff/issues/1024).

## [0.5.5] - 2021-05-13

- Bugfix release for an off-by-one error introduced in L016 as part of `0.5.4`.

## [0.5.4] - 2021-05-12

### Added

- Parsing of Postgres dollar quoted literals.
- Parsing of Postgres filter grammar.
- Parsing of "ALTER DEFAULT PRIVILEGES" Postgres statement.
- Parsing of Postgres non-explicit role granting and function execution.
- Early failing on fatal dbt templater fails.

### Changed

- Big rewrite of the lexer, segments and position markers for simplicity
  and to support future parallelism work.
- Fix to L036 which previously mangled whitespace.

## [0.5.3] - 2021-05-04

### Added

- [`L009`](https://docs.sqlfluff.com/en/stable/rules.html#sqlfluff.core.rules.Rule_L009) can now be enforced when `templater = dbt`.
- Parsing of `EXPLAIN`, `USE` statements.
- Parsing of `ALTER TABLE x RENAME TO y` syntax.
- Parsing of `ALTER SESSION` in snowflake.
- Parsing of numeric literals with exponents.
- Added rule codes to diff_cover output.

### Changed

- Fix `templater = dbt` L009 bug [#861](https://github.com/sqlfluff/sqlfluff/issues/861) where:
  - `sqlfluff lint` would incorrectly always return `L009 | Files must end with a trailing newline.`
  - `sqlfluff fix` would remove trailing newlines when `exclude_rules = L009`.
- Fix bug with BigQuery comparison operators.
- Fix recursion bug with L045.
- Fix tuple index bug with L016.
- Fix mange coalecse bug with L043.
- Fix Jinja templating error with _UnboundLocalError_.
- Improve array parsing.
- Simplify bracket parsing.
- Speed up L010 with caching capitalisation policy.
- Output of `sqlfluff dialects` is now sorted.
- Handle disabled `dbt` models.

## [0.5.2] - 2021-04-11

### Changed

- Fix false positive in L045 when CTE used in WHERE clause ([#944](https://github.com/sqlfluff/sqlfluff/issues/944))
- Logging and readout now includes more detail and a notification of dbt compilation.
- Fix bug in L048 which flagged adjoining commas as failures.
- Fix bug in L019 with inline comments.
- Fix bug in L036 with multiple newlines.
- Skip disabled dbt models. ([#931](https://github.com/sqlfluff/sqlfluff/issues/931)).
- Support "USE" statement in ANSI ([#902](https://github.com/sqlfluff/sqlfluff/issues/902)).
- Parse explain statement ([#893](https://github.com/sqlfluff/sqlfluff/issues/893)).

## [0.5.1] - 2021-04-09

### Changed

- Parsing improvements around optional brackets.
- Better parsing of set operators (like `UNION`) and how they interact with
  `ORDER BY` clauses.
- Support for comparison operators like `~`.
- Fix parsing of snowflake `SAMPLE` syntax.
- Fix recursion issues in L044.
- `SPACE` keyword now has no special meaning in the postgres dialect.

## [0.5.0] - 2021-04-05

### Added

- `pascal` (PascalCase) `capitalisation_policy` option for L014 (unquoted identifiers)
- `only_aliases` configuration option for L014 (unquoted identifiers)
- Dialects now have more advanced dependency options to allow less repetition
  between related dialects. The methods `get_segment` and `get_grammar` can be
  used on unexpanded grammars to access elements of the parent grammars.
  The `copy` method on grammars can be used to copy with alterations.
- Rule L046 to line whitespace within jinja tags.
- Enable and Disable syntax for [ignoring violations from ranges of lines](https://docs.sqlfluff.com/en/latest/configuration.html#ignoring-line-ranges).

### Changed

- Renamed the BaseCrawler class to BaseRule. This is the base class for all
  rules. This is a breaking change for any custom rules that have been added
  via plugins or by forking the SQLFluff repo.
- Renamed `sqlfluff.rules()` to `sqlfluff.list_rules()` and `sqlfluff.dialects()`
  to `sqlfluff.list_dialects()` due to naming conflicts with the now separate
  `sqlfluff.dialects` module.
- Extracted dialect definitions from the `sqlfluff.core` module so that each
  dialect is better isolated from each other. This also allows more focused
  testing and the potential for dialect plugins in future. Dialects are now
  only imported as needed at runtime. All dialects should now be accessed
  using the selector methods in `sqlfluff.core.dialects` rather than importing
  from `sqlfluff.dialects` directly.
- Add support for `ALTER USER` commands in Snowflake dialect.
- Added describe statement to ANSI dialect
- Renamed `capitalisation_policy` to `extended_capitalisation_policy` for L014
  to reflect the fact that it now accepts more options (`pascal`) than regular
  `capitalisation_policy` still used by L010 and others.
- Replaced `only_aliases` config with `unquoted_identifiers_policy` and added
  it to rule L014 in addition to L029.
- Parse structure of `FROM` clauses to better represent nested joins and table
  functions.
- Parse structure of expressions to avoid unnecessary nesting and overly
  recursive method calls.

## [0.4.1] - 2021-02-25

### Added

- Initial architecture for rule plugins to allow custom rules. This
  initial release should be considered _beta_ until the release of
  0.5.0.
- Add tests for dbt 0.19.0.
- General increased parsing coverage.
- Added some missing Postgres syntax elements.
- Added some basic introspection API elements to output what dialects
  and rules are available for use within the API.

### Changed

- Fix several Snowflake parsing bugs.
- Refactor from clause to handle flattens after joins.
- Fix .get_table_references() in Snowflake dialect.
- Macros defined within the .sqlfluff config will take precedence over the macros defined in the
  path that is defined with config value `sqlfluff:templater:jinja:load_macros_from_path`.
- Fix Snowflake indent parsing.
- Fixed incorrect parsing of syntax-like elements in comments.
- Altered parsing of `NULL` keywords, so parse as Literals where
  appropriate.
- Fixed bug in expression parsing leading to recursion errors.

## [0.4.0] - 2021-02-14

### Added

- Public API to enable people to import `sqlfluff` as a python module
  and call `parse`, `lint` and `fix` within their own projects. See
  [the docs](https://docs.sqlfluff.com/en/latest/api.html) for more
  information. ([#501](https://github.com/sqlfluff/sqlfluff/pull/501))
- The ability to use `dbt` as a templating engine directly allowing
  richer and more accurate linting around `dbt` macros (and packages
  related to `dbt`). For more info see [the docs](https://docs.sqlfluff.com/en/latest/configuration.html#dbt-project-configuration). ([#508](https://github.com/sqlfluff/sqlfluff/pull/508))
- Support for modulo (`%`) operator. ([#447](https://github.com/sqlfluff/sqlfluff/pull/447))
- A limit in the internal fix routines to catch any infinite loops. ([#494](https://github.com/sqlfluff/sqlfluff/pull/494))
- Added the `.is_type()` method on segments to more intelligently
  deal with type matching in rules when inheritance is at play.
- Added the ability for the user to add their own rules when interacting
  with the `Linter` directly using `user_rules`.
- Added L034 'Fields should be stated before aggregates / window functions' per
  [dbt coding convenventions](https://github.com/fishtown-analytics/corp/blob/master/dbt_coding_conventions.md#sql-style-guide.) ([#495](https://github.com/sqlfluff/sqlfluff/pull/495))
- Templating tags, such as `{{ variables }}`, `{# comments #}` and
  `{% loops %}` (in jinja) now have placeholders in the parsed
  structure. Rule L003 (indentation), also now respects these
  placeholders so that their indentation is linted accordingly.
  For loop or block tags, they also generate an `Indent` and
  `Dedent` tag accordingly (which can be enabled or disabled)
  with a configuration value so that indentation around these
  functions can be linted accordingly. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- MyPy type linting into a large proportion of the core library. ([#526](https://github.com/sqlfluff/sqlfluff/pull/526), [#580](https://github.com/sqlfluff/sqlfluff/pull/580))
- Config values specific to a file can now be defined using a comment
  line starting with `-- sqlfluff:`. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- Added documentation for `--noqa:` use in rules. ([#552](https://github.com/sqlfluff/sqlfluff/pull/552))
- Added `pre-commit` hooks for `lint` and `fix`. ([#576](https://github.com/sqlfluff/sqlfluff/pull/576))
- Added a fix routine for Rule L019 (comma placement). ([#575](https://github.com/sqlfluff/sqlfluff/pull/575))
- Added Rule L031 to enforce "avoid using alias in the `FROM`/`JOIN` clauses" from the `dbt` coding conventions. ([#473](https://github.com/sqlfluff/sqlfluff/pull/473), [#479](https://github.com/sqlfluff/sqlfluff/pull/479))
- Added Rule L032 to enforce "do not use `USING`" from the `dbt` coding conventions. ([#487](https://github.com/sqlfluff/sqlfluff/pull/487))
- Added Rule L033 to enforce "prefer `UNION ALL` to `UNION *`" from the `dbt` coding conventions. ([#489](https://github.com/sqlfluff/sqlfluff/pull/489))
- Added Rule L034 to enforce "fields should be stated before aggregate/window functions" from the `dbt` coding conventions. ([#495](https://github.com/sqlfluff/sqlfluff/pull/495))
- Added Rule L038 to forbid (or require) trailing commas in select clauses. ([#362](https://github.com/sqlfluff/sqlfluff/pull/752))
- Added Rule L039 to lint unnecessary whitespace between elements. ([#502](https://github.com/sqlfluff/sqlfluff/pull/753))
- Added a fix routine for L015. ([#732](https://github.com/sqlfluff/sqlfluff/pull/732))
- Added a fix routine for L025. ([#404](https://github.com/sqlfluff/sqlfluff/pull/741))
- Adopted the `black` coding style. ([#485](https://github.com/sqlfluff/sqlfluff/pull/485))
- Added validation and documentation for rule configuration options. ([#462](https://github.com/sqlfluff/sqlfluff/pull/462))
- Added documentation for which rules are fixable. ([#594](https://github.com/sqlfluff/sqlfluff/pull/594))
- Added `EPOCH` keyword for postgres dialect. ([#522](https://github.com/sqlfluff/sqlfluff/pull/522))
- Added column index identifier in snowflake dialect. ([#458](https://github.com/sqlfluff/sqlfluff/pull/458))
- Added `USE` statement to the snowflake dialect. ([#537](https://github.com/sqlfluff/sqlfluff/pull/537))
- Added `CODE_OF_CONDUCT` to the project. ([#471](https://github.com/sqlfluff/sqlfluff/pull/471))
- Added `ISNULL` and `NOTNULL` keywords to ansi dialect. ([#441](https://github.com/sqlfluff/sqlfluff/pull/441))
- Added support for python 3.9. ([#482](https://github.com/sqlfluff/sqlfluff/pull/482))
- Added `requirements_dev.txt` for local testing/linting. ([#500](https://github.com/sqlfluff/sqlfluff/pull/500))
- Added CLI option `--disregard-sqlfluffignores` to allow direct linting of files in the `.sqlfluffignore`. ([#486](https://github.com/sqlfluff/sqlfluff/pull/486))
- Added `dbt` `incremental` macro. ([#363](https://github.com/sqlfluff/sqlfluff/pull/363))
- Added links to cockroachlabs expression grammars in ansi dialect. ([#592](https://github.com/sqlfluff/sqlfluff/pull/592))
- Added favicon to the docs website. ([#589](https://github.com/sqlfluff/sqlfluff/pull/589))
- Added `CREATE FUNCTION` syntax for postgres and for bigquery. ([#325](https://github.com/sqlfluff/sqlfluff/pull/325))
- Added `CREATE INDEX` and `DROP INDEX` for mysql. ([#740](https://github.com/sqlfluff/sqlfluff/pull/748))
- Added `IGNORE NULLS`, `RESPECT NULLS`, `GENERATE_DATE_ARRAY` and
  `GENERATE_TIMESTAMP_ARRAY` for bigquery. (
  [#667](https://github.com/sqlfluff/sqlfluff/pull/727),
  [#527](https://github.com/sqlfluff/sqlfluff/pull/726))
- Added `CREATE` and `CREATE ... CLONE` for snowflake. ([#539](https://github.com/sqlfluff/sqlfluff/pull/670))
- Added support for EXASOL. ([#684](https://github.com/sqlfluff/sqlfluff/pull/684))

### Changed

- Fixed parsing of semi-structured objects in the snowflake of dialects
  with whitespace gaps. [#634](https://github.com/sqlfluff/sqlfluff/issues/635)
- Handle internal errors elegantly, reporting the stacktrace and the
  error-surfacing file. [#632](https://github.com/sqlfluff/sqlfluff/pull/632)
- Improve message for when an automatic fix is not available for L004. [#633](https://github.com/sqlfluff/sqlfluff/issues/633)
- Linting errors raised on templated sections are now ignored by default
  and added a configuration value to show them. ([#713](https://github.com/sqlfluff/sqlfluff/pull/745))
- Big refactor of logging internally. `Linter` is now decoupled from
  logging so that it can be imported directly by subprojects without
  needing to worry about weird output or without the log handing getting
  in the way of your project. ([#460](https://github.com/sqlfluff/sqlfluff/pull/460))
- Linting errors in the final file are now reported with their position
  in the source file rather than in the templated file. This means
  when using sqlfluff as a plugabble library within an IDE, the
  references match the file which is being edited. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- Created new Github Organisation (https://github.com/sqlfluff) and
  migrated from https://github.com/alanmcruickshank/sqlfluff to
  https://github.com/sqlfluff/sqlfluff. ([#444](https://github.com/sqlfluff/sqlfluff/issues/444))
- Changed the handling of `*` and `a.b.*` expressions to have their
  own expressions. Any dependencies on this structure downstream
  will be broken. This also fixes the linting of both kinds of expressions
  with regard to L013 and L025. ([#454](https://github.com/sqlfluff/sqlfluff/pull/454))
- Refactor of L022 to handle poorly formatted CTEs better. ([#494](https://github.com/sqlfluff/sqlfluff/pull/494))
- Restriction of L017 to only fix when it would delete whitespace or
  newlines. ([#598](https://github.com/sqlfluff/sqlfluff/pull/756))
- Added a configuration value to L016 to optionally ignore lines
  containing only comments. ([#299](https://github.com/sqlfluff/sqlfluff/pull/751))
- Internally added an `EphemeralSegment` to aid with parsing efficiency
  without altering the end structure of the query. ([#491](https://github.com/sqlfluff/sqlfluff/pull/491))
- Split `ObjectReference` into `ColumnReference` and `TableReference`
  for more useful API access to the underlying structure. ([#504](https://github.com/sqlfluff/sqlfluff/pull/504))
- `KeywordSegment` and the new `SymbolSegment` both now inherit
  from `_ProtoKeywordSegment` which allows symbols to match in a very
  similar way to keywords without later appearing with the `type` of
  `keyword`. ([#504](https://github.com/sqlfluff/sqlfluff/pull/504))
- Introduced the `Parser` class to parse a lexed query rather than
  relying on users to instantiate a `FileSegment` directly. As a result
  the `FileSegment` has been moved from the core parser directly into
  the dialects. Users can refer to it via the `get_root_segment()`
  method of a dialect. ([#510](https://github.com/sqlfluff/sqlfluff/pull/510))
- Several performance improvements through removing unused functionality,
  sensible caching and optimising loops within functions. ([#526](https://github.com/sqlfluff/sqlfluff/pull/526))
- Split up rule tests into separate `yml` files. ([#553](https://github.com/sqlfluff/sqlfluff/pull/553))
- Allow escaped quotes in strings. ([#557](https://github.com/sqlfluff/sqlfluff/pull/557))
- Fixed `ESCAPE` parsing in `LIKE` clause. ([#566](https://github.com/sqlfluff/sqlfluff/pull/566))
- Fixed parsing of complex `BETWEEN` statements. ([#498](https://github.com/sqlfluff/sqlfluff/pull/498))
- Fixed BigQuery `EXCEPT` clause parsing. ([#472](https://github.com/sqlfluff/sqlfluff/pull/472))
- Fixed Rule L022 to respect leading comma configuration. ([#455](https://github.com/sqlfluff/sqlfluff/pull/455))
- Improved instructions on adding a virtual environment in the `README`. ([#457](https://github.com/sqlfluff/sqlfluff/pull/457))
- Improved documentation for passing CLI defaults in `.sqlfluff`. ([#452](https://github.com/sqlfluff/sqlfluff/pull/452))
- Fix bug with templated blocks + `capitalisation_policy = lower`. ([#477](https://github.com/sqlfluff/sqlfluff/pull/477))
- Fix array accessors in snowflake dialect. ([#442](https://github.com/sqlfluff/sqlfluff/pull/442))
- Color `logging` warnings red. ([#497](https://github.com/sqlfluff/sqlfluff/pull/497))
- Allow whitespace before a shorthand cast. ([#544](https://github.com/sqlfluff/sqlfluff/pull/544))
- Silenced warnings when fixing from stdin. ([#522](https://github.com/sqlfluff/sqlfluff/pull/522))
- Allow an underscore as the first char in a semi structured element key. ([#596](https://github.com/sqlfluff/sqlfluff/pull/596))
- Fix PostFunctionGrammar in the Snowflake dialect which was causing strange behaviour in L012. ([#619](https://github.com/sqlfluff/sqlfluff/pull/619/files))
- `Bracketed` segment now obtains its brackets directly from the dialect
  using a set named `bracket_pairs`. This now enables better configuration
  of brackets between dialects. ([#325](https://github.com/sqlfluff/sqlfluff/pull/325))

### Removed

- Dropped support for python 3.5. ([#482](https://github.com/sqlfluff/sqlfluff/pull/482))
- From the CLI, the `--no-safety` option has been removed, the default
  is now that all enabled rules will be fixed. ([#583](https://github.com/sqlfluff/sqlfluff/pull/583))
- Removed `BaseSegment.grammar`, `BaseSegment._match_grammar()` and
  `BaseSegment._parse_grammar()` instead preferring references directly
  to `BaseSegment.match_grammar` and `BaseSegment.parse_grammar`. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed `EmptySegmentGrammar` and replaced with better non-code handling
  in the `FileSegment` itself. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Remove the `ContainsOnly` grammar as it remained only as an anti-pattern. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed the `expected_string()` functionality from grammars and segments ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
  as it was poorly supported.
- Removed `BaseSegment.as_optional()` as now this functionality happens
  mostly in grammars (including `Ref`). ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed `ColumnExpressionSegment` in favour of `ColumnReference`. ([#512](https://github.com/sqlfluff/sqlfluff/pull/512))
- Removed the `LambdaSegment` feature, instead replacing with an internal
  to the grammar module called `NonCodeMatcher`. ([#512](https://github.com/sqlfluff/sqlfluff/pull/512))
- Case sensitivity as a feature for segment matching has been removed as
  not required for existing dialects. ([#517](https://github.com/sqlfluff/sqlfluff/pull/517))
- Dependency on `difflib` or `cdifflib`, by relying on source mapping
  instead to apply fixes. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))

## [0.3.6] - 2020-09-24

### Added

- `sqlfluff dialects` command to get a readout of available
  dialects [+ associated docs].
- More helpful error messages when trying to run in Python2.
- Window functions now parse with `IGNORE`/`RESPECT` `NULLS`.
- Parsing of `current_timestamp` and similar functions. Thanks [@dmateusp](https://github.com/dmateusp).
- Snowflake `QUALIFY` clause.

### Changed

- Respect user config directories. Thanks [@sethwoodworth](https://github.com/sethwoodworth).
- Fix incorrect reporting of L013 with `*`. Thanks [@dmateusp](https://github.com/dmateusp).
- Fix incorrect reporting of L027 with column aliases. Thanks [@pwildenhain](https://github.com/pwildenhain).
- Simplification of application of fixes and correction of
  a case where fixes could be depleted. Thanks [@NiallRees](https://github.com/NiallRees).
- Fix functions with a similar structure to `SUBSTRING`.
- Refactor BigQuery `REPLACE` and `EXCEPT` clauses.
- Bigquery date parts corrected.
- Snowflake array accessors.
- Psotgres `NOTNULL` and `ISNULL`.
- Bugfix in snowflake for keywords used in semistructured
  queries.
- Nested `WITH` statements now parse.
- Performance improvements in the `fix` command.
- Numeric literals starting with a decimal now parse.
- Refactor the jinja templater.

## [0.3.5] - 2020-08-03

### Added

- Patterns and Anti-patterns in documentation. Thanks [@flpezet](https://github.com/flpezet).
- Functions in `GROUP BY`. Thanks [@flpezet](https://github.com/flpezet).

### Changed

- Deep bugfixes in the parser to handle simple matching better for a few
  edge cases. Also added some logging deeper in the parser.
- Added in the `SelectableGrammar` and some related segments to make it
  easier to refer to _select-like_ things in other grammars.
- Fixes to `CASE` statement parsing. Thanks [@azhard](https://github.com/azhard).
- Fix to snowflake `SAMPLE` implementation. Thanks [@rkm3](https://github.com/rkm3).
- Numerous docs fixes. Thanks [@SimonStJG](https://github.com/SimonStJG),
  [@flpezet](https://github.com/flpezet), [@s-pace](https://github.com/s-pace),
  [@nolanbconaway](https://github.com/nolanbconaway).

## [0.3.4] - 2020-05-13

### Changed

- Implementation of the bigquery `CREATE MODEL` syntax. Thanks [@barrywhart](https://github.com/barrywhart).
- Bugfixes for:
  - Edge cases for L006
  - False alarms on L025
  - `ORDER BY x NULLS FIRST|LAST`
  - `FOR` keyword in bigquery `SYSTEM_TIME` syntax.

## [0.3.3] - 2020-05-11

### Added

- Added the `--nofail` option to `parse` and `lint` commands to assist
  rollout.
- Added the `--version` option to complement the `version` option already
  available on the cli.
- Parsing for `ALTER TABLE`.
- Warning for unset dialects when getting parsing errors.
- Configurable line lengths for output.

## [0.3.2] - 2020-05-08

### Added

- Support for the Teradata dialect. Thanks [@Katzmann1983](https://github.com/Katzmann1983)!
- A much more detailed getting started guide in the docs.
- For the `parse` command, added the `--profiler` and `--bench` options
  to help debugging performance issues.
- Support for the `do` command in the jinja templater.
- Proper parsing of the concatenate operator (`||`).
- Proper indent handling of closing brackets.
- Logging and benchmarking of parse performance as part of the CI pipeline.
- Parsing of object references with defaults like `my_db..my_table`.
- Support for the `INTERVAL '4 days'` style interval expression.
- Configurable trailing or leading comma linting.
- Configurable indentation for `JOIN` clauses.
- Rules now have their own logging interface to improve debugging ability.
- Snowflake and Postgres dialects.
- Support for a `.sqlfluffignore` file to ignore certain paths.
- More generic interfaces for managing keywords in dialects, including `set`
  interfaces for managing and creating keywords and the `Ref.keyword()` method
  to refer to them, and the ability to refer directly to keyword names in
  most grammars using strings directly. Includes `SegmentGenerator` objects
  to bind dialect objects at runtime from sets. Thanks [@Katzmann1983](https://github.com/Katzmann1983)!
- Rule `L029` for using unreserved keywords as variable names.
- The jinja templater now allows macros loaded from files, and the
  hydration of variables ending in `_path` in the config files.
- JSON operators and the `DISTINCT ON ()` syntax for the postgres dialect.

### Changed

- Refactor of whitespace and non-code handling so that segments are
  less greedy and default to not holding whitespace on ends. This allows
  more consistent linting rule application.
- Change config file reading to _case-sensitive_ to support case
  sensitivity in jinja templating.
- Non-string values (including lists) now function in the python
  and jinja templating libraries.
- Validation of the match results of grammars has been reduced. In
  production cases the validation will still be done, but only on
  _parse_ and not on _match_.
- At low verbosities, python level logging is also reduced.
- Some matcher rules in the parser can now be classified as _simple_
  which allows them to shortcut some of the matching routines.
- Yaml output now double quotes values with newlines or tab characters.
- Better handling on hanging and closing indents when linting rule L003.
- More capable handline of multi-line comments so that indentation
  and line length parsing works. This involves some deep changes to the
  lexer.
- Getting violations from the linter now automatically takes into account
  of ignore rules and filters.
- Several bugfixes, including catching potential infinite regress during
  fixing of files, if one fix would re-introduce a problem with another.
- Behaviour of the `Bracketed` grammar has been changed to treat its
  content as a `Sequence` rather than a `OneOf`.
- Move to `SandboxedEnvironment` rather than `Environment` for jinja
  templating for security.
- Improve reporting of templating issues, especially for the jinja templater
  so that missing variables are rendered as blanks, but still reported as
  templating violations.

## [0.3.1] - 2020-02-17

### Added

- Support for `a.b.*` on top of `a.*` in select target expressions.

## [0.3.0] - 2020-02-15

### Changed

- Deprecated python 2.7 and python 3.4 which are now both past
  their maintenance horizon. The 0.2.x branch will remain available
  for continued development for these versions.
- Rule L003 is now significantly smarter in linting indentation
  with support for hanging indents and comparison to the most
  recent line which doesn't have an error. The old (more simple)
  functionality of directly checking whether an indent was a
  multiple of a preset value has been removed.
- Fixed the "inconsistent" bug in L010. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Updated logging of parsing and lexing errors to have more useful
  error codes.
- Changed parsing of expressions to favour functions over identifiers
  to [fix the expression bug](https://github.com/sqlfluff/sqlfluff/issues/96).
- Fixed the "inconsistent" bug in L010. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Moved where the `SELECT` keyword is parsed within a select statement,
  so that it belongs as part of the newly renamed `select_clause` (renamed
  from previously `select_target_group`).
- Clarified handling of the `type` and `name` properties of the BaseSegment
  class and its children. `name` should be specific to a particular kind
  of segment, and `type` should express a wider group. Handling of the
  `newline`, `whitespace` and `comma` segments has been updated so that
  we use the `type` property for most use cases rather than `name`.

### Added

- _Meta segments_ for indicating where things can be present in the parsed
  tree. This is mostly illustrated using the `Indent` and `Dedent` segments
  used for indicating the position of theoretical indents in the structure.
  Several helper functions have been added across the codebase to handle
  this increase in the kinds of segments which might be encountered by
  various grammars.
- Rule L016 has been added to lint long lines. In the `fix` phase of this
  rule, there is enough logic to try and reconstruct a sensible place for
  line breaks as re-flow the query. This will likely need further work
  and may still encounter places where it doesn't fix all errors but should
  be able to deal with the majority of simple cases.
- BigQuery dialect, initially just for appropriate quoting.
- Added parsing of DDL statements such as `COMMIT`, `DROP`, `GRANT`, `REVOKE`
  and `ROLLBACK`. Thanks [@barrywhart](https://github.com/barrywhart).
- `--format` option to the `parse` command that allows a yaml output. This
  is mostly to make test writing easier in the development process but
  might also be useful for other things.
- Parsing of set operations like `UNION`.
- Support for the `diff-cover` tool. Thanks [@barrywhart](https://github.com/barrywhart).
- Enabled the `fix` command while using `stdin`. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Rule to detect incorrect use of `DISTINCT`. Thanks [@barrywhart](https://github.com/barrywhart).
- Security fixes from DeepCover. Thanks [@sanketsaurav](https://github.com/sanketsaurav).
- Automatic fix testing, to help support the newer more complicated rules.
- Interval literals
- Support for the `source` macro from dbt. Thanks [@Dandandan](https://github.com/Dandandan)
- Support for functions with spaces between the function name and the brackets
  and a linting rule `L017` to catch this.
- Efficiency cache for faster pruning of the parse tree.
- Parsing of array notation as using in BigQuery and Postgres.
- Enable the `ignore` parameter on linting and fixing commands to ignore
  particular kinds of violations.

## [0.2.4] - 2019-12-06

### Added

- A `--code-only` option to the `parse` command to spit out a more
  simplified output with only the code elements.
- Rules can now optionally override the description of the violation
  and pass that back via the `LintingResult`.

### Changed

- Bugfix, correct missing files in `setup.py` `install_requires` section.
- Better parsing of the _not equal_ operator.
- Added more exclusions to identifier reserved words to fix cross joins.
- At verbosity levels 2 or above, the root config is printed and then any
  diffs to that for specific files are also printed.
- Linting and parsing of directories now reports files in alphabetical
  order. Thanks [@barrywhart](https://github.com/barrywhart).
- Better python 2.7 stability. Thanks [@barrywhart](https://github.com/barrywhart).
- Fixing parsing of `IN`/`NOT IN` and `IS`/`IS NOT`.

## [0.2.3] - 2019-12-02

### Changed

- Bugfix, default config not included.

## [0.2.2] - 2019-12-02

### Changed

- Tweak rule L005 to report more sensibly with newlines.
- Rework testing of rules to be more modular.
- Fix a config file bug if no root config file was present for some
  values. Thanks [@barrywhart](https://github.com/barrywhart).
- Lexing rules are now part of the dialect rather than a
  global so that they can be overridden by other dialects
  when we get to that stage.

## [0.2.0] - 2019-12-01

### Added

- Templating support (jinja2, python or raw).
  - Variables + Macros.
  - The `fix` command is also sensitive to fixing over templates
    and will skip certain fixes if it feels that it's conflicted.
- Config file support, including specifying context for the templater.
- Documentation via Sphinx and readthedocs.
  - Including a guide on the role of SQL in the real world.
    Assisted by [@barrywhart](https://github.com/barrywhart).
- Documentation LINTING (given we're a linting project) introduced in CI.
- Reimplemented L006 & L007 which lint whitespace around operators.
- Ability to configure rule behaviour directly from the config file.
- Implemented L010 to lint capitalisation of keywords.
- Allow casting in the parser using the `::` operator.
- Implemented `GROUP BY`and `LIMIT`.
- Added `ORDER BY` using indexes and expressions.
- Added parsing of `CASE` statements.
- Support for window/aggregate functions.
- Added linting and parsing of alias expressions.

### Changed

- Fixed a bug which could cause potential infinite recursion in configuration
- Changed how negative literals are handled, so that they're now a compound segment
  rather than being identified at the lexing stage. This is to allow the parser
  to resolve the potential ambiguity.
- Restructure of rule definitions to be more streamlined and also enable
  autodocumentation. This includes a more complete `RuleSet` class which now
  holds the filtering code.
- Corrected logging in fix mode not to duplicate the reporting of errors.
- Now allows insert statements with a nested `with` clause.
- Fixed verbose logging during parsing.
- Allow the `Bracketed` grammar to optionally match empty brackets using
  the optional keyword.

## [0.1.5] - 2019-11-11

### Added

- Python 3.8 Support!

### Changed

- Moved some of the responsibility for formatted logging into the linter to mean that we can
  log progressively in large directories.
- Fixed a bug in the grammar where one of the return values was messed up.

## [0.1.4] - 2019-11-10

### Added

- Added a `--exclude-rules` argument to most of the commands to allow rule users
  to exclude specific subset of rules, by [@sumitkumar1209](https://github.com/sumitkumar1209)
- Added lexing for `!=`, `~` and `::`.
- Added a new common segment: `LambdaSegment` which allows matching based on arbitrary
  functions which can be applied to segments.
- Recursive Expressions for both arithmetic and functions, based heavily off the grammar
  provided by the guys at [CockroachDB](https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt).
- An `Anything` grammar, useful in matching rather than in parsing to match anything.

### Changed

- Complete rewrite of the bracket counting functions, using some centralised class methods
  on the `BaseGrammar` class to support common matching features across multiple grammars.
  In particular this affects the `Delimited` grammar which is now _much simpler_ but does
  also require _slightly_ more liberal use of terminators to match effectively.
- Rather than passing around multiple variables during parsing and matching, there is now
  a `ParseContext` object which contains things like the dialect and various depths. This
  simplifies the parsing and matching code significantly.
- Bracket referencing is now done from the dialect directly, rather than in individual
  Grammars (except the `Bracketed` grammar, which still implements it directly). This
  takes out some originally duplicated code.
- Corrected the parsing of ordering keywords in and `ORDER BY` clause.

### Removed

- Removed the `bracket_sensitive_forward_match` method from the `BaseGrammar`. It was ugly
  and not flexible enough. It's been replaced by a suite of methods as described above.

## [0.1.3] - 2019-10-30

### Changed

- Tweak to the L001 rule so that it doesn't crash the whole thing.

## [0.1.2] - 2019-10-30

### Changed

- Fixed the errors raised by the lexer.

## [0.1.1] - 2019-10-30

### Changed

- Fixed which modules from sqlfluff are installed in the setup.py. This affects
  the `version` command.

## [0.1.0] - 2019-10-29

### Changed

- _Big Rewrite - some loss in functionality might be apparent compared
  to pre-0.1.0. Please submit any major problems as issues on github_
- Changed unicode handling for better escape codes in python 2.
  Thanks [@mrshu](https://github.com/mrshu)
- BIG rewrite of the parser, completely new architecture. This introduces
  breaking changes and some loss of functionality while we catch up.
  - In particular, matches now return partial matches to speed up parsing.
  - The `Delimited` matcher has had a significant re-write with a major
    speedup and broken the dependency on `Sequence`.
  - Rewrite of `StartsWith` and `Sequence` to use partial matches properly.
  - Different treatment of numeric literals.
  - Both `Bracketed` and `Delimited` respect bracket counting.
  - MASSIVE rewrite of `Bracketed`.
- Grammars now have timers.
- Joins properly parsing,
- Rewrite of logging to selectively output commands at different levels
  of verbosity. This uses the `verbosity_logger` method.
- Added a command line `sqlfluff parse` option which runs just the parsing step
  of the process to better understand how a file is being parsed. This also
  has options to configure how deep we recurse.
- Complete Re-write of the rules section, implementing new `crawlers` which
  implement the linting rules. Now with inbuilt fixers in them.
- Old rules removed and re implemented so we now have parity with the old rule sets.
- Moved to using Ref mostly within the core grammar so that we can have recursion.
- Used recursion to do a first implementation of arithmetic parsing. Including a test for it.
- Moved the main grammar into a separate dialect and renamed source and test files accordingly.
- Moved to file-based tests for the ansi dialect to make it easier to test using the tool directly.
- As part of file tests - expected outcomes are now encoded in yaml to make it easier to write new tests.
- Vastly improved readability and debugging potential of the \_match logging.
- Added support for windows line endings in the lexer.

## [0.0.7] - 2018-11-19

### Added

- Added a `sqlfluff fix` as a command to implement auto-fixing of linting
  errors. For now only `L001` is implemented as a rule that can fix things.
- Added a `rules` command to introspect the available rules.
- Updated the cli table function to use the `testwrap` library and also
  deal a lot better with longer values.
- Added a `--rules` argument to most of the commands to allow rule users
  to focus their search on a specific subset of rules.

### Changed

- Refactor the cli tests to use the click CliRunner. Much faster

## [0.0.6] - 2018-11-15

### Added

- Number matching

### Changed

- Fixed operator parsing and linting (including allowing the exception of `(*)`)

## [0.0.5] - 2018-11-15

### Added

- Much better documentation including the DOCS.md

### Changed

- Fixed comma parsing and linting

## [0.0.4] - 2018-11-14

### Added

- Added operator regexes
- Added a priority for matchers to resolve some ambiguity
- Added tests for operator regexes
- Added ability to initialise the memory in rules

## [0.0.3] - 2018-11-14

### Added

- Refactor of rules to allow rules with memory
- Adding comma linting rules (correcting the single character matchers)
- Adding mixed indentation linting rules
- Integration with CircleCI, CodeCov and lots of badges

### Changed

- Changed import of version information to fix bug with importing config.ini
- Added basic violations/file reporting for some verbosities
- Refactor of rules to simplify definition
- Refactor of color cli output to make it more reusable

## [0.0.2] - 2018-11-09

### Added

- Longer project description
- Proper exit codes
- colorama for colored output

### Changed

- Significant CLI changes
- Much improved output from CLI

## [0.0.1] - 2018-11-07

### Added

- Initial Commit! - VERY ALPHA
- Restructure into [package layout](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure)
- Adding Tox and Pytest so that they work
