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
import oyaml as yaml
import requests


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
@click.option('--from-file', '-f', default=None)
@click.option('--runs', default=3, show_default=True)
def benchmark(cmd, runs, from_file):
    """Benchmark how long it takes to run a particular command."""
    if from_file:
        with open(from_file, 'r') as yaml_file:
            parsed = yaml.load(yaml_file.read(), Loader=yaml.FullLoader)
            benchmarks = parsed['benchmarks']
            click.echo(repr(benchmarks))
    elif cmd:
        benchmarks = [{'name': str(hash(cmd)), 'cmd': cmd}]
    else:
        click.echo("No command or file specified!")
        sys.exit(1)

    commit_hash = None
    post_results = False
    # Try and detect a CI environment
    if 'CIRCLECI' in os.environ:
        click.echo("Circle CI detected!")
        # available_vars = [var for var in os.environ.keys()]  # if var.startswith('CIRCLE')
        # click.echo("Available keys: {0!r}".format(available_vars))
        commit_hash = os.environ.get('CIRCLE_SHA1', None)
        post_results = True
        click.echo("Commit hash is: {0!r}".format(commit_hash))

    all_results = {}
    for run_no in range(runs):
        click.echo("===== Run #{0} =====".format(run_no + 1))
        results = {}
        for benchmark in benchmarks:
            # Iterate through benchmarks
            click.echo("Starting bechmark: {0!r}".format(benchmark['name']))
            t0 = time.monotonic()
            click.echo("===START PROCESS OUTPUT===")
            process = subprocess.run(benchmark['cmd'])
            click.echo("===END PROCESS OUTPUT===")
            t1 = time.monotonic()
            if process.returncode != 0:
                click.echo("Command failed with return code: {0}".format(process.returncode))
                sys.exit(process.returncode)
            else:
                duration = t1 - t0
                click.echo("Process completed in {0:.4f}s".format(duration))
                results[benchmark['name']] = duration

        if post_results:
            click.echo("Posting results: {0}".format(results))
            resp = requests.post(
                'https://f32cvv8yh3.execute-api.eu-west-1.amazonaws.com/result/gh/{repo}/{commit}'.format(
                    # TODO: update the stats collector eventually to allow the new repo path
                    repo='alanmcruickshank/sqlfluff',
                    commit=commit_hash
                ),
                params={
                    'key': 'mtqTC1fVVebVQ5BVREP7jYrKwgjaO0IfRILzyZt'
                },
                json=results
            )
            click.echo(resp.text)
        all_results[run_no] = results
    click.echo("===== Done =====")
    for run_no in all_results:
        click.echo(
            "Run {0:>5}: {1}".format(
                "#{0}".format(run_no),
                all_results[run_no]
            )
        )


if __name__ == '__main__':
    cli()
