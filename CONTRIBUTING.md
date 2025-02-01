# SQLFluff - Contributing

:star2: **First** - thanks for being interested in improving SQLFluff! :smiley:

:star2: **Second** - please read and familiarise yourself with both the content
of this guide and also our [code of conduct](CODE_OF_CONDUCT.md).

:star2: **Third** - the best way to get started contributing, is to use the
tool in anger and then to submit bugs and features through GitHub.
In particular, in helping to develop the parser, examples of queries
that do not parse as expected are especially helpful.

:star2: **Fourth** - making sure that our documentation is up-to-date and useful
for new users is really important. If you are a new user, you are in precisely
the best position to do this. Familiarise yourself with the tool (as per step
2 above) and familiarise yourself with the current documentation (live version
at [docs.sqlfluff.com](https://docs.sqlfluff.com) and the source can be found
in the [docs](./docs/) folder of the repo). Pull requests are always welcome
with documentation improvements. Keep in mind that there are linting checks in
place for good formatting so keep an eye on the tests whenever submitting a PR.
We also have a [GitHub wiki](https://github.com/sqlfluff/sqlfluff/wiki) for
longer tutorials. We welcome
[contributions, suggestions or requests](https://github.com/sqlfluff/sqlfluff/issues/2104)
for the wiki.

:star2: **Fifth** - if you are so inclined - pull requests on the core codebase
are always welcome. Dialect additions are often a good entry point for new
contributors, and we have [a set of guides](https://docs.sqlfluff.com/en/stable/perma/guides.html)
to help you through your first contribution. Bear in mind that all the tests
should pass, and test coverage should not decrease unduly as part of the
changes which you make. You may find it useful to familiarise yourself with the
[architectural principles here](https://docs.sqlfluff.com/en/stable/perma/architecture.html)
and with the [current documentation here](https://docs.sqlfluff.com).

## How The Community Works

SQLFluff is maintained by a community of volunteers, which means we have a
few processes in place to allow everyone to contribute at a level that suits
them and at a time that suits them. These are not meant to be a way of restricting
development, but a way of allowing the community to agree what to focus on
and then effectively direct its focus toward that. Anyone can pipe up in these
discussions, and the more we hear from users the more we can build a tool
that is useful for the community.

- Large features for consideration will be organised into _Major Releases_.
  These will usually include significant changes in functionality or backwards-incompatible
  changes. As some of these features may require significant
  coordination, discussion or development work, there is a process for each
  major release to work out what features will fit into that release.
  - Each major release will have its own GitHub issue. For example, the link
    to the issue for [0.6.0 is here](https://github.com/sqlfluff/sqlfluff/issues/922).
  - Features or issues are organised into a _shortlist_. During the initial
    discussion for the release, each feature is vetted for enough clarity
    that someone in the community can pick it up. Issues, where we cannot
    reach clarity, will be pushed to the next release. Getting this clarity
    is important before development work progresses so that we know that
    larger changes are a) in line with the aims of the project and b) are
    effectively pre-approved changes so that there are not any surprises
    when it comes to merging.
  - Once we reach the deadline for closing the roadmap for a release the
    focus on development work should be on those features.
- Small features and bug fixes (assuming no backward compatibility issues)
  do not need to go through the same process and vetting and can be picked
  up and merged at any time.

### Maintainers

A small group of people volunteer their time to maintain the project and
share the responsibility for responding to issues and reviewing any proposed
changes via pull requests. Each one of them will be trying to follow
the process above and keep development work on the project moving. That
means for smaller changes and improvements they may review changes as
individuals and merge them into the project in a very lightweight way.
For larger changes, especially if not already part of the current major
release process the expectation is that they will involve other members
or the maintainer community or the project admins before merging in
larger changes or giving the green light to major structural project
changes.

## Nerdy Details

### Developing and Running SQLFluff Locally

#### Requirements

If you plan on working with a particular dbt plugin, you will need
to ensure your python version is high enough to support it. For example,
the instructions below use `python3.12`, and we support as low as `python3.8`
but if you are working with `dbt-snowflake` 1.9.0 you will need python at least 3.9.

The simplest way to set up a development environment is to use `tox`.

First ensure that you have tox installed:
```shell
python3.12 -m pip install -U tox
```
**IMPORTANT:** Python 3.8 is the minimum version we support. Feel free
to test on anything between `python3.8` and `python3.13`.

Note: Unfortunately tox does not currently support setting just a minimum
Python version (though this may be be coming in tox 4!).

#### Creating a virtual environment

A virtual environment can then be created and activated. For the
various versions currently available you can check the `tox.ini` file.
The numbers correspond to the dbt core version; dbt180 will install
dbt 1.8.0.

To build and activate the virtual environment:
```shell
tox -e dbt180 --devenv .venv
source .venv/bin/activate
```
(The `dbt180` environment is a good default choice.
However any version can be installed by replacing `dbt180` with
`py`, `py38` through `py313`, `dbt140` through `dbt190`, etc.
`py` defaults to the python version that was used to install tox.
To be able to run all tests including the dbt templater,
choose one of the dbt environments.)

Windows users should call `.venv\Scripts\activate` rather than `source .venv/bin/activate`.
They may also want to substitute `winpy` for `py` in the commands above.

This virtual environment will already have the package installed in editable
mode for you, as well as `requirements_dev.txt` and `plugins/sqlfluff-plugin-example`.
Additionally if a dbt virtual environment was specified, you will also have
`dbt-core`, `dbt-postgres`, and `plugins/sqlfluff-templater-dbt` available.
A different dbt plugin can be selected by changing the appropriate file under `constraints`
for the desired package and version.

### Wiki

We have a [GitHub wiki](https://github.com/sqlfluff/sqlfluff/wiki) with some
more long form tutorials for contributors, particularly those new to SQLFluff
or contributing to open source. We welcome
[contributions, suggestions or requests](https://github.com/sqlfluff/sqlfluff/issues/2104)
for the wiki.

### Developing plugins

If you're working on plugins (like the dbt templater), you'll also need to install
those plugins too in an editable mode. This works the same way as the main project
but you'll need to do each one explicitly. e.g.

```shell
pip install -e plugins/sqlfluff-templater-dbt/.
```

> NOTE: For packages intended to be installed like this, the source code must be directly
> within a subdirectory with the name of the package and not in a subdirectory such as
> src. This is due to a restriction in the implementation of setup.py in editable mode.

### Testing

To test locally, SQLFluff uses `tox` (check the [requirements](#requirements)!).
The test suite can be run via:

```shell
tox
```

This will build and test for several Python versions, and also lint the project.
Practically on a day-to-day basis, you might only want to lint and test for one
Python version, so you can always specify a particular environment. For example,
if you are developing in Python 3.8 you might call...

```shell
tox -e generate-fixture-yml,py38,linting,mypy
```

...or if you also want to see the coverage reporting...

```shell
tox -e generate-fixture-yml,cov-init,py38,cov-report,linting,mypy
```

> NB: The `cov-init` task clears the previous test results, the `py38` environment
> generates the results for tests in that Python version and the `cov-report`
> environment reports those results out to you (excluding dbt).

`tox` accepts `posargs` to allow you to refine your test run, which is much
faster while working on an issue, before running full tests at the end.
For example, you can run specific tests by making use of the `-k` option in `pytest`:

```
tox -e py38 -- -k AL02 test
```

Alternatively, you can also run tests from a specific directory or file only:
```
tox -e py38 -- test/cli
tox -e py38 -- test/cli/commands_test.py
```

You can also manually test your updated code against a SQL file via:
```shell
sqlfluff parse test.sql
```
(ensure your virtual environment is activated first).

#### How to use and understand the test suite

When developing for SQLFluff, you may not need (or wish) to run the whole test
suite, depending on what you are working on. Here are a couple of scenarios
for development, and which parts of the test suite you may find most useful.

1. For dialect improvements (i.e. changes to anything in [src/sqlfluff/dialects](./src/sqlfluff/dialects))
   you should not need to continuously run the full core test suite. Running
   either `tox -e generate-fixture-yml` (if using tox), or setting up a python
   virtualenv and running `test/generate_parse_fixture_yml.py` directly will
   usually be sufficient. Both of these options accept arguments to restrict
   runs to specific dialects to further improve iteration speed. e.g.
   - `tox -e generate-fixture-yml -- -d mysql` will run just the mysql tests.
   - `python test/generate_parse_fixture_yml.py -d mysql` will do the same.
2. Developing for the dbt templater should only require running the dbt test
   suite (see below).
3. Developing rules and rule plugins there are a couple of scenarios.
   - When developing a new rule or working with a more isolated rule, you
     should only need to run the tests for that rule. These are usually what
     are called the _yaml tests_. This refers to a body of example sql
     statements and potential fixes defined in a large set of yaml files
     found in [test/fixtures/rules/std_rule_cases](./test/fixtures/rules/std_rule_cases).
     The easiest way to run these is by calling that part of the suite
     directly and filtering to just that rule. For example:
     - `tox -e py39 -- test/rules/yaml_test_cases_test.py -k AL01`
     - `pytest test/rules/yaml_test_cases_test.py -k AL01`
   - When developing on some more complicated rules, or ones known to
     have interactions with other rules, there are a set of rule fixing
     tests which apply a set combination of those rules. These are best
     run via the `autofix` tests. For example:
     - `tox -e py39 -- test/rules/std_fix_auto_test.py`
     - `pytest test/rules/std_fix_auto_test.py`
     - Potentially even the full rules suite `tox -e py39 -- test/rules`
   - A small number of core rules are also used in making sure that inner
     parts of SQLFluff are also functioning. This isn't great isolation
     but does mean that occasionally you may find side effects of your
     changes in the wider test suite. These can usually be caught by
     running the full `tox -e py39` suite as a final check (or using the
     test suite on GitHub when posting your PR).
4. When developing the internals of SQLFluff (i.e. anything not
   already mentioned above), the test suite typically mirrors the structure
   of the internal submodules of sqlfluff:
   - When working with the CLI, the `sqlfluff.cli` module has a test suite
     called via `tox -e py39 -- test/cli`.
   - When working with the templaters (i.e. `sqlfluff.core.templaters`), the
     corresponding test suite is found via `tox -e py39 -- test/core/templaters`.
   - This rough guidance and may however not apply for all of the internals.
     For example, changes to the internals of the parsing module (`sqlfluff.core.parser`)
     are very likely to have knock-on implications across the rest of the test
     suite and it may be necessary to run the whole thing. In these
     situations however you can usually work slowly outward, for example:
     1. If your change is to the `AnyOf()` grammar, first running `tox -e py39 -- test/core/parser/grammar_test.py` would be wise.
     2. ...followed by `tox -e py39 -- test/core/parser` once the above is passing.
     3. ...and then `tox -e py39 -- test/core`.
     4. ...and finally the full suite `tox -e py39`.

#### dbt templater tests

The dbt templater tests require a locally running Postgres instance. See the
required connection parameters in `plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles.yml`.
We recommend using https://postgresapp.com/.

To run the dbt-related tests you will have to explicitly include these tests:

```shell
tox -e cov-init,dbt018-py38,cov-report-dbt -- plugins/sqlfluff-templater-dbt
```

For more information on adding and running test cases see the [Parser Test README](test/fixtures/dialects/README.md) and the [Rules Test README](test/fixtures/rules/std_rule_cases/README.md).

#### Running dbt templater tests in Docker Compose

NOTE: If you prefer, you can develop and debug the dbt templater using a
Docker Compose environment. It's a simple two-container configuration:
* `app`: Hosts the SQLFluff development environment. The host's source
  directory is mounted into the container, so you can iterate on code
  changes without having to constantly rebuild and restart the container.
* `postgres`: Hosts a transient Postgres database instance.

Steps to use the Docker Compose environment:
* Install Docker on your machine.
* Run `plugins/sqlfluff-templater-dbt/docker/startup` to create the containers.
* Run `plugins/sqlfluff-templater-dbt/docker/shell` to start a bash session
  in the `app` container.

Inside the container, run:
```
py.test -v plugins/sqlfluff-templater-dbt/test/
```

### Pre-Commit Config

For development convenience we also provide a `.pre-commit-config.yaml` file
to allow the user to install a selection of pre-commit hooks by running (check
the [requirements](#requirements) before running this):

```
tox -e pre-commit -- install
```

These hooks can help the user identify and fix potential linting/typing
violations prior to committing their code and therefore reduce having to deal
with these sort of issues during code review.

### Documentation Website

Documentation is built using Sphinx with some pages being built based on the
source code. See the [Documentation Website README.md](./docs/README.md) file
for more information on how to build and test this.

### Building Package

New versions of SQLFluff will be published to PyPI automatically via
[GitHub Actions](.github/workflows/publish-release-to-pypi.yaml)
whenever a new release is published to GitHub.

#### Release checklist:

The [release page](https://github.com/sqlfluff/sqlfluff/releases) shows
maintainers all merges since last release. Once we have a long enough list,
we should prepare a release.

A release PR can be created by maintainers via the
["Create release pull request" GitHub Action](https://github.com/sqlfluff/sqlfluff/actions/workflows/create-release-pull-request.yaml).

As further PRs are merged, we may need to rerun the release script again
(or alternatively just manually updating the branch). This can only be rerun
locally (the GitHub Action will exit error if the branch already exists to
prevent overwriting it).

Check out the release branch created by the GitHub Action locally and run
the script. It will preserve any `Highlights` you have added and update the
other sections with new contributions. It can be run as follows (you will
need a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with "repo" permission):

```shell
source .venv/bin/activate
export GITHUB_REPOSITORY_OWNER=sqlfluff
export GITHUB_TOKEN=gho_xxxxxxxx # Change to your token with "repo" permissions.
python util.py release 2.0.3 # Change to your release number
```

Below is the old list of release steps, but many are automated by the process
described above.

- [ ] Change the version in `setup.cfg` and `plugins/sqlfluff-templater-dbt/setup.cfg`
- [ ] Update the stable_version in the `[sqlfluff_docs]` section of `setup.cfg`
- [ ] Copy the draft releases from https://github.com/sqlfluff/sqlfluff/releases
      to [CHANGELOG.md](CHANGELOG.md). These draft release notes have been created
      by a GitHub Action on each PR merge.
- [ ] If you pretend to create a new draft in GitHub and hit "Auto Generate Release
      Notes", then it will basically recreate these notes (though in a slightly
      different format), but also add a nice "First contributors" section, so can
      copy that "First contributors" section too and then abandon that new draft
      ([an issues](https://github.com/release-drafter/release-drafter/issues/1001)
      has been raised to ask for this in Release Drafter GitHub Action).
- [ ] Add markdown links to PRs as annoyingly GitHub doesn't do this automatically
      when displaying Markdown files, like it does for comments. You can use regex
      in most code editors to replace `\(#([0-9]*)\) @([^ ]*)$` to
      `[#$1](https://github.com/sqlfluff/sqlfluff/pull/$1) [@$2](https://github.com/$2)`,
      or if using the GitHub generated release notes then can replace
      `by @([^ ]*) in https://github.com/sqlfluff/sqlfluff/pull/([0-9]*)$` to
      `[#$2](https://github.com/sqlfluff/sqlfluff/pull/$2) [@$1](https://github.com/$1)`.
- [ ] For the new contributors section, you can replace
      `\* @([^ ]*) made their first contribution in https://github.com/sqlfluff/sqlfluff/pull/([0-9]*)$`
      with `* [@$1](https://github.com/$1) made their first contribution in [#$2](https://github.com/sqlfluff/sqlfluff/pull/$2)` to do this automatically).
- [ ] Check each issue title is clear, and if not edit issue title (which will
      automatically update Release notes on next PR merged, as the Draft one is
      recreated in full each time). We also don't use
      [conventional commit PR titles](https://www.conventionalcommits.org/en/v1.0.0/)
      (e.g. `feat`) so make them more English readable. Make same edits locally
      in [CHANGELOG.md](CHANGELOG.md).
- [ ] Add a comment at the top to highlight the main things in this release.
- [ ] If this is a non-patch release then update the `Notable changes` section in
      `index.rst` with a brief summary of the new features added that made this a
      non-patch release.
- [ ] View the CHANGELOG in this branch on GitHub to ensure you didn't miss any
      link conversions or other markup errors.
- [ ] Open draft PR with those change a few days in advance to give contributors
      notice. Tag those with open PRs in the PR in GitHub to give them time to merge
      their work before the new release
- [ ] Comment in #contributing slack channel about release candidate.
- [ ] Update the draft PR as more changes get merged.
- [ ] Get another contributor to approve the PR.
- [ ] Merge the PR when looks like we've got all we’re going to get for this release.
- [ ] Go to the [releases page](https://github.com/sqlfluff/sqlfluff/releases), edit
      the release to be same as [CHANGELOG.md](CHANGELOG.md) (remember to remove your
      release PR which doesn’t need to go in this). Add version tag and a title and
      click “Publish release”.
- [ ] Announce the release in the #general channel, with shout outs to those who
      contributed many, or big items.
- [ ] Announce the release on Twitter (@tunetheweb can do this or let him know your
      Twitter handle if you want access to Tweet on SQLFluff’s behalf).

:warning: **Before creating a new release, ensure that
[setup.cfg](setup.cfg) is up-to-date with a new version** :warning:.
If this is not done, PyPI will reject the package. Also, ensure you have used that
version as a part of the tag and have described the changes accordingly.

#### Releasing Manually

If for some reason the package needs to be submitted to PyPI manually, we use `twine`.
You will need to be an admin to submit this to PyPI, and you will need a properly
formatted `.pypirc` file. If you have managed all that then you can run:

```shell
tox -e publish-dist
```

... and the most recent version will be uploaded to PyPI.
