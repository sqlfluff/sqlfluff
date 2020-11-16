# SqlFluff - Contributing

:star2: **First** - thanks for being interested in improving sqlfluff! :smiley:

:star2: **Second** - please read and familiarise yourself with both the content
of this guide and also our [code of conduct](CODE_OF_CONDUCT.md).

:star2: **Third** - the best way to get started contributing, is to use the
tool in anger and then to submit bugs and features through github.
In particular, in helping to develop the parser, examples of queries
which don't parse as expected are especially helpful.

:star2: **Fourth** - making sure that our documentation is up to date and useful
for new users is really important. If you're a new user, you're in precisely
the best position to do this. Familiarise yourself with the tool (as per step
2 above) and familiarise yourself with the current documentation (live version
at [docs.sqlfluff.com](https://docs.sqlfluff.com) and the source can be found
in the [docs/source](https://github.com/sqlfluff/sqlfluff/tree/master/docs/source)
folder of the repo). Pull requests are always welcome with documentation
improvements. Keep in mind that there are linting checks in place for good
formatting so keep an eye on the tests whenever submitting a PR.

:star2: **Fifth** - if you're so inclined - pull requests on the core codebase
are always welcome. Bear in mind that all the tests should pass, and test
coverage should not decrease unduly as part of the changes which you make.
You may find it useful to familiarise yourself with the
[architectural principles here](https://docs.sqlfluff.com/en/latest/architecture.html)
and with the [current documentation here](https://docs.sqlfluff.com).

## How the community works

SQLfluff is maintained by a community of volunteers, which means we have a
few processes in place to allow everyone to contribute at a level that suits
them and at a time that suits them. These aren't meant to be a way of restricting
development, but a way of allowing the community to agree what to focus on
and then effectively direct its focus toward that. Anyone can pipe up in these
discussions, and the more we hear from users the more we can build a tool
that's actually useful for the community.

- Large features for consideration will be organised into _Major Releases_.
  These will usually include significant changes in functionality or backward
  incompatible changes. As some of these features may require significant
  coordination, discussion or development work, there is a process for each
  major release to work out what features will fit into that release.
  - Each major release will have its own github issue. For example the link
    to the issue for [0.4.0 is here](https://github.com/sqlfluff/sqlfluff/issues/470).
  - Features or issues are organised into a _shortlist_. During the initial
    discussion for the release, each feature is vetted for enough clarity
    that someone in the community can pick it up. Issues where we can't
    reach clarity will be pushed to the next release. Getting this clarity
    is important before development work progresses so that we know that
    larger changes are a) in line with the aims of the project and b) are
    effectively pre-approved changes so that there aren't any suprises
    when it comes to merging.
  - Once we reach the deadline for closing the roadmap for a release the
    focus on development work should be on those features.
- Small features and bugfixes (assuming no backward compatability issues)
  don't need to go through the same process and vetting and can be picked
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

To test locally, sqlfluff uses `tox`.

**For Windows users**: the tox environment depends on `make` to set up the dbt test folders.
To do that we recommend using _chocolatey_. You can find the instructions to install chocolately here: https://chocolatey.org/install.
Once chocolatey is installed you can use `choco install make` to install `make`.

Then you can build locally using...

```shell
pip install tox
tox
```

This will build and test for several python versions, and also lint the project.
Practically on a day to day basis, you might only want to lint and test for one
python version, so you can always specify a particular environment. For example
if you're developing in python 3.6 you might call...

```shell
tox -e py36,linting
```

...or if you also want to see the coverage reporting...

```shell
tox -e cov-init,py36,cov-report,linting
```

> NB: The `cov-init` task clears the previous test results, the `py36` environment
> generates the results for tests in that python version and the `cov-report` environment
> actually reports those results out to you.

To run the dbt-related tests you will have to explicitly include these tests:

```shell
tox -e dbt018-py38 -- -m "dbt"
```

### Using your local version

To trial using your local development branch of sqlfluff, I recommend you use a virtual
environment. e.g:

```shell
python3 -m venv .venv
source .venv/bin/activate
```
> `python3 -m venv .venv` creates a new virtual environment (in current working
> directory) called `.venv`.
> `source .venv/bin/activate` activates the virtual environment so that packages
> can be installed/uninstalled into it. [More info on venv](https://docs.python.org/3/library/venv.html).

Once you're in a virtual environment, run:

```shell
pip install -Ur requirements.txt -Ur requirements_dev.txt
python setup.py develop
```

> `setup.py develop` installs the package using a link to the source code so that any changes
> which you make will immediately be available for use.
>
> `pip install -Ur requirements.txt -Ur requirements_dev.txt` installs the project dependencies
> as well as the dependencies needed to run linting, formatting, and testing commands. This will
> install the most up-to-date package versions for all dependencies.

## Building Package

To build and submit the package to pypi we use `twine`. You'll need to be an admin
to actually submit this to pypi and you'll need a properly formatted `.pypirc` file.
If you've managed all that then you can run:

```shell
python setup.py sdist
twine upload dist/*
```

... and the most recent version will be uploaded to pypi.
