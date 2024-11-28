.. _gettingstartedref:

Getting Started
===============

To get started with *SQLFluff* you'll need python and pip installed
on your machine, if you're already set up, you can skip straight to
`Installing sqlfluff`_.

Installing Python
-----------------

How to install *python* and *pip* depends on what operating system
you're using. In any case, the python wiki provides up to date
`instructions for all platforms here`_.

There's a chance that you'll be offered the choice between python
versions. Support for python 2 was dropped in early 2020, so you
should always opt for a version number starting with a 3. As for
more specific options beyond that, *SQLFluff* aims to be compatible
with all current python versions, and so it's best to pick the most
recent.

You can confirm that python is working as expected by heading to
your terminal or console of choice and typing :code:`python --version`
which should give you a sensible read out and not an error.

.. code-block:: text

    $ python --version
    Python 3.9.1

For most people, their installation of python will come with
:code:`pip` (the python package manager) preinstalled. To confirm
this you can type :code:`pip --version` similar to python above.

.. code-block:: text

    $ pip --version
    pip 21.3.1 from ...

If however, you do have python installed but not :code:`pip`, then
the best instructions for what to do next are `on the python website`_.

.. _`instructions for all platforms here`: https://wiki.python.org/moin/BeginnersGuide/Download
.. _`on the python website`: https://pip.pypa.io/en/stable/installation/

.. _installingsqlfluff:

Installing SQLFluff
-------------------

Assuming that python and pip are already installed, then installing
*SQLFluff* is straight forward.

.. code-block:: text

    $ pip install sqlfluff

You can confirm its installation by getting *SQLFluff* to show its
version number.

.. code-block:: text

    $ sqlfluff version
    3.3.0

Basic Usage
-----------

To get a feel for how to use *SQLFluff* it helps to have a small
:code:`.sql` file which has a simple structure and some known
issues for testing. Create a file called :code:`test.sql` in the
same folder that you're currently in with the following content:

.. code-block:: sql

    SELECT a+b  AS foo,
    c AS bar from my_table

You can then run :code:`sqlfluff lint test.sql --dialect ansi` to lint this
file.

.. code-block:: text

    $ sqlfluff lint test.sql --dialect ansi
    == [test.sql] FAIL
    L:   1 | P:   1 | LT09 | Select targets should be on a new line unless there is
                           | only one select target.
                           | [layout.select_targets]
    L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                           | and aggregates. [structure.column_order]
    L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                           | [layout.indent]
    L:   1 | P:   9 | LT01 | Expected single whitespace between naked identifier and
                           | binary operator '+'. [layout.spacing]
    L:   1 | P:  10 | LT01 | Expected single whitespace between binary operator '+'
                           | and naked identifier. [layout.spacing]
    L:   1 | P:  11 | LT01 | Expected only single space before 'AS' keyword. Found '
                           | '. [layout.spacing]
    L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                           | [layout.indent]
    L:   2 | P:   9 | LT02 | Expected line break and no indent before 'from'.
                           | [layout.indent]
    L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                           | [capitalisation.keywords]
    All Finished 📜 🎉!

You'll see that *SQLFluff* has failed the linting check for this file.
On each of the following lines you can see each of the problems it has
found, with some information about the location and what kind of
problem there is. One of the errors has been found on *line 1*, *position *
(as shown by :code:`L:   1 | P:   9`) and it's a problem with rule
*LT01* (for a full list of rules, see :ref:`ruleref`). From this
(and the following error) we can see that the problem is that there
is no space either side of the :code:`+` symbol in :code:`a+b`.
Head into the file, and correct this issue so that the file now
looks like this:

.. code-block:: sql

    SELECT a + b  AS foo,
    c AS bar from my_table

Rerun the same command as before, and you'll see that the original
error (violation of *LT01*) no longer shows up.

.. code-block:: text

    $ sqlfluff lint test.sql --dialect ansi
    == [test.sql] FAIL
    L:   1 | P:   1 | LT09 | Select targets should be on a new line unless there is
                           | only one select target.
                           | [layout.select_targets]
    L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                           | and aggregates. [structure.column_order]
    L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                           | [layout.indent]
    L:   1 | P:  13 | LT01 | Expected only single space before 'AS' keyword. Found '
                           | '. [layout.spacing]
    L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                           | [layout.indent]
    L:   2 | P:   9 | LT02 | Expected line break and no indent before 'from'.
                           | [layout.indent]
    L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                           | [capitalisation.keywords]

To fix the remaining issues, we're going to use one of the more
advanced features of *SQLFluff*, which is the *fix* command. This
allows more automated fixing of some errors, to save you time in
sorting out your sql files. Not all rules can be fixed in this way
and there may be some situations where a fix may not be able to be
applied because of the context of the query, but in many simple cases
it's a good place to start.

For now, we only want to fix the following rules: *LT02*, *LT12*, *CP01*

