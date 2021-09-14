# SQLFluff - Generating the document website

You can run the following steps to generate the documentation website:

```
tox -e docbuild, doclint
```

The built HTML should be placed in `docs/build/html` and can be opened directly
or you can launch a webserver with the following:

```
python -m http.server --directory docs/build/html
```

Note this is run from the root server, not the `doc` subfolder but you can
alter the path as appropriate if needs be.

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
The config is available in `docs/src/conf.py`.
