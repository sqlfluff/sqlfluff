# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Changed import of version information to fix bug with importing config.ini
- Added basic violations/file reporting for some verbosities
- Refactor of rules to allow rules with memory
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