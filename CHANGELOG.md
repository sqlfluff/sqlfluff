# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Note: Changes are now automatically tracked in [GitHub](https://github.com/sqlfluff/sqlfluff/releases) and will be copied in here on each release (please remember to update the issues and contributors to links!). There is no need to manually edit this file going forward.
-->
<!--Start Of Releases (DO NOT DELETE THIS LINE)-->

## [1.3.1] - 2022-09-09

## Highlights
## Highlights

* More refactoring of parse structures in preparation for upcoming refactor of
  formatting/whitespace rules.
* Fixes some bugs in L003 (indentation).
* New config flag `large_file_skip_byte_limit` which applies **prior to**
  loading the file.
## What’s Changed

* Add support for additional magic methods on DummyUndefined [#3835](https://github.com/sqlfluff/sqlfluff/pull/3835) [@barrywhart
](https://github.com/barrywhart
)
* MySQL: support variable assignments by assignment operator := [#3829](https://github.com/sqlfluff/sqlfluff/pull/3829) [@yoichi
](https://github.com/yoichi
)
* MYSQL: improve lexing for single-quoted strings [#3831](https://github.com/sqlfluff/sqlfluff/pull/3831) [@mdahlman
](https://github.com/mdahlman
)
* MySQL: More support for index definition in CREATE TABLE [#3826](https://github.com/sqlfluff/sqlfluff/pull/3826) [@yoichi
](https://github.com/yoichi
)
* Typed matching and ripping out the rest of .name [#3819](https://github.com/sqlfluff/sqlfluff/pull/3819) [@alanmcruickshank
](https://github.com/alanmcruickshank
)
* sparksql dialect to support lambda expressions (->) [#3821](https://github.com/sqlfluff/sqlfluff/pull/3821) [@juhoautio
](https://github.com/juhoautio
)
* Enable file name logging for multi-files w/ --show-lint-violations flag [#3788](https://github.com/sqlfluff/sqlfluff/pull/3788) [@thechopkins
](https://github.com/thechopkins
)
* Take database and schema out of Snowflake reserved keywords list [#3818](https://github.com/sqlfluff/sqlfluff/pull/3818) [@NiallRees
](https://github.com/NiallRees
)
* Remove a chunk of name references [#3814](https://github.com/sqlfluff/sqlfluff/pull/3814) [@alanmcruickshank
](https://github.com/alanmcruickshank
)
* Fix typo in Snowflake dialect  [#3813](https://github.com/sqlfluff/sqlfluff/pull/3813) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* Allow the use of libraries in macro definitions [#3803](https://github.com/sqlfluff/sqlfluff/pull/3803) [@bjgbeelen
](https://github.com/bjgbeelen
)
* Indentation fixes and rule logging improvements [#3808](https://github.com/sqlfluff/sqlfluff/pull/3808) [@alanmcruickshank
](https://github.com/alanmcruickshank
)
* Fixes a recursion error in  JinjaTemplater handling of undefined values [#3809](https://github.com/sqlfluff/sqlfluff/pull/3809) [@barrywhart
](https://github.com/barrywhart
)
* Snowflake: extend `GRANT` syntax [#3807](https://github.com/sqlfluff/sqlfluff/pull/3807) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* add warehouse_type in snowflake dialect [#3805](https://github.com/sqlfluff/sqlfluff/pull/3805) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* add Create Notification Integration syntax [#3801](https://github.com/sqlfluff/sqlfluff/pull/3801) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* T-SQL: fix parsing PARTITION BY NULL in window function [#3790](https://github.com/sqlfluff/sqlfluff/pull/3790) [@fmms
](https://github.com/fmms
)
* SparkSQL: Update L014 rule to not flag Delta Change Data Feed Session & Table Property [#3689](https://github.com/sqlfluff/sqlfluff/pull/3689) [@R7L208
](https://github.com/R7L208
)
* Snowflake: OVER (ORDER BY) clause required for first_value (fixes #3797) [#3798](https://github.com/sqlfluff/sqlfluff/pull/3798) [@JamesRTaylor
](https://github.com/JamesRTaylor
)
* add Alter Pipe syntax for snowflake dialect [#3796](https://github.com/sqlfluff/sqlfluff/pull/3796) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* BigQuery: Parse WEEK(<WEEKDAY>) in date_part [#3787](https://github.com/sqlfluff/sqlfluff/pull/3787) [@yoichi
](https://github.com/yoichi
)
* Postgres: Support setting user properties using intrinsic ON & OFF values [#3793](https://github.com/sqlfluff/sqlfluff/pull/3793) [@chris-codaio
](https://github.com/chris-codaio
)
* extend SF dialect for File Format statements [#3774](https://github.com/sqlfluff/sqlfluff/pull/3774) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* Add QUALIFY to SparkSQL dialect [#3778](https://github.com/sqlfluff/sqlfluff/pull/3778) [@ThijsKoot
](https://github.com/ThijsKoot
)
* fix regex for S3Path [#3782](https://github.com/sqlfluff/sqlfluff/pull/3782) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* Snowflake: add Optional parameter ERROR INTEGRATION for PIPE [#3785](https://github.com/sqlfluff/sqlfluff/pull/3785) [@Gal40n04ek
](https://github.com/Gal40n04ek
)
* Add a file size check in bytes [#3770](https://github.com/sqlfluff/sqlfluff/pull/3770) [@alanmcruickshank
](https://github.com/alanmcruickshank
)
* Require importlib_metadata >=1.0.0 [#3769](https://github.com/sqlfluff/sqlfluff/pull/3769) [@alanmcruickshank
](https://github.com/alanmcruickshank
)

