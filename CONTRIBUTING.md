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
in the [docs/source](https://github.com/sqlfluff/sqlfluff/tree/master/docs/source)
folder of the repo). Pull requests are always welcome with documentation
improvements. Keep in mind that there are linting checks in place for good
formatting so keep an eye on the tests whenever submitting a PR.

:star2: **Fifth** - if you are so inclined - pull requests on the core codebase
are always welcome. Bear in mind that all the tests should pass, and test
coverage should not decrease unduly as part of the changes which you make.
You may find it useful to familiarise yourself with the
[architectural principles here](https://docs.sqlfluff.com/en/latest/architecture.html)
and with the [current documentation here](https://docs.sqlfluff.com).

## How the community works

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
### Testing

To test locally, SQLFluff uses `tox`, which means you can build locally using...

```shell
pip install tox
tox
```

This will build and test for several Python versions, and also lint the project.
Practically on a day-to-day basis, you might only want to lint and test for one
Python version, so you can always specify a particular environment. For example,
if you are developing in Python 3.8 you might call...

```shell
tox -e generate-fixture-yml,py38,linting
```

...or if you also want to see the coverage reporting...

```shell
tox -e generate-fixture-yml,cov-init,py38,cov-report,linting
```

> NB: The `cov-init` task clears the previous test results, the `py36` environment
> generates the results for tests in that Python version and the `cov-report-nobt`
> environment reports those results out to you (excluding dbt).

To run the dbt-related tests you will have to explicitly include these tests:

```shell
tox -e cov-init,dbt018-py38,cov-report-dbt -- -m "dbt"
```

For more information on adding and running test cases see the [Parser Test README](test/fixtures/parser/README.md) and the [Rules Test README](test/fixtures/rules/std_rule_cases/README.md).

### Using your local version

To trial using your local development branch of SQLFluff, I recommend you use a virtual
environment. e.g:

```shell
python3 -m venv .venv
source .venv/bin/activate
```
> `python3 -m venv .venv` creates a new virtual environment (in current working
> directory) called `.venv`.
> `source .venv/bin/activate` activates the virtual environment so that packages
> can be installed/uninstalled into it. [More info on venv](https://docs.python.org/3/library/venv.html).

Once you are in a virtual environment, run:

```shell
pip install -Ur requirements.txt -Ur requirements_dev.txt
python setup.py develop
```

> `pip install -Ur requirements.txt -Ur requirements_dev.txt` installs the project dependencies
> as well as the dependencies needed to run linting, formatting, and testing commands. This will
> install the most up-to-date package versions for all dependencies (-U).

> `python setup.py develop` installs the package using a link to the source code so that any changes
> which you make will immediately be available for use.

## Building Package

New versions of SQLFluff will be published to PyPI automatically via 
[GitHub actions](.github/workflows/publish-release-to-pypi.yaml) 
whenever a new release is published to GitHub.

A new release can be published with a tag in GitHub by navigating to the
[releases page](https://github.com/sqlfluff/sqlfluff/releases) and a Draft release should
already exist with merged Pull Requests automatically added since the last release.
Copy the text from the draft release into a new, version-numbered section of the [CHANGELOG.md](CHANGELOG.md) file and update the
[src/sqlfluff/config.ini](src/sqlfluff/config.ini) file to the new version.
Once both changes are done, open a new Pull Request for these changes.

:warning: **Before creating a new release, ensure that
[src/sqlfluff/config.ini](src/sqlfluff/config.ini) is up-to-date with a new version** :warning:.
If this is not done, PyPI will reject the package. Also, ensure you have used that 
version as a part of the tag and have described the changes accordingly.

### Manually

If for some reason the package needs to be submitted to PyPI manually, we use `twine`.
You will need to be an admin to submit this to PyPI, and you will need a properly
formatted `.pypirc` file. If you have managed all that then you can run:

```shell
python setup.py sdist
twine upload dist/*
```

... and the most recent version will be uploaded to PyPI.
