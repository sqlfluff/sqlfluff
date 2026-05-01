.. _templater_variant_rendering:

Template Variant Rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^

SQLFluff normally lints the rendered SQL produced by a templater. For a template
with control flow such as :code:`if` or :code:`for`, a single render can only
exercise one path through that template.

Template variant rendering allows SQLFluff to render multiple versions of the
same source file and combine the linting results. This improves coverage for
templated SQL by allowing SQLFluff to inspect branches that would otherwise stay
unreached in a single render.

This currently matters most for the :ref:`jinja_templater` and
:ref:`dbt_templater`, because they can contain conditional branches which change
the rendered SQL substantially.

How It Works
""""""""""""

At a high level, SQLFluff:

#. Renders the template once using the configured templater context.
#. Identifies literal slices in the source file that were not reached in that
   render.
#. Generates additional renderings designed to cover those unreached areas.
#. Lints the returned variants and maps the resulting violations back onto the
   original source file.

This does **not** guarantee exhaustive coverage of every possible branch
combination. Instead, it is a practical best-effort mechanism which improves
lint coverage while keeping runtime bounded.

Note that in cases where no other variants can be generated, the performance
impact is minimal as variants are only linted if they are meaningfully different
from the primary render. In cases where many variants are generated, the performance
impact can be more substantial.

Configuration
"""""""""""""

Variant rendering is controlled by the top-level
:code:`render_variant_limit` setting:

.. code-block:: cfg

    [sqlfluff]
    render_variant_limit = 5

This is the maximum number of rendered variants SQLFluff will lint for a single
file, including the primary render.

Recommended values:

* :code:`1`: Disable additional variant rendering and restore the historical
  single-render behaviour.
* :code:`5`: Default. A moderate setting which improves branch coverage without
  opening the search space too aggressively.
* Higher values: Useful for heavily branched templates, but can increase
  templating and linting time noticeably.

When To Use It
""""""""""""""

Variant rendering is most useful when your templated SQL contains control flow
that changes the SQL structure, for example:

* :code:`{% if %}` / :code:`{% elif %}` / :code:`{% else %}` blocks
* conditional :code:`WHERE`, :code:`JOIN`, or :code:`SELECT` fragments
* dbt models whose branches produce different SQL layouts

If your templates are mostly simple substitutions, macros, or library calls,
variant rendering is less likely to change lint coverage.

Limitations
"""""""""""

There are still some important limits:

* SQLFluff does not attempt to enumerate every possible execution path.
* Additional variants are capped by :code:`render_variant_limit`.
* Support depends on the templater implementation. Jinja-derived templaters,
  including dbt, currently provide the most meaningful support.
* More variants mean more work, so runtime and the number of surfaced issues can
  increase.
* Some templater errors may still be repeated across variants while the feature
  continues to mature.

Practical Guidance
""""""""""""""""""

Start with the default and only tune upward if you have concrete examples where
important branches are still being missed.

If you are debugging surprising output, temporarily setting
:code:`render_variant_limit = 1` is a useful way to compare current behaviour
with the old single-render model.

For teams using the :ref:`dbt_templater`, this setting complements the existing
dbt configuration rather than replacing it. Accurate dbt rendering still depends
on project, profile, and macro configuration.
