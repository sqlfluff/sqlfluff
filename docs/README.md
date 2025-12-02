# SQLFluff - Generating the document website

You can run the following steps to generate the documentation website:

```
tox -e docbuild,doclinting
```

The `docbuild` job will recognise when source files have changed and only
generate the changed files. To force a clean build (for example when changing
config) rather than the source files use the following command from the project
root directory (drop the `-C docs` if running from within the `docs` directory).

```
make -C docs clean
```

The built HTML should be placed in `docs/build/html` and can be opened directly
in the browser or you can launch a simple webserver with the below command
and then navigate to http://127.0.0.1:8000/ to view the site locally:

```
python -m http.server --directory docs/build/html
```

Again, this command is run from the root server, not the `docs` subfolder but you
can alter the path as appropriate if needs be.

If you don't want to use `tox`, then you can complete the steps manually with
the following commands after setting up your Python environment as detailed
in the [CONTRIBUTING.md](../CONTRIBUTING.md) file.

```
cd docs
pip install -r requirements.txt
make html
python -m http.server --directory build/html
```

Or alternatively from the root folder:

```
pip install -r docs/requirements.txt
make -C docs html
python -m http.server --directory docs/build/html
```

The docs use Sphinx and are generated from the source code.
The config is available in `docs/source/conf.py`.
