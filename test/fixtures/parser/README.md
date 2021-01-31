# Automated parser tests

The `parser` directory contains the files for automated parser tests.

This is organised first into folders for each `dialect` (e.g. `ansi`, `mysql`)
which each then contain both `.sql` files and `.yml` files. The intent for these
folders is that each test should be in the _highest_ dialect that it can be in. i.e.
If it can be in the `ansi` dialect then it should be in there.

Within each folder, any `.sql` files will be tested that they can
successfully parse (i.e. that they do not raise any errors
and that the parsed result does not contain any _unparsable_ segments).

If there is a `.yml` file with the same filename as the `.sql` file
then the _structure_ of the parsed query will also be compared against the structure
within that yaml file.

## Adding a new test

For best test coverage, add both a `.sql` and `.yml` file. The easiest way to
add a `.yml` file is to run `sqlfluff parse file.sql -f yaml`, and copy and paste
the result. From here, remove any `newline` and `whitespace` segments from the `.yml`
file, and your test should pass!
