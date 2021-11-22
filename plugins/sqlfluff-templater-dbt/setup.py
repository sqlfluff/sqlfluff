"""Setup file for example plugin."""
from setuptools import setup
from os.path import dirname, join


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="sqlfluff-templater-dbt",
    version="0.8.2",
    include_package_data=False,
    license="MIT License",
    description="Lint your dbt project SQL.",
    long_description=read("README.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    author="Alan Cruickshank",
    author_email="alan@designingoverload.com",
    url="https://github.com/sqlfluff/sqlfluff",
    python_requires=">=3.6",
    keywords=[
        "sqlfluff",
        "sql",
        "linter",
        "formatter",
        "dbt",
    ],
    project_urls={
        "Homepage": "https://www.sqlfluff.com",
        "Documentation": "https://docs.sqlfluff.com",
        "Changes": "https://github.com/sqlfluff/sqlfluff/blob/main/CHANGELOG.md",
        "Source": "https://github.com/sqlfluff/sqlfluff",
        "Issue Tracker": "https://github.com/sqlfluff/sqlfluff/issues",
        "Twitter": "https://twitter.com/SQLFluff",
        "Chat": "https://github.com/sqlfluff/sqlfluff#sqlfluff-on-slack",
    },
    packages=["sqlfluff_templater_dbt"],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=["sqlfluff>=0.7.0", "dbt-core>=0.17", "jinja2-simple-tags>=0.3.1"],
    entry_points={"sqlfluff": ["sqlfluff_templater_dbt = sqlfluff_templater_dbt"]},
)
