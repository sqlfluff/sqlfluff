.. _developing_custom_rules:

Developing Custom Rules
=======================

It's quite common to have organisation-, or project-specific norms and
conventions you might want to enforce using SQLFluff. With a little bit
of python knowledge this is very achievable with SQLFluff, and there's
a plugin architecture to support that.

This guide should be read alongside the code for the
`SQLFluff example plugin`_ and the more technical documentation for
:ref:`developingpluginsref`.

What Plugin do I need?
----------------------

When thinking about developing a rule, the following thought process will
help you decide what to develop:

1. When do I want this rule to show a warning, when should it definitely
   **not** show one? What information do I need when evaluating whether
   a the rule has been followed or not? This information will tell you
   about the two important *locations* in the parse tree which will become
   important.

   * The *trigger* location: i.e. when should the rule be *called* for
     evaluation. e.g. :sqlfluff:ref:`CP01` triggers on keywords, because
     it only needs the information about that keyword to run, but
     :sqlfluff:ref:`LT08` triggers on ``WITH`` statements even though it's
     only interested in specific pieces of whitespace, because it needs the
     full context of the statement to evaluate. You may with to examine the
     parse structure of some example queries you'd want to handle by using
     ``sqlfluff parse my_file.sql`` to identify the right segment. This is
     then specified using the ``crawl_behaviour`` attribute on the rule.

   * The *anchor* location: i.e. which position will show up in the CLI
     readout back to the user. To continue the example of above, while
     :sqlfluff:ref:`LT08` *triggers* on a ``WITH`` statement, it *anchors*
     on a more specific segment just after where it expected whitespace.
     It specifies this using the ``anchor`` argument to the
     :py:class:`~sqlfluff.core.rules.base.LintResult` object.

2. How should the rule evaluate and should I implement an auto-fix? For
   the simplest rules, it the logic to evaluate whether there's an issue
   can be *very simple*. For example in the `SQLFluff example plugin`_,
   we are just checking the name of an element isn't in a configured list.
   Typically we recommend that for organisation-specific rules, **KEEP IT**
   **SIMPLE**. Some of the rules bundled with SQLFluff contain a lot of
   complexity for handling how to automatically fix lots of edge cases,
   but for your organisation it's probably not worth the overhead unless
   you're a **very big team** or **come across a huge amount of poorly**
   **formatted SQL**.

   * Consider the information not just to *trigger*, but also whether a
     custom error message would be appropriate and how to get the information
     to construct that too. The default error message will be the first
     line of the rule docstring_. Custom messages can be configured by
     setting the ``description`` argument of the
     :py:class:`~sqlfluff.core.rules.base.LintResult` object.

   * Do use the existing SQLFluff core rules as examples of what is possible
     and how to achieve various things - but remember that many of them
     implement a level of complexity and edge case handling which may not
     be necessary for your organisation.

3. How am I going to roll out my rule to the team? Thinking through this
   aspect of rule development is just as important as the technical aspect.
   Spending a lot of time on rule development for it to be rejected by
   the end users of it is both a waste of time and also counterproductive.

   * Consider manually fixing any pre-existing issues in your project which
     would trigger the rule before rollout.

   * Seek consensus on how strictly the rule will be enforced and what the
     step by step pathway is to strict enforcement.

   * Consider *beta-testing* your new rule with a smaller group of users
     who are more engaged with SQLFluff or code quality in general.

.. _docstring:  https://en.wikipedia.org/wiki/Docstring

Plugin Discovery
----------------

One of most common questions asked with respect to custom plugins is
*discovery*, or *"how do I tell SQLFluff where my plugin is"*. SQLFluff
uses pluggy_ as it's plugin architecture (developed by the folks at pytest_).
Pluggy uses the python packaging metadata for plugin discovery. This means
that **your plugin must be installed as a python package for discovery**.
Specifically, it must define an `entry point`_ for SQLFluff.
When SQLFluff runs, it inspects installed python packages for this entry
point and then can run any which define one. For example you'll see in the
`SQLFluff example plugin`_ that the ``pyproject.toml`` file has the
following section:

.. code-block:: toml

   [project.entry-points.sqlfluff]
   # Change this name in your plugin, e.g. company name or plugin purpose.
   sqlfluff_example = "sqlfluff_plugin_example"

You can find equivalent examples for ``setup.cfg`` and ``setup.py`` in the
python docs for `entry point`_. This information is registered
*on install* of your plugin, (i.e. when running `pip install`, or equivalent
if you're using a different package manager) so if you change it later, you
may need to re-install your plugin.

You can test whether your rule has been successfully discovered by running
``sqlfluff rules`` and reviewing whether your new rule has been included in
the readout.

.. note::
    If you're struggling with rule discovery, **use the example plugin**.
    It can be much easier to take a known working example and then modify
    from there:

    1. Copy the code from the `SQLFluff example plugin`_ into a local
       folder.

    2. Run `pip install -e /path/to/where/you/put/it`.

    3. Run `sqlfluff rules`, to confirm that the example plugin is present
       to demonstrate to yourself that discovery is functional.

    4. Then edit the example plugin to do what you want now that discovery
       isn't an issue. You may have to re-run `pip install ...` if you
       change anything in the rule metadata (like the entry point, filenames
       or plugin location).

.. _pluggy: https://pluggy.readthedocs.io/en/latest/
.. _pytest: https://docs.pytest.org/en/stable/
.. _`entry point`: https://setuptools.pypa.io/en/stable/userguide/entry_point.html
.. _`SQLFluff example plugin`: https://github.com/sqlfluff/sqlfluff/tree/main/plugins/sqlfluff-plugin-example
