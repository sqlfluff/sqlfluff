.. _why_sqlfluff:

Why SQLFluff?
=============

SQL has been around for a long time, as a language for communicating
with databases, like a communication protocol. More recently with the
rise of *data* as a business function, or a domain in its own right
SQL has also become an invaluable tool for defining the *structure* of
data and analysis - not just as a one off but as a form of
`infrastructure as code`_.

As *analytics* transitions from a profession of people doing one-offs,
and moves to building stable and reusable pieces of analytics, more and
more principles from software engineering are moving in the analytics
space. One of the best articulations of this is written in the
`viewpoint section of the docs for the open-source tool dbt`_. Two of
the principles mentioned in that article are `quality assurance`_ and
`modularity`_.

Quality assurance
-----------------

The primary aim of `SQLFluff` as a project is in service of that first
aim of `quality assurance`_. With larger and larger teams maintaining
large bodies of SQL code, it becomes more and more important that the
code is not just *valid* but also easily *comprehensible* by other users
of the same codebase. One way to ensure readability is to enforce a
`consistent style`_, and the tools used to do this are called `linters`_.

Some famous `linters`_ which are well known in the software community are
`flake8`_ and `jslint`_ (the former is used to lint the `SQLFluff` project
itself).

**SQLFluff** aims to fill this space for SQL.

Modularity
----------

SQL itself doesn't lend itself well to `modularity`_, so to introduce
some flexibility and reusability it is often `templated`_. Typically
this is done in the wild in one of the following ways:

1. Using the limited inbuilt templating abilities of a programming
   language directly. For example in python this would be using the
   `format string syntax`_:

   .. code-block:: python

      "SELECT {foo} FROM {tbl}".format(foo="bar", tbl="mytable")

   Which would evaluate to:

   .. code-block:: sql

      SELECT bar FROM mytable

2. Using a dedicated templating library such as `jinja2`_. This allows
   a lot more flexibility and more powerful expressions and macros. See
   the :ref:`templateconfig` section for more detail on how this works.

   - Often there are tools like `dbt`_ or `apache airflow`_ which allow
     `templated`_ sql to be used directly, and they will implement a
     library like `jinja2`_ under the hood themselves.


All of these templating tools are great for `modularity`_ but they also
mean that the SQL files themselves are no longer valid SQL code, because
they now contain these configured *placeholder* values, intended to
improve modularity.

SQLFluff supports both of the templating methods outlined above,
as well as `dbt`_ projects, to allow you to still lint these
"dynamic" SQL files as part of your CI/CD pipeline (which is great 🙌),
rather than waiting until you're in production (which is bad 🤦,
and maybe too late).

During the CI/CD pipeline (or any time that we need to handle `templated`_
code), SQLFluff needs additional info in order to interpret your templates
as valid SQL code. You do so by providing dummy parameters in SQLFluff
configuration files. When substituted into the template, these values should
evaluate to valid SQL (so SQLFluff can check its style, formatting, and
correctness), but the values don't need to match actual values used in
production. This means that you can use *much simpler* dummy values than
what you would really use. The recommendation is to use *the simplest*
possible dummy value that still allows your code to evaluate to valid SQL
so that the configuration values can be as streamlined as possible.

.. _`infrastructure as code`: https://en.wikipedia.org/wiki/Infrastructure_as_code
.. _`viewpoint section of the docs for the open-source tool dbt`: https://docs.getdbt.com/docs/viewpoint
.. _`quality assurance`: https://docs.getdbt.com/docs/viewpoint#quality-assurance
.. _`modularity`: https://docs.getdbt.com/docs/viewpoint#modularity
.. _`consistent style`: https://www.smashingmagazine.com/2012/10/why-coding-style-matters/
.. _`linters`: https://en.wikipedia.org/wiki/Lint_(software)
.. _`flake8`: http://flake8.pycqa.org/
.. _`jslint`: https://www.jslint.com/
.. _`templated`: https://en.wikipedia.org/wiki/Template_processor
.. _`format string syntax`: https://docs.python.org/3/library/string.html#formatstrings
.. _`jinja2`: https://jinja.palletsprojects.com/
.. _`apache airflow`: https://airflow.apache.org
.. _`dbt`: https://getdbt.com

.. _vision:

Vision for SQLFluff
-------------------

SQLFluff has a few components:

1. A generic parser for SQL which aims to be able to unify SQL written
   in different dialects into a comparable format. The *parser*.
2. A mechanism for measuring written SQL against a set of rules, with
   the added ability to fix any violations found. The *linter*.
3. An opinionated set of guidelines for how SQL should be structured
   and formatted. The *rules*.

The core vision [#f1]_ for SQLFluff is to be really good at being the *linter*.
The reasoning for this is outlined in :ref:`why_sqlfluff`.

Most of the codebase for SQLFluff is the *parser*, mostly because at
the point of developing SQLFluff, there didn't appear to be a good
option for a whitespace-aware parser that could be used instead.

With regards to the *rules*, SQLFluff aims to be opinionated but it
also accepts that many organisations and groups have pre-existing
strong conventions around how to write SQL and so ultimately SQLFluff
should be flexible enough to support whichever rule set a user wishes
to.

.. rubric:: Notes

.. [#f1] Credit to `this article`_ for highlighting the importance of a
   good vision.

.. _`this article`: https://opensource.com/business/16/6/bad-practice-foss-projects-management
