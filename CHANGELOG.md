# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Changed unicode handling for better escape codes in python 2.
  Thanks [@mrshu](https://github.com/mrshu)

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