# SqlFluff - Contributing

:star2: **First** - thanks for being interested in improving sqlfluff! :smiley:

:star2: **Second** - the best way to get started contributing, is to use the
tool in anger and then to submit bugs and features through github.
In particular, in helping to develop the parser, examples of queries
which don't parse as expected are especially helpful.

:star2: **Third** - making sure that our documentation is up to date and useful
for new users is really important. If you're a new user, you're in precisely
the best position to do this. Familiarise yourself with the tool (as per step
2 above) and familiarise yourself with the current documentation (live version
at [docs.sqlfluff.com](https://docs.sqlfluff.com) and the source can be found
in the [docs/source](https://github.com/sqlfluff/sqlfluff/tree/master/docs/source)
folder of the repo). Pull requests are always welcome with documentation
improvements. Keep in mind that there are linting checks in place for good
formatting so keep an eye on the tests whenever submitting a PR.

:star2: **Fourth** - if you're so inclined - pull requests on the core codebase
are always welcome. Bear in mind that all the tests should pass, and test
coverage should not decrease unduly as part of the changes which you make.
You may find it useful to familiarise yourself with the
[architectural principles here](https://docs.sqlfluff.com/en/latest/architecture.html)
and with the [current documentation here](https://docs.sqlfluff.com).

## Nerdy Details
### Testing

To test locally, sqlfluff uses `tox`. You can build locally using...

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

### Using your local version

To trial using your local development branch of sqlfluff, I recommend you use a virtual
environment. __(TODO: Insert a link here to the python docs for `virtualenv`)__

Once you're in a virtual environment, run:

```shell
pip install -r requirements.txt
python setup.py develop
```

> `setup.py develop` installs the package using a link to the source code so that any changes
> which you make will immediately be available for use.

## Building Package

To build and submit the package to pypi we use `twine`. You'll need to be an admin
to actually submit this to pypi and you'll need a properly formatted `.pypirc` file.
If you've managed all that then you can run:

```shell
python setup.py sdist
twine upload dist/*
```

... and the most recent version will be uploaded to pypi.
