# Introduction

Bored of not having a good SQL linter that works with whichever dialect
you're working with? Fluff is an extensible and modular linter designed
to help you write good SQL and catch errors and bad SQL before it hits
your database.


To get started just install the package, make a sql file and then run
SQLFluff and point it at the file. For more details or if you don't
have python or pip already installed see the [installation guide](./install).

```bash
pip install sqlfluff
echo "  SELECT a  +  b FROM tbl;  " > test.sql
sqlfluff lint test.sql --dialect ansi

    == [test.sql] FAIL
    L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                           | Found '  '. [layout.spacing]
    L:   1 | P:   1 | LT02 | First line should not be indented.
                           | [layout.indent]
    L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                           | [layout.start_of_file]
    L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                           | Found '  '. [layout.spacing]
    L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                           | Found '  '. [layout.spacing]
    L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                           | [layout.spacing]
    L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                           | [layout.end_of_file]
    All Finished 📜 🎉!
```

## Why SQLFluff?

SQL has been around for a long time, as a language for communicating
with databases, like a communication protocol. More recently with the
rise of *data* as a business function, or a domain in its own right
SQL has also become an invaluable tool for defining the *structure* of
data and analysis - not just as a one off but as a form of
[infrastructure as code](https://en.wikipedia.org/wiki/Infrastructure_as_code).

As *analytics* transitions from a profession of people doing one-offs,
and moves to building stable and reusable pieces of analytics, more and
more principles from software engineering are moving in the analytics
space. One of the best articulations of this is written in the
[viewpoint section of the docs for the open-source tool dbt](https://docs.getdbt.com/docs/viewpoint). Two of
the principles mentioned in that article are `quality assurance`_ and
[modularity](https://docs.getdbt.com/docs/viewpoint#modularity).

### Quality assurance

The primary aim of `SQLFluff` as a project is in service of that first
aim of [quality assurance](https://docs.getdbt.com/docs/viewpoint#quality-assurance). With larger and larger teams maintaining
large bodies of SQL code, it becomes more and more important that the
code is not just *valid* but also easily *comprehensible* by other users
of the same codebase. One way to ensure readability is to enforce a
[consistent style](https://www.smashingmagazine.com/2012/10/why-coding-style-matters/), and the tools used to do this are called [linters](https://en.wikipedia.org/wiki/Lint_(software)).

Some famous [linters](https://en.wikipedia.org/wiki/Lint_(software)) which are well known in the software community are
[flake8](http://flake8.pycqa.org/) and [jslint](https://www.jslint.com/) (the former is used to lint the `SQLFluff` project
itself).

**SQLFluff** aims to fill this space for SQL.

### Modularity

SQL itself doesn't lend itself well to `modularity`_, so to introduce
some flexibility and reusability it is often [templated](https://en.wikipedia.org/wiki/Template_processor). Typically
this is done in the wild in one of the following ways:

1. Using the limited inbuilt templating abilities of a programming
   language directly. For example in python this would be using the
   [format string syntax](https://docs.python.org/3/library/string.html#formatstrings):

    ```python
      "SELECT {foo} FROM {tbl}".format(foo="bar", tbl="mytable")
    ```

   Which would evaluate to:

   ```sql
      SELECT bar FROM mytable
    ```

2. Using a dedicated templating library such as [jinja2](https://jinja.palletsprojects.com/). This allows
   a lot more flexibility and more powerful expressions and macros. See
   the [templating section](#templating) for more detail on how this works.

   - Often there are tools like [dbt](https://getdbt.com) or [apache airflow](https://airflow.apache.org) which allow
     [templated](https://en.wikipedia.org/wiki/Template_processor) sql to be used directly, and they will implement a
     library like [jinja2](https://jinja.palletsprojects.com/) under the hood themselves.


All of these templating tools are great for `modularity`_ but they also
mean that the SQL files themselves are no longer valid SQL code, because
they now contain these configured *placeholder* values, intended to
improve modularity.

SQLFluff supports both of the templating methods outlined above,
as well as [dbt](https://getdbt.com) projects, to allow you to still lint these
"dynamic" SQL files as part of your CI/CD pipeline (which is great 🙌),
rather than waiting until you're in production (which is bad 🤦,
and maybe too late).

During the CI/CD pipeline (or any time that we need to handle [templated](https://en.wikipedia.org/wiki/Template_processor)
code), SQLFluff needs additional info in order to interpret your templates
as valid SQL code. You do so by providing dummy parameters in SQLFluff
configuration files. When substituted into the template, these values should
evaluate to valid SQL (so SQLFluff can check its style, formatting, and
correctness), but the values don't need to match actual values used in
production. This means that you can use *much simpler* dummy values than
what you would really use. The recommendation is to use *the simplest*
possible dummy value that still allows your code to evaluate to valid SQL
so that the configuration values can be as streamlined as possible.

### Vision for SQLFluff

SQLFluff has a few components:

1. A generic parser for SQL which aims to be able to unify SQL written
   in different dialects into a comparable format. The *parser*.
2. A mechanism for measuring written SQL against a set of rules, with
   the added ability to fix any violations found. The *linter*.
3. An opinionated set of guidelines for how SQL should be structured
   and formatted. The *rules*.

The core vision for SQLFluff is to be really good at being the *linter*.
The reasoning for this is outlined in :ref:`why_sqlfluff`.

::: tip NOTE
Credit [to this article](https://opensource.com/business/16/6/bad-practice-foss-projects-management) for highlighting the importance of a good vision.
:::

Most of the codebase for SQLFluff is the *parser*, mostly because at
the point of developing SQLFluff, there didn't appear to be a good
option for a whitespace-aware parser that could be used instead.

With regards to the *rules*, SQLFluff aims to be opinionated but it
also accepts that many organisations and groups have pre-existing
strong conventions around how to write SQL and so ultimately SQLFluff
should be flexible enough to support whichever rule set a user wishes
to.
