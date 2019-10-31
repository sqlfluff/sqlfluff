# Automated parser tests

The `parser` directory contains the files for automated parser tests.

This is organised first into folders for each `dialect` (e.g. `ansi`, `mysql`)
which each then contain both `.sql` files and `.yml` files. The intent for these
folders is that each test should be in the _highest_ dialect that it can be in. i.e.
If it can be in the `ansi` dialect then it should be in there.

Within each folder, and `.sql` files will automatically get picked up in the testing
scripts that the can successfully parse (i.e. that they do not raise any errors
and that the parsed result does not contain any _unparsable_ segments).

**Additionally** if there is a `.yml` file with the same root as the `.sql` file
then the _structure_ of the parsed query will also be compared against the structure
within that yaml file. See some of the simple examples for how to lay out these
files.
