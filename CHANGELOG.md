# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed

## [0.1.2] - 2019-10-30
### Changed
- Fixed the errors raised by the lexer.

## [0.1.1] - 2019-10-30
### Changed
- Fixed which modules from sqlfluff are installed in the setup.py. This affects
  the `version` command.

## [0.1.0] - 2019-10-29
### Changed
- *Big Rewrite - some loss in functionality might be apparent compared
  to pre-0.1.0. Please submit any major problems as issues on github*
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
- Moved the main grammar into a seperate dialect and renamed source and test files accordingly.
- Moved to file-based tests for the ansi dialect to make it easier to test using the tool directly.
- As part of file tests - expected outcomes are now encoded in yaml to make it easier to write new tests.
- Vastly improved readability and debugging potential of the _match logging.
- Added support for windows line endings in the lexer.

## [0.0.7] - 2018-11-19
### Added
- Added a `sqlfluff fix` as a command to implement auto-fixing of linting
  errors. For now only `L001` is implemented as a rule that can fix things.
- Added a `rules` command to introspec the available rules.
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
- Added a priority for matchers to resolve some abiguity
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