.. code-block:: text

    $ sqlfluff fix test.sql --rules LT02,LT12,CP01 --dialect ansi
    ==== finding violations ====
    == [test.sql] FAIL
    L:   1 | P:   7 | LT02 | Expected line break and indent of 4 spaces before 'a'.
                           | [layout.indent]
    L:   2 | P:   1 | LT02 | Expected indent of 4 spaces.
                           | [layout.indent]
    L:   2 | P:   9 | LT02 | Expected line break and no indent before 'FROM'.
                           | [layout.indent]
    L:   2 | P:  10 | CP01 | Keywords must be consistently upper case.
                           | [capitalisation.keywords]
    ==== fixing violations ====
    4 fixable linting violations found
    Are you sure you wish to attempt to fix these? [Y/n]

...at this point you'll have to confirm that you want to make the
changes by pressing :code:`y` on your keyboard...

.. code-block:: text

    Are you sure you wish to attempt to fix these? [Y/n] ...
    Attempting fixes...
    Persisting Changes...
    == [test.sql] PASS
    Done. Please check your files to confirm.

If we now open up :code:`test.sql`, we'll see the content is
now different.

.. code-block:: sql

    SELECT
        a + b  AS foo,
        c AS bar
    FROM my_table

In particular:

* The two columns have been indented to reflect being inside the
  :code:`SELECT` statement.
* The :code:`FROM` keyword has been capitalised to match the
  other keywords.

We could also fix *all* of the fixable errors by not
specifying :code:`--rules`.

.. code-block:: text

    $ sqlfluff fix test.sql --dialect ansi
    ==== finding violations ====
    == [test.sql] FAIL
    L:   1 | P:   1 | ST06 | Select wildcards then simple targets before calculations
                           | and aggregates. [structure.column_order]
    L:   2 | P:  10 | LT01 | Expected only single space before 'AS' keyword. Found '
                           | '. [layout.spacing]
    ==== fixing violations ====
    2 fixable linting violations found
    Are you sure you wish to attempt to fix these? [Y/n] ...
    Attempting fixes...
    Persisting Changes...
    == [test.sql] PASS
    Done. Please check your files to confirm.

If we now open up :code:`test.sql`, we'll see the content has
been updated again.

.. code-block:: sql

    SELECT
        c AS bar,
        a + b AS foo
    FROM my_table

The SQL statement is now well formatted according to all the
rules defined in SQLFluff.

The :code:`--rules` argument is optional, and could be useful when
you or your organisation follows a slightly different convention
than what we have defined.

Custom Usage
------------

So far we've covered the stock settings of *SQLFluff*, but there
are many different ways that people style their sql, and if you
or your organisation have different conventions, then many of
these behaviours can be configured. For example, given the
example above, what if we actually think that indents should only
be two spaces, and rather than uppercase keywords, they should
all be lowercase?

To achieve this we create a configuration file named :code:`.sqlfluff`
and place it in the same directory as the current file. In that file
put the following content:

.. code-block:: cfg

    [sqlfluff]
    dialect = ansi

    [sqlfluff:indentation]
    tab_space_size = 2

    [sqlfluff:rules:capitalisation.keywords]
    capitalisation_policy = lower

Then rerun the same command as before.

.. code-block:: text

    $ sqlfluff fix test.sql --rules LT02,LT12,CP01,ST06,LT09,LT01

Then examine the file again, and you'll notice that the
file has been fixed accordingly.

.. code-block:: sql

    select
      c as bar,
      a + b as foo
    from my_table

For a full list of configuration options check out :ref:`defaultconfig`.
Note that in our example here we've only set a few configuration values
and any other configuration settings remain as per the default config.
To see how these options apply to specific rules check out the
"Configuration" section within each rule's documentation in :ref:`ruleref`.

Going further
-------------

From here, there are several more things to explore.

* To understand how *SQLFluff* is interpreting your file
  explore the :code:`parse` command. You can learn more about
  that command and more by running :code:`sqlfluff --help` or
  :code:`sqlfluff parse --help`.
* To start linting more than just one file at a time, experiment
  with passing SQLFluff directories rather than just single files.
  Try running :code:`sqlfluff lint .` (to lint every sql file in the
  current folder) or :code:`sqlfluff lint path/to/my/sqlfiles`.
* To find out more about which rules are available, see :ref:`ruleref`.
* To find out more about configuring *SQLFluff* and what other options
  are available, see :ref:`config`.
* Once you're ready to start using *SQLFluff* on a project or with the
  rest of your team, check out :ref:`production-use`.

One last thing to note is that *SQLFluff* is a relatively new project
and you may find bugs or strange things while using it. If you do find
anything, the most useful thing you can do is to `post the issue on
GitHub`_ where the maintainers of the project can work out what to do with
it. The project is in active development and so updates and fixes may
come out regularly.

.. _`post the issue on GitHub`: https://github.com/sqlfluff/sqlfluff/issues
