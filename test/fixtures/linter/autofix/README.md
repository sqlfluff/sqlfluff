# Automated linter fix tests

The `autofix` directory contains the files for automated linter fix tests.

The structure is:
- First level is folders for each `dialect` (e.g. `ansi`, `mysql`).
- Second level is a series of folders for each test. Typically these
  are of the for `001_L001_test_description`, to help contributers
  understand the purpose of the test. The `L001` section will be used
  to populate the `--rules` argument for which rules we'll fix. For
  multiple rules, simply concatenate them e.g. `L001L002`, they'll be
  seperated in the test.
- Within that folder there will be a `before.sql` file and an `after.sql`
  file, optionally there may also be a config file named `setup.cfg`.
  Additionally if a `violations.json` file is provided, it will be used
  to check that the relevant violations are found in the first place.