## New Contributors

* [@alanmcruickshank
](https://github.com/alanmcruickshank
) made their first contribution in [#3769](https://github.com/sqlfluff/sqlfluff/pull/3769)
* [@Gal40n04ek
](https://github.com/Gal40n04ek
) made their first contribution in [#3785](https://github.com/sqlfluff/sqlfluff/pull/3785)
* [@ThijsKoot
](https://github.com/ThijsKoot
) made their first contribution in [#3778](https://github.com/sqlfluff/sqlfluff/pull/3778)
* [@chris-codaio
](https://github.com/chris-codaio
) made their first contribution in [#3793](https://github.com/sqlfluff/sqlfluff/pull/3793)
* [@yoichi
](https://github.com/yoichi
) made their first contribution in [#3787](https://github.com/sqlfluff/sqlfluff/pull/3787)
* [@JamesRTaylor
](https://github.com/JamesRTaylor
) made their first contribution in [#3798](https://github.com/sqlfluff/sqlfluff/pull/3798)
* [@R7L208
](https://github.com/R7L208
) made their first contribution in [#3689](https://github.com/sqlfluff/sqlfluff/pull/3689)
* [@fmms
](https://github.com/fmms
) made their first contribution in [#3790](https://github.com/sqlfluff/sqlfluff/pull/3790)
* [@barrywhart
](https://github.com/barrywhart
) made their first contribution in [#3809](https://github.com/sqlfluff/sqlfluff/pull/3809)
* [@bjgbeelen
](https://github.com/bjgbeelen
) made their first contribution in [#3803](https://github.com/sqlfluff/sqlfluff/pull/3803)
* [@NiallRees
](https://github.com/NiallRees
) made their first contribution in [#3818](https://github.com/sqlfluff/sqlfluff/pull/3818)
* [@thechopkins
](https://github.com/thechopkins
) made their first contribution in [#3788](https://github.com/sqlfluff/sqlfluff/pull/3788)
* [@juhoautio
](https://github.com/juhoautio
) made their first contribution in [#3821](https://github.com/sqlfluff/sqlfluff/pull/3821)
* [@mdahlman
](https://github.com/mdahlman
) made their first contribution in [#3831](https://github.com/sqlfluff/sqlfluff/pull/3831)

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
* Make extenstion case insensitive [#2773](https://github.com/sqlfluff/sqlfluff/pull/2773) [@tunetheweb](https://github.com/tunetheweb)
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
* Docstrings: Replace double backtics with single quote for lint results. [#2386](https://github.com/sqlfluff/sqlfluff/pull/2386) [@jpy-git](https://github.com/jpy-git)
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
- CLI and Simple API paramaters to provide custom paths to config files.
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
* dbt 1.0.0 compatability [#2079](https://github.com/sqlfluff/sqlfluff/pull/2079) [@alanmcruickshank](https://github.com/alanmcruickshank)
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
* T-SQL: fix STRING_AGG() WITHIN GROUP clause [#1559](https://github.com/sqlfluff/sqlfluff/pull/1559) [@jpers36](https://github.com/jpers36)
* fix spelling: occurance>occurrence [#1507](https://github.com/sqlfluff/sqlfluff/pull/1507) [@jpers36](https://github.com/jpers36)


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
