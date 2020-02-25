#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Utility strings for use during deployment.

NB: This is not part of the core sqlfluff code.
"""

from __future__ import absolute_import
from __future__ import print_function

# This contains various utility scripts

import shutil
import os
import click
import time
import subprocess
import sys


@click.group()
def cli():
    """Launch the utility cli."""
    pass


@cli.command()
@click.option('--path', default='.test-reports')
def clean_tests(path):
    """Clear up the tests directory.

    NB: Using scripts allows platform independence
    Makes a new one afterward
    """
    try:
        shutil.rmtree(path)
        click.echo("Removed {0!r}...".format(path))
    # OSError is for python 27
    # in py36 its FileNotFoundError (but that inherits from IOError, which exists in py27)
    except (IOError, OSError):
        click.echo("Directory {0!r} does not exist. Skipping...".format(path))

    os.mkdir(path)
    click.echo("Created {0!r}".format(path))


@cli.command()
@click.argument('cmd', nargs=-1)
def benchmark(cmd):
    """Benchmark how long it takes to run a particular command."""
    if not cmd:
        click.echo("No command specified!")
        sys.exit(1)

    # Try and detect a CI environment
    if 'CIRCLECI' in os.environ:
        click.echo("Circle CI detected!")
        available_vars = [var for var in os.environ.keys() if var.startswith('CIRCLE')]
        click.echo("Available keys: {0!r}".format(available_vars))

    t0 = time.monotonic()
    click.echo("===START PROCESS OUTPUT===")
    process = subprocess.run(cmd)
    click.echo("===END PROCESS OUTPUT===")
    t1 = time.monotonic()
    if process.returncode != 0:
        click.echo("Command failed with return code: {0}".format(process.returncode))
        sys.exit(process.returncode)
    else:
        click.echo("Process completed in {0:.4f}s".format(t1 - t0))


if __name__ == '__main__':
    cli()
