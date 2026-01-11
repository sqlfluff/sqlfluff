# Installation Guide

To get started with *SQLFluff* you'll need `python` and `pip` installed
on your machine, if you're already set up, you can skip straight to
[Installing sqlfluff](#installing-sqlfluff).

## Installing Python

How to install `python` and `pip` depends on what operating system
you're using. In any case, the python wiki provides up to date
[instructions for all platforms here](https://wiki.python.org/moin/BeginnersGuide/Download).

There's a chance that you'll be offered the choice between `python`
versions. Support for python 2 was dropped in early 2020, so you
should always opt for a version number starting with a 3. As for
more specific options beyond that, *SQLFluff* aims to be compatible
with all current python versions, and so it's best to pick the most
recent.

You can confirm that python is working as expected by heading to
your terminal or console of choice and typing `python --version`
which should give you a sensible read out and not an error.

```bash
python --version
Python 3.9.1
```

For most people, their installation of python will come with
`pip` (the python package manager) preinstalled. To confirm
this you can type `pip --version` similar to python above.

```bash
pip --version
pip 21.3.1 from
```

If however, you do have python installed but not `pip`, then
the best instructions for what to do next are [on the python website](https://pip.pypa.io/en/stable/installation/).

## Installing SQLFluff

Assuming that python and pip are already installed, then installing
*SQLFluff* is straight forward.

```bash
pip install sqlfluff
```

You can confirm its installation by getting *SQLFluff* to show its
version number.

```bash
sqlfluff version
3.5.0
```

## Going further

From here, there are several more things to explore.

* To understand how *SQLFluff* is interpreting your file
  explore the `parse` command. You can learn more about
  that command and more by running `sqlfluff --help` or
  `sqlfluff parse --help`.
* To start linting more than just one file at a time, experiment
  with passing SQLFluff directories rather than just single files.
  Try running `sqlfluff lint .` (to lint every sql file in the
  current folder) or `sqlfluff lint path/to/my/sqlfiles`.
* To find out more about which rules are available, see [Rules Reference](/reference/rules).
* To find out more about configuring *SQLFluff* and what other options
  are available, see [Configuration](/configuration/).
* Once you're ready to start using *SQLFluff* on a project or with the
  rest of your team, check out [Production Usage](/usage/production).

One last thing to note is that *SQLFluff* is a relatively new project
and you may find bugs or strange things while using it. If you do find
anything, the most useful thing you can do is to [post the issue on
GitHub](https://github.com/sqlfluff/sqlfluff/issues) where the maintainers of the project can work out what to do with
it. The project is in active development and so updates and fixes may
come out regularly.
