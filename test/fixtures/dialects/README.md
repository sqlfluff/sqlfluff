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
add a `.yml` file is to run:

```
python test/generate_parse_fixture_yml.py [--dialect <dialect>] [--filter <glob_filter>] [--new-only]
```

Or via `tox`:

```
tox -e generate-fixture-yml
```

Or via `tox` with arguments:

```
tox -e generate-fixture-yml -- --dialect <dialect>
```

This will regenerate all the parsed structure yml files, or a subset based on the given filters.

## Running parser tests

To avoid running the whole test suite with tox after changing parsers, you can instead
run:

```
pytest test/dialects/dialects_test.py
```

to save some time.
