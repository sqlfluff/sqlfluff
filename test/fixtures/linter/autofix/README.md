# Automated linter fix tests

The `autofix` directory contains the files for automated linter fix tests.

The structure is:
- First level is folders for each `dialect` (e.g. `ansi`, `mysql`).
- Second level is a series of folders for each test. Typically these
  are of the for `001_test_description`, to help contributors
  understand the purpose of the test.
- Within that folder there will be a `before.sql` file, an `after.sql`
  file, and a config file named `test-config.yml`. Additionally if a
  `violations.json` file is provided, it will be used to check that the
  relevant violations are found in the first place.
