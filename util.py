#!/usr/bin/env python

"""Utility strings for use during deployment.

NB: This is not part of the core sqlfluff code.
"""


# This contains various utility scripts

import shutil
import os
import click
import time
import subprocess
import sys
import yaml
import requests


@click.group()
def cli():
    """Launch the utility cli."""
    pass


@cli.command()
@click.option("--path", default=".test-reports")
def clean_tests(path):
    """Clear up the tests directory.

    NB: Using scripts allows platform independence
    Makes a new one afterward
    """
    try:
        shutil.rmtree(path)
        click.echo(f"Removed {path!r}...")
    # OSError is for python 27
    # in py36 its FileNotFoundError (but that inherits from IOError, which exists in
    # py27)
    except OSError:
        click.echo(f"Directory {path!r} does not exist. Skipping...")

    os.mkdir(path)
    click.echo(f"Created {path!r}")


@cli.command()
@click.argument("cmd", nargs=-1)
@click.option("--from-file", "-f", default=None)
@click.option("--runs", default=3, show_default=True)
def benchmark(cmd, runs, from_file):
    """Benchmark how long it takes to run a particular command."""
    if from_file:
        with open(from_file) as yaml_file:
            parsed = yaml.load(yaml_file.read(), Loader=yaml.FullLoader)
            benchmarks = parsed["benchmarks"]
            click.echo(repr(benchmarks))
    elif cmd:
        benchmarks = [{"name": str(hash(cmd)), "cmd": cmd}]
    else:
        click.echo("No command or file specified!")
        sys.exit(1)

    commit_hash = None
    post_results = False
    # Try and detect a CI environment
    if "CI" in os.environ:
        click.echo("CI detected!")
        # available_vars = [var for var in os.environ.keys()]
        # if var.startswith('CIRCLE')
        # click.echo("Available keys: {0!r}".format(available_vars))
        commit_hash = os.environ.get("GITHUB_SHA", None)
        post_results = True
        click.echo(f"Commit hash is: {commit_hash!r}")

    all_results = {}
    for run_no in range(runs):
        click.echo(f"===== Run #{run_no + 1} =====")
        results = {}
        for benchmark in benchmarks:
            # Iterate through benchmarks
            click.echo("Starting benchmark: {!r}".format(benchmark["name"]))
            t0 = time.monotonic()
            click.echo("===START PROCESS OUTPUT===")
            process = subprocess.run(benchmark["cmd"])
            click.echo("===END PROCESS OUTPUT===")
            t1 = time.monotonic()
            if process.returncode != 0:
                if benchmark["cmd"][0] == "sqlfluff" and benchmark["cmd"][1] == "fix":
                    # Allow fix to fail as not all our benchmark errors are fixable
                    click.echo(
                        f"Fix command failed with return code: {process.returncode}"
                    )
                else:
                    click.echo(f"Command failed with return code: {process.returncode}")
                    sys.exit(process.returncode)
            else:
                duration = t1 - t0
                click.echo(f"Process completed in {duration:.4f}s")
                results[benchmark["name"]] = duration

        if post_results:
            click.echo(f"Posting results: {results}")
            api_key = os.environ["SQLFLUFF_BENCHMARK_API_KEY"]
            resp = requests.post(
                "https://f32cvv8yh3.execute-api.eu-west-1.amazonaws.com/result/gh"
                "/{repo}/{commit}".format(
                    # TODO: update the stats collector eventually to allow the new repo
                    # path
                    repo="alanmcruickshank/sqlfluff",
                    commit=commit_hash,
                ),
                params={"key": api_key},
                json=results,
            )
            click.echo(resp.text)
        all_results[run_no] = results
    click.echo("===== Done =====")
    for run_no in all_results:
        click.echo("Run {:>5}: {}".format(f"#{run_no}", all_results[run_no]))


if __name__ == "__main__":
    cli()
