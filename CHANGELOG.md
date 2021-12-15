# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Note: Changes are now automatically tracked in [GitHub](https://github.com/sqlfluff/sqlfluff/releases) and will be copied in here on each release (please remember to update the issues and contributors to links!). There is no need to manually edit this file going forward.
-->

## [0.9.0] - 2021-12-13

## What’s Changed

This release brings about several great new additions including:
- dbt 1.0.0 compatibility.
- CLI and Simple API paramaters to provide custom paths to config files.
- Refinement to Simple API to return parse output in JSON format rather than as an internal SQLFluff object (**BREAKING CHANGE**).
- An [Official SQLFluff Docker Image](https://hub.docker.com/r/sqlfluff/sqlfluff).
- Grammar improvements across various dialects.
- A new rule (L057) to check for non-alphanumeric values in identifiers.

There have also been many bug fixes and improvements to the CI and development processes.

## 🚀 Enhancements

* TSQL: Reserved Keyword cleanup [#2100](https://github.com/sqlfluff/sqlfluff/pull/2100) [@jpers36](https://github.com/jpers36)
* Add wiki links to CONTRIBUTING.md [#2106](https://github.com/sqlfluff/sqlfluff/pull/2106) [@tunetheweb](https://github.com/tunetheweb)
* Add snowflake create stage and alter stage statements + RegexParser case fix [#2098](https://github.com/sqlfluff/sqlfluff/pull/2098) [@chwiese](https://github.com/chwiese)
* Allow for more value types in ALTER TABLE ALTER COLUMN SET DEFAULT statement [#2101](https://github.com/sqlfluff/sqlfluff/pull/2101) [@derickl](https://github.com/derickl)
* Grammar: Adds support for ALTER VIEW statement for Postgres dialect [#2096](https://github.com/sqlfluff/sqlfluff/pull/2096) [@derickl](https://github.com/derickl)
* Add example for using JSON output of Simple API parse function [#2099](https://github.com/sqlfluff/sqlfluff/pull/2099) [@jpy-git](https://github.com/jpy-git)
* Allow optional keywords in create table unique constraints [#2077](https://github.com/sqlfluff/sqlfluff/pull/2077) [@kayman-mk](https://github.com/kayman-mk)
* Grammar: Adds support for ALTER FUNCTION statement for Postgres dialect [#2090](https://github.com/sqlfluff/sqlfluff/pull/2090) [@derickl](https://github.com/derickl)
* Grammar: adds support for CREATE/ALTER/DROP DATABASE for Postgres dialect [#2081](https://github.com/sqlfluff/sqlfluff/pull/2081) [@derickl](https://github.com/derickl)
* Update parse method of Simple API to output JSON parse tree [#2082](https://github.com/sqlfluff/sqlfluff/pull/2082) [@jpy-git](https://github.com/jpy-git)
* TSQL dialect: add parsing for MERGE statement [#2057](https://github.com/sqlfluff/sqlfluff/pull/2057) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
* Simple API config path [#2080](https://github.com/sqlfluff/sqlfluff/pull/2080) [@jpy-git](https://github.com/jpy-git)
* dbt 1.0.0 compatability [#2079](https://github.com/sqlfluff/sqlfluff/pull/2079) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Parse `on delete` and `on update` clause for create table constraints [#2076](https://github.com/sqlfluff/sqlfluff/pull/2076) [@kayman-mk](https://github.com/kayman-mk)
* Pre-commit: Add hook for doc8 [#2074](https://github.com/sqlfluff/sqlfluff/pull/2074) [@jpy-git](https://github.com/jpy-git)
* Grammar: Fix typo in Alter Table parser in Postgres dialect [#2072](https://github.com/sqlfluff/sqlfluff/pull/2072) [@derickl](https://github.com/derickl)
* Grammar: Adds support for materialized views for postgres dialect [#2041](https://github.com/sqlfluff/sqlfluff/pull/2041) [@derickl](https://github.com/derickl)
* Add basic pre-commit config [#2067](https://github.com/sqlfluff/sqlfluff/pull/2067) [@jpy-git](https://github.com/jpy-git)
* CLI: Add --ignore-local-config flag [#2061](https://github.com/sqlfluff/sqlfluff/pull/2061) [@jpy-git](https://github.com/jpy-git)
* TSQL: INSERT INTO [#2054](https://github.com/sqlfluff/sqlfluff/pull/2054) [@jpers36](https://github.com/jpers36)
* Add --disable-noqa option to CLI and config [#2043](https://github.com/sqlfluff/sqlfluff/pull/2043) [@jpy-git](https://github.com/jpy-git)
* TSQL: TRY/CATCH [#2044](https://github.com/sqlfluff/sqlfluff/pull/2044) [@jpers36](https://github.com/jpers36)
* enabled arrays support in `declare` and `set` statements for `bigquery` dialect [#2038](https://github.com/sqlfluff/sqlfluff/pull/2038) [@KulykDmytro](https://github.com/KulykDmytro)
* L008 refactor [#2004](https://github.com/sqlfluff/sqlfluff/pull/2004) [@jpy-git](https://github.com/jpy-git)
* Support __init__.py for library_path [#1976](https://github.com/sqlfluff/sqlfluff/pull/1976) [@Tonkonozhenko](https://github.com/Tonkonozhenko)
* L052: Redefine semi-colon newline to multiline newline [#2022](https://github.com/sqlfluff/sqlfluff/pull/2022) [@jpy-git](https://github.com/jpy-git)
* Grammar: Remove hash inline comment from Postgres [#2035](https://github.com/sqlfluff/sqlfluff/pull/2035) [@jpy-git](https://github.com/jpy-git)
* `noqa` enhancement: Enable glob rule matching for inline comments [#2002](https://github.com/sqlfluff/sqlfluff/pull/2002) [@jpy-git](https://github.com/jpy-git)
* TSQL (ASA): Allow for table identifier in DELETE clause [#2031](https://github.com/sqlfluff/sqlfluff/pull/2031) [@jpers36](https://github.com/jpers36)
* TSQL (ASA): Fix CTAS with WITH statement [#2028](https://github.com/sqlfluff/sqlfluff/pull/2028) [@jpers36](https://github.com/jpers36)
* Grammar: Parse multiple grants [#2023](https://github.com/sqlfluff/sqlfluff/pull/2023) [@jpy-git](https://github.com/jpy-git)
* Add tsql nested block comment support and add regex package dependency [#2027](https://github.com/sqlfluff/sqlfluff/pull/2027) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add complete Snowflake datetime units [#2026](https://github.com/sqlfluff/sqlfluff/pull/2026) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add DROP POLICY statement to postgres dialect [#2024](https://github.com/sqlfluff/sqlfluff/pull/2024) [@jpy-git](https://github.com/jpy-git)
* Grammar: Add complete datetime units to postgres dialect [#2025](https://github.com/sqlfluff/sqlfluff/pull/2025) [@jpy-git](https://github.com/jpy-git)
* Grammar: Postgres CREATE POLICY [#2021](https://github.com/sqlfluff/sqlfluff/pull/2021) [@jpy-git](https://github.com/jpy-git)
* Speed up CI [#1957](https://github.com/sqlfluff/sqlfluff/pull/1957) [@pwildenhain](https://github.com/pwildenhain)
* Add support for Snowflake create/alter SQL and js UDF [#1993](https://github.com/sqlfluff/sqlfluff/pull/1993) [@chwiese](https://github.com/chwiese)
* Add encoding CLI argument [#1994](https://github.com/sqlfluff/sqlfluff/pull/1994) [@jpy-git](https://github.com/jpy-git)
* TSQL: Spaces allowed in comparison operators [#1965](https://github.com/sqlfluff/sqlfluff/pull/1965) [@jpers36](https://github.com/jpers36)
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
* L027: Remove unnessary crawl in get_select_statement_info [#1974](https://github.com/sqlfluff/sqlfluff/pull/1974) [@jpy-git](https://github.com/jpy-git)
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
* TSQL dialect: fix index/tables creation options [#1955](https://github.com/sqlfluff/sqlfluff/pull/1955) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
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
* Fixed Delimited() logic, added TSQL grammar [#1894](https://github.com/sqlfluff/sqlfluff/pull/1894) [@WittierDinosaur](https://github.com/WittierDinosaur)
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
* TSQL: Support trailing commas in CREATE TABLE [#1817](https://github.com/sqlfluff/sqlfluff/pull/1817) [@tommydb](https://github.com/tommydb)
* Spark3: Add CREATE VIEW support [#1813](https://github.com/sqlfluff/sqlfluff/pull/1813) [@DipeshCS](https://github.com/DipeshCS)
* BigQuery: Support PIVOT and UNPIVOT [#1794](https://github.com/sqlfluff/sqlfluff/pull/1794) [@tunetheweb](https://github.com/tunetheweb)
* L029: Optionally check quoted identifiers in addition to naked identifiers [#1775](https://github.com/sqlfluff/sqlfluff/pull/1775) [@jpers36](https://github.com/jpers36)
* Add sysdate to Redshift as a bare function [#1789](https://github.com/sqlfluff/sqlfluff/pull/1789) [@tdstark](https://github.com/tdstark)
* Robust Jinja raw/template mapping [#1678](https://github.com/sqlfluff/sqlfluff/pull/1678) [@barrywhart](https://github.com/barrywhart)
* Add CREATE TABLE AS to Postgres and Redshift [#1785](https://github.com/sqlfluff/sqlfluff/pull/1785) [@tdstark](https://github.com/tdstark)
* Improve Parser Performance By Caching Values [#1744](https://github.com/sqlfluff/sqlfluff/pull/1744) [@WittierDinosaur](https://github.com/WittierDinosaur)
* templater-dbt: Change dbt dependency to dbt-core [#1786](https://github.com/sqlfluff/sqlfluff/pull/1786) [@amardeep](https://github.com/amardeep)
* TSQL: Create Schema definition [#1773](https://github.com/sqlfluff/sqlfluff/pull/1773) [@jpers36](https://github.com/jpers36)
* TSQL: allow optional brackets for column default constraints [#1760](https://github.com/sqlfluff/sqlfluff/pull/1760) [@nevado](https://github.com/nevado)
* Postgres: Support parameters and identifiers prepended with _ and containing $ [#1765](https://github.com/sqlfluff/sqlfluff/pull/1765) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Postgres: Added support for double precision [#1764](https://github.com/sqlfluff/sqlfluff/pull/1764) [@WittierDinosaur](https://github.com/WittierDinosaur)
* "sqlfluff fix": Write to a temporary .sql file first [#1763](https://github.com/sqlfluff/sqlfluff/pull/1763) [@barrywhart](https://github.com/barrywhart)
* Update older dbt dependency [#1756](https://github.com/sqlfluff/sqlfluff/pull/1756) [@alanmcruickshank](https://github.com/alanmcruickshank)
* TSQL: add IDENTITY column constraint [#1757](https://github.com/sqlfluff/sqlfluff/pull/1757) [@nevado](https://github.com/nevado)
* Update CI to run under Python 3.10 [#1739](https://github.com/sqlfluff/sqlfluff/pull/1739) [@rooterkyberian](https://github.com/rooterkyberian)
* MySQL: Add drop index support [#1738](https://github.com/sqlfluff/sqlfluff/pull/1738) [@fatelei](https://github.com/fatelei)
* Snowflake dialect improvements [#1737](https://github.com/sqlfluff/sqlfluff/pull/1737) [@tunetheweb](https://github.com/tunetheweb)
* Add missing test case [#1735](https://github.com/sqlfluff/sqlfluff/pull/1735) [@tunetheweb](https://github.com/tunetheweb)

## 🐛 Bug Fixes

* Fix: Add missing init file to sqlfluff.core.templaters.slicers [#1826](https://github.com/sqlfluff/sqlfluff/pull/1826) [@CrossNox](https://github.com/CrossNox)
* Hive: Fix order of CREATE TEMPORARY EXTERNAL TABLE [#1825](https://github.com/sqlfluff/sqlfluff/pull/1825) [@mifercre](https://github.com/mifercre)
* TSQL: add AS keyword as optional in PIVOT-UNPIVOT [#1807](https://github.com/sqlfluff/sqlfluff/pull/1807) [@tkachenkomaria244](https://github.com/tkachenkomaria244)
* Prevent L019 plus L034 corrupting SQL [#1803](https://github.com/sqlfluff/sqlfluff/pull/1803) [@barrywhart](https://github.com/barrywhart)
* L028 fix - Allow SELECT column alias in WHERE clauses for certain dialects [#1796](https://github.com/sqlfluff/sqlfluff/pull/1796) [@tunetheweb](https://github.com/tunetheweb)
* Comment out instructions in GitHub templates [#1792](https://github.com/sqlfluff/sqlfluff/pull/1792) [@tunetheweb](https://github.com/tunetheweb)
* Fix internal error in L016 when template/whitespace-only line too long [#1795](https://github.com/sqlfluff/sqlfluff/pull/1795) [@barrywhart](https://github.com/barrywhart)
* Fix L049 to allow = NULL in SET clauses [#1791](https://github.com/sqlfluff/sqlfluff/pull/1791) [@tunetheweb](https://github.com/tunetheweb)
* Hive: Fix bug in CREATE TABLE WITH syntax [#1790](https://github.com/sqlfluff/sqlfluff/pull/1790) [@iajoiner](https://github.com/iajoiner)
* Fixed encoding error when linting to file [#1787](https://github.com/sqlfluff/sqlfluff/pull/1787) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Fix L012 documentation [#1782](https://github.com/sqlfluff/sqlfluff/pull/1782) [@jpers36](https://github.com/jpers36)
* TSQL: fix quote alias [#1766](https://github.com/sqlfluff/sqlfluff/pull/1766) [@jpers36](https://github.com/jpers36)
* Fix incorrect indentation issue [#1733](https://github.com/sqlfluff/sqlfluff/pull/1733) [@tunetheweb](https://github.com/tunetheweb)
* TSQL: Fix OVER functionality for functions [#1731](https://github.com/sqlfluff/sqlfluff/pull/1731) [@jpers36](https://github.com/jpers36)

## [0.7.1] - 2021-10-22

## What’s Changed

Highlights of this release contains a lot of T-SQL dialect improvements (shout out to @jpers36 for most of these!). We also added Spark3 as a new dialect thanks to @R7L208. The complete list of changes are shown below.

## 🚀 Enhancements

* TSQL: Add rank functions  [#1725](https://github.com/sqlfluff/sqlfluff/pull/1725) [@jpers36](https://github.com/jpers36)
* Spark3 Dialect Support [#1706](https://github.com/sqlfluff/sqlfluff/pull/1706) [@R7L208](https://github.com/R7L208)
* Postgres Array Support [#1722](https://github.com/sqlfluff/sqlfluff/pull/1722) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Hive: Add LEFT SEMI JOIN support [#1718](https://github.com/sqlfluff/sqlfluff/pull/1718) [@fatelei](https://github.com/fatelei)
* MySQL: Change and drop column in alter table [#1670](https://github.com/sqlfluff/sqlfluff/pull/1670) [@MontealegreLuis](https://github.com/MontealegreLuis)
* Added type hints to some rule files [#1616](https://github.com/sqlfluff/sqlfluff/pull/1616) [@ttomasz](https://github.com/ttomasz)
* Added Redshift to README [#1720](https://github.com/sqlfluff/sqlfluff/pull/1720) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Exasol: Fix create table statement [#1700](https://github.com/sqlfluff/sqlfluff/pull/1700) [@sti0](https://github.com/sti0)
* TSQL: Add optional delimiter to SET [#1717](https://github.com/sqlfluff/sqlfluff/pull/1717) [@jpers36](https://github.com/jpers36)
* TSQL: Escaped quotes [#1715](https://github.com/sqlfluff/sqlfluff/pull/1715) [@jpers36](https://github.com/jpers36)
* TSQL: SELECT INTO [#1714](https://github.com/sqlfluff/sqlfluff/pull/1714) [@jpers36](https://github.com/jpers36)
* Postgres: Added support for psql variables [#1709](https://github.com/sqlfluff/sqlfluff/pull/1709) [@WittierDinosaur](https://github.com/WittierDinosaur)
* TSQL: split location clause out from index clause [#1711](https://github.com/sqlfluff/sqlfluff/pull/1711) [@jpers36](https://github.com/jpers36)
* TSQL: Override ANSI HAVING [#1707](https://github.com/sqlfluff/sqlfluff/pull/1707) [@jpers36](https://github.com/jpers36)
* TSQL: Add UPDATE STATISTICS [#1703](https://github.com/sqlfluff/sqlfluff/pull/1703) [@jpers36](https://github.com/jpers36)
* TSQL: CTAS Option Clause [#1705](https://github.com/sqlfluff/sqlfluff/pull/1705) [@jpers36](https://github.com/jpers36)
* TSQL: DECLARE has optional AS [#1704](https://github.com/sqlfluff/sqlfluff/pull/1704) [@jpers36](https://github.com/jpers36)
* TSQL: DROP STATISTICS and INDEX [#1698](https://github.com/sqlfluff/sqlfluff/pull/1698) [@jpers36](https://github.com/jpers36)
* TSQL: CTAS select can be optionally bracketed [#1697](https://github.com/sqlfluff/sqlfluff/pull/1697) [@jpers36](https://github.com/jpers36)
* Exasol: Make function_script_terminator more strict [#1696](https://github.com/sqlfluff/sqlfluff/pull/1696) [@sti0](https://github.com/sti0)
* TSQL distribution index location [#1695](https://github.com/sqlfluff/sqlfluff/pull/1695) [@jpers36](https://github.com/jpers36)
* TSQL: allow for non-alphanumeric initial characters in delimited identifiers [#1693](https://github.com/sqlfluff/sqlfluff/pull/1693) [@jpers36](https://github.com/jpers36)
* TSQL: allow for semi-colon after BEGIN in a BEGIN/END block [#1694](https://github.com/sqlfluff/sqlfluff/pull/1694) [@jpers36](https://github.com/jpers36)
* Exasol: Fix adapter script syntax [#1692](https://github.com/sqlfluff/sqlfluff/pull/1692) [@sti0](https://github.com/sti0)
* TSQL: Basic EXECUTE functionality [#1691](https://github.com/sqlfluff/sqlfluff/pull/1691) [@jpers36](https://github.com/jpers36)
* TSQL: Add #, @ to valid identifier characters [#1690](https://github.com/sqlfluff/sqlfluff/pull/1690) [@jpers36](https://github.com/jpers36)
* TSQL - add support for Filegroups in table create [#1689](https://github.com/sqlfluff/sqlfluff/pull/1689) [@nevado](https://github.com/nevado)
* Exclude Exasol scripts from rule L003 [#1684](https://github.com/sqlfluff/sqlfluff/pull/1684) [@tunetheweb](https://github.com/tunetheweb)
* Added PostGIS keyword data types to Postgres [#1686](https://github.com/sqlfluff/sqlfluff/pull/1686) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Indent LIMIT values if on separate line [#1683](https://github.com/sqlfluff/sqlfluff/pull/1683) [@tunetheweb](https://github.com/tunetheweb)
* Postgres: Added support for SELECT INTO statements [#1676](https://github.com/sqlfluff/sqlfluff/pull/1676) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Allow :: casting of CASE statements [#1657](https://github.com/sqlfluff/sqlfluff/pull/1657) [@tunetheweb](https://github.com/tunetheweb)
* Add more keywords to Redhift and BigQuery to avoid errors [#1671](https://github.com/sqlfluff/sqlfluff/pull/1671) [@tunetheweb](https://github.com/tunetheweb)
* TSQL begin end delimiter [#1664](https://github.com/sqlfluff/sqlfluff/pull/1664) [@jpers36](https://github.com/jpers36)
* Teradata: Added date as bare function for [#1663](https://github.com/sqlfluff/sqlfluff/pull/1663) [@anzelpwj](https://github.com/anzelpwj)
* TSQL: CREATE STATISTICS [#1662](https://github.com/sqlfluff/sqlfluff/pull/1662) [@jpers36](https://github.com/jpers36)
* TSQL table and query hints [#1661](https://github.com/sqlfluff/sqlfluff/pull/1661) [@jpers36](https://github.com/jpers36)
* TSQL: Allow spaces in qualified names [#1654](https://github.com/sqlfluff/sqlfluff/pull/1654) [@jpers36](https://github.com/jpers36)

## 🐛 Bug Fixes

* EXASOL: Fix typo in alter_table_statement [#1726](https://github.com/sqlfluff/sqlfluff/pull/1726) [@sti0](https://github.com/sti0)
* Fix markdown links in production.rst [#1721](https://github.com/sqlfluff/sqlfluff/pull/1721) [@asottile](https://github.com/asottile)
* Correct contributing testing information [#1702](https://github.com/sqlfluff/sqlfluff/pull/1702) [@adam-tokarski](https://github.com/adam-tokarski)
* More ORDER BY clarifications [#1681](https://github.com/sqlfluff/sqlfluff/pull/1681) [@tunetheweb](https://github.com/tunetheweb)
* Fix TSQL L025 linter exception [#1677](https://github.com/sqlfluff/sqlfluff/pull/1677) [@tunetheweb](https://github.com/tunetheweb)
* Improve Jinja whitespace handling in rules [#1647](https://github.com/sqlfluff/sqlfluff/pull/1647) [@barrywhart](https://github.com/barrywhart)


## [0.7.0] - 2021-10-14

*** BREAKING CHANGE ***

This release extracts the dbt templater to a seperately installable plugin
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

* TSQL: CTAS delimiter [#1652](https://github.com/sqlfluff/sqlfluff/pull/1652) [@jpers36](https://github.com/jpers36)
* TSQL: Allow for multiple variables DECLAREd in the same statement [#1651](https://github.com/sqlfluff/sqlfluff/pull/1651) [@jpers36](https://github.com/jpers36)
* TSQL: Allow DECLARE/SET statements to parse using ExpressionStatement [#1649](https://github.com/sqlfluff/sqlfluff/pull/1649) [@jpers36](https://github.com/jpers36)
* TSQL PRINT statement parsing [#1648](https://github.com/sqlfluff/sqlfluff/pull/1648) [@jpers36](https://github.com/jpers36)
* Better date function for tsql [#1636](https://github.com/sqlfluff/sqlfluff/pull/1636) [@tunetheweb](https://github.com/tunetheweb)
* TSQL: Allow for multiple statements in a procedure [#1637](https://github.com/sqlfluff/sqlfluff/pull/1637) [@jpers36](https://github.com/jpers36)
* TSQL: Allow for !>, !< operators [#1640](https://github.com/sqlfluff/sqlfluff/pull/1640) [@jpers36](https://github.com/jpers36)
* TSQL: Fix GROUP BY delimiter [#1635](https://github.com/sqlfluff/sqlfluff/pull/1635) [@jpers36](https://github.com/jpers36)
* TSQL: Fix DROP delimiter [#1633](https://github.com/sqlfluff/sqlfluff/pull/1633) [@jpers36](https://github.com/jpers36)
* TSQL: +RENAME statement for Azure Synapse Analytics [#1631](https://github.com/sqlfluff/sqlfluff/pull/1631) [@jpers36](https://github.com/jpers36)
* TSQL: Fix CASTing variables [#1627](https://github.com/sqlfluff/sqlfluff/pull/1627) [@jpers36](https://github.com/jpers36)
* Snowflake: Add implementation for CREATE TASK statement [#1597](https://github.com/sqlfluff/sqlfluff/pull/1597) [#1603](https://github.com/sqlfluff/sqlfluff/pull/1603) [@JoeHut](https://github.com/JoeHut)
* Allow global config for rule testcases [#1580](https://github.com/sqlfluff/sqlfluff/pull/1580) [@sti0](https://github.com/sti0)
* Snowflake dollar sign literals [#1591](https://github.com/sqlfluff/sqlfluff/pull/1591) [@myschkyna](https://github.com/myschkyna)
* Rename test/fixtures/parser directory to test/fixtures/dialects [#1585](https://github.com/sqlfluff/sqlfluff/pull/1585) [@tunetheweb](https://github.com/tunetheweb)
* Rename keyword files [#1584](https://github.com/sqlfluff/sqlfluff/pull/1584) [@tunetheweb](https://github.com/tunetheweb)
* Add some more unreserved keywords to BigQuery [#1588](https://github.com/sqlfluff/sqlfluff/pull/1588) [@tunetheweb](https://github.com/tunetheweb)
* Increase minimum runs before coverage report is issued [#1596](https://github.com/sqlfluff/sqlfluff/pull/1596) [@tunetheweb](https://github.com/tunetheweb)
* Snowflake: Support CURRENT_TIMESTAMP as a column default value [#1578](https://github.com/sqlfluff/sqlfluff/pull/1578) [@wong-codaio](https://github.com/wong-codaio)
* TSQL temp tables [#1574](https://github.com/sqlfluff/sqlfluff/pull/1574) [@jpers36](https://github.com/jpers36)

## 🐛 Bug Fixes

* Fix NoneType exception in L031 [#1643](https://github.com/sqlfluff/sqlfluff/pull/1643) [@tunetheweb](https://github.com/tunetheweb)
* Stop rule L048 complaining if literal is followed by a semicolon [#1638](https://github.com/sqlfluff/sqlfluff/pull/1638) [@tunetheweb](https://github.com/tunetheweb)
* L031 desc updated to cover both 'from' and 'join' [#1625](https://github.com/sqlfluff/sqlfluff/pull/1625) [@nevado](https://github.com/nevado)
* Snowflake auto increments fixes [#1620](https://github.com/sqlfluff/sqlfluff/pull/1620) [@myschkyna](https://github.com/myschkyna)
* Fix DECLARE Delimitation [#1615](https://github.com/sqlfluff/sqlfluff/pull/1615) [@jpers36](https://github.com/jpers36)
* Snowflake drop column fixes [#1618](https://github.com/sqlfluff/sqlfluff/pull/1618) [@myschkyna](https://github.com/myschkyna)
* TSQL: fix statement delimitation [#1612](https://github.com/sqlfluff/sqlfluff/pull/1612) [@jpers36](https://github.com/jpers36)
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
* Update Rule L028 to handle TSQL PIVOT columns [#1545](https://github.com/sqlfluff/sqlfluff/pull/1545) [@tunetheweb](https://github.com/tunetheweb)
* TSQL IF/ELSE [#1564](https://github.com/sqlfluff/sqlfluff/pull/1564) [@jpers36](https://github.com/jpers36)
* Enums for format types and colors added [#1558](https://github.com/sqlfluff/sqlfluff/pull/1558) [@adam-tokarski](https://github.com/adam-tokarski)
* Add dbt 0.21.0 to the test suite [#1566](https://github.com/sqlfluff/sqlfluff/pull/1566) [@alanmcruickshank](https://github.com/alanmcruickshank)
* Merge EXASOL_FS dialect into EXASOL dialect [#1498](https://github.com/sqlfluff/sqlfluff/pull/1498) [@sti0](https://github.com/sti0)
* TSQL - BEGIN/END blocks [#1553](https://github.com/sqlfluff/sqlfluff/pull/1553) [@jpers36](https://github.com/jpers36)
* Small refactor with type hints and string formattings [#1525](https://github.com/sqlfluff/sqlfluff/pull/1525) [@adam-tokarski](https://github.com/adam-tokarski)
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
* TSQL: fix STRING_AGG() WITHIN GROUP clause [#1559](https://github.com/sqlfluff/sqlfluff/pull/1559) [@jpers36](https://github.com/jpers36)
* fix spelling: occurance>occurrence [#1507](https://github.com/sqlfluff/sqlfluff/pull/1507) [@jpers36](https://github.com/jpers36)


## [0.6.8] - 2021-10-05

Fixed a DBT bug introduced in 0.6.7 - apologies!

## What’s Changed

SQLFluff can't find dbt models [#1513](https://github.com/sqlfluff/sqlfluff/pull/1513) [@barrywhart](https://github.com/barrywhart)
TSQL: Support for unicode literals [#1511](https://github.com/sqlfluff/sqlfluff/pull/1511) [@adam-tokarski](https://github.com/adam-tokarski)


## [0.6.7] - 2021-10-04

Lots of fixes to our rules (particularly when running `sqlfluff fix`, and particularly for Jinja and DBT templates). We also have good improvements to Exasol, Snowflake, and T-SQL dialects amongst others. Plus we added Hive and SQLite as supported dialects!

## What’s Changed

* Snowflake better WAREHOUSE and CREATE (EXTERNAL) TABLES support [#1508](https://github.com/sqlfluff/sqlfluff/pull/1508) [@tunetheweb](https://github.com/tunetheweb)
* Exasol: Fix typo in `REORGANIZE` statement [#1509](https://github.com/sqlfluff/sqlfluff/pull/1509) [@sti0](https://github.com/sti0)
* Fix bug that can prevent linting ephemeral dbt models [#1496](https://github.com/sqlfluff/sqlfluff/pull/1496) [@barrywhart](https://github.com/barrywhart)
* Disable rules L026 and L028 for BigQuery by default, with option to reenable [#1504](https://github.com/sqlfluff/sqlfluff/pull/1504) [@tunetheweb](https://github.com/tunetheweb)
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
* TSQL dialect - +support for CONVERT() special function [#1489](https://github.com/sqlfluff/sqlfluff/pull/1489) [@jpers36](https://github.com/jpers36)
* Allow Postgres column references to use `AT TIME ZONE` [#1485](https://github.com/sqlfluff/sqlfluff/pull/1485) [@leamingrad](https://github.com/leamingrad)
* TSQL dialect - provide alternate ASA PR incorporating ASA into TSQL [#1478](https://github.com/sqlfluff/sqlfluff/pull/1478) [@jpers36](https://github.com/jpers36)
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
* TSQL: Remove Limit and NamedWindow segments as not supported in T-SQL [#1420](https://github.com/sqlfluff/sqlfluff/pull/1420) [@jpers36](https://github.com/jpers36)
* Fix runtime error (IndexError ) when linting file with jinja "if" [#1430](https://github.com/sqlfluff/sqlfluff/pull/1430) [@barrywhart](https://github.com/barrywhart)
* Add Hive dialect (#985) [@satish-ravi](https://github.com/satish-ravi)
* Further fix for L036 [#1428](https://github.com/sqlfluff/sqlfluff/pull/1428) [@tunetheweb](https://github.com/tunetheweb)
* Add default parameter to dbt "var" macro stub [#1426](https://github.com/sqlfluff/sqlfluff/pull/1426) [@CyberShadow](https://github.com/CyberShadow)


## [0.6.6] - 2021-09-20

Fixed some of our autofix rules where running `fix` sometimes made unintended changes. Added config to rules L011 and L012 to allow preferring implicit aliasing. Also further improved our Postgres support and documentation.

### What's Changed

* Rule L036 bug fixes [#1427](https://github.com/sqlfluff/sqlfluff/pull/1427) [@tunetheweb](https://github.com/tunetheweb)
* Added support for psql meta commands to Postgres [#1423](https://github.com/sqlfluff/sqlfluff/pull/1423) [@WittierDinosaur](https://github.com/WittierDinosaur)
* Remaining line endings [#1415](https://github.com/sqlfluff/sqlfluff/pull/1415) [@tunetheweb](https://github.com/tunetheweb)
* TSQL: Remove match possibilities for segments with no TSQL equivalent [#1416](https://github.com/sqlfluff/sqlfluff/pull/1416) [@jpers36](https://github.com/jpers36)
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

### What's Changed

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
* Added support for empty WINDOWS specificiations ([#1293](https://github.com/sqlfluff/sqlfluff/pull/1293)) [@matthieucan](https://github.com/matthieucan)
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
  when overriden in a specific child dialect (mysql) [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added support for the DELIMITER statement in the mysql dialect [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
- Added support for additional delimiters by creating a new DelimiterSegment in the
  ANSI dialect which defaults to the semicolon, but allows it to be more intuitive
  when overriden in a specific child dialect (mysql) [#901](https://github.com/sqlfluff/sqlfluff/issues/901))
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
  don't allow gaps. This is facilitated through an optional agrument to
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

- Tweek rule L005 to report more sensibly with newlines.
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
