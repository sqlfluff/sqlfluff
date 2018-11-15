#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

# This contains various utility scripts

import shutil
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--path', default='.test-reports')
def clean_tests(path):
    """
    Clear up the tests directory
    NB: Using scripts allows platform independence
    """
    try:
        shutil.rmtree(path)
        click.echo("Removed {0!r}...".format(path))
    except FileNotFoundError:
        click.echo("Directory {0!r} does not exist. Skipping...".format(path))


if __name__ == '__main__':
    cli()
