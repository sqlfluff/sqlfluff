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
contributors, and we have
[a wiki page](https://github.com/sqlfluff/sqlfluff/wiki/Contributing-Dialect-Changes)
to help you through your first contribution. Bear in mind that all the tests
should pass, and test coverage should not decrease unduly as part of the
changes which you make. You may find it useful to familiarise yourself with the
[architectural principles here](https://docs.sqlfluff.com/en/latest/architecture.html)
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

The simplest way to set up a development environment is to use `tox`.
First ensure that you have tox installed (windows users may have to replace `python3` with `py`):
```shell
python3 -m pip install -U tox
```

A virtual environment can then be created and activated by running:
```shell
tox -e py --devenv .venv
source .venv/bin/activate
```
(The `py` environment defaults to the python version used
to install tox, however any version you want can be installed
by replacing `py` with `py37`, `py39`, `dbt020-py38`, etc. If
you are planning development on or using the dbt templater
you may wish to chose one of the dbt environments.)

Windows users should call `.venv\Scripts\activate` rather than `source .venv/bin/activate`.

This virtual environment will already have the package installed in editable mode for you, as well as
`requirements_dev.txt` and `plugins/sqlfluff-plugin-example`. Additionally if a dbt virtual environment
was specified, you will also have `dbt-core`, `dbt-postgres`, and `plugins/sqlfluff-templater-dbt` available.

### Wiki

We have a [GitHub wiki](https://github.com/sqlfluff/sqlfluff/wiki) with some
more long form tutorials for contributors, particualrly those new to SQLFluff
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

> NOTE: For packages intended to be installed like this, the source code must be directy
> within a subdirectory with the name of the package and not in a subdirectory such as
> src. This is due to a restriction in the implementation of setup.py in editable mode.

### Testing

To test locally, SQLFluff uses `tox`. The test suite can be run via:

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
tox -e py38 -- -k L012 test
```

Alternatively, you can also run tests from a specific directory or file only:
```
tox -e py38 -- test/cli
tox -e py38 -- test/cli/commands_test.py
```

To run the dbt-related tests you will have to explicitly include these tests:

```shell
tox -e cov-init,dbt018-py38,cov-report-dbt -- plugins/sqlfluff-templater-dbt
```

For more information on adding and running test cases see the [Parser Test README](test/fixtures/dialects/README.md) and the [Rules Test README](test/fixtures/rules/std_rule_cases/README.md).

### Pre-Commit Config

For development convenience we also provide a `.pre-commit-config.yaml` file to allow the user to install a selection of pre-commit hooks via `tox -e pre-commit -- install`. These hooks can help the user identify and fix potential linting/typing violations prior to committing their code and therefore reduce having to deal with these sort of issues during code review.

### Documentation Website

Documentation is built using Sphinx with some pages being built based on the source code.
See the [Documentation Website README.md](./docs/README.md) file for more information on how to build and test this.

### Building Package

New versions of SQLFluff will be published to PyPI automatically via
[GitHub Actions](.github/workflows/publish-release-to-pypi.yaml)
whenever a new release is published to GitHub.

#### Release checklist:

- [ ] Change the version in `setup.cfg` and `plugins/sqlfluff-templator-dbt/setup.cfg`
- [ ] Update the stable_version in the `[sqlfluff_docs]` section of `setup.cfg`
- [ ] Copy the draft releases from https://github.com/sqlfluff/sqlfluff/releases to [CHANGELOG.md](CHANGELOG.md)
- [ ] Add markdown links to PRs and contributors
- [ ] Check each issue title is clear, and if not edit issue title (which will automatically update Release notes on next PR merged, as the Draft one is recreated in full each time). Also edit locally in [CHANGELOG.md](CHANGELOG.md)
- [ ] Categorise them into "Enhancements" and "Bug Fixes". Enhancements should go above Bug Fixes (lead with the positive!)
- [ ] Add a comment at the top to highlight the main things in this release
- [ ] If this is a non-patch release then update the `Notable changes` section in `index.rst` with a brief summary of the new features added.
- [ ] View the CHANGELOG in this branch on GitHub to ensure you didn't miss any link conversions or other markup errors.
- [ ] Open draft PR with those change a few days in advance to give contributors notice. Tag those with open PRs in the PR to give them time to merge their work before the new release
- [ ] Comment in #contributing slack channel about release candidate
- [ ] Update the draft PR as more changes get merged
- [ ] Get another contributor to approve the PR
- [ ] Merge the PR when looks like we've got all we’re gonna get for this release
- [ ] Go to the [releases page](https://github.com/sqlfluff/sqlfluff/releases), edit the release to be same as [CHANGELOG.md](CHANGELOG.md) (remember to remove your release PR which doesn’t need to go in this). Add version tag and a title and click “Publish release”
- [ ] Announce the release in the #general channel, with shout outs to those who contributed many, or big items
- [ ] Announce the release on Twitter (@tunetheweb can do this or let him know your Twitter handle if you want access to Tweet on SQLFluff’s behalf).

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
