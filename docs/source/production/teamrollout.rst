.. _rolloutref:

Rolling out SQLFluff with a new team
====================================

Rolling out SQLFluff, like rolling out any other linter or style
guide, is not just about the *technical* rollout, but also
how you introduce the tool to the team and organisation around
you.

   *The effect of SQLFluff should be to change your behaviours, not*
   *just your SQL*.

With that in mind, it's worth reminding ourselves what we're trying
to achieve with a tool like this. A set of potential success criteria
might be:

#. **Faster comprehension and collaboration** by the team on a shared
   codebase. This includes more effective (and more enjoyable) code
   review on top of code which is easy to review and build upon.
#. **Easier and faster onboarding** for new team members. By adopting
   a style which is clean and *consistent with other organisations*
   we make it easier for new people to join the team.
#. **Improved adoption of shared SQL** from other sources. If the SQL
   found in open source projects is easy to read and *looks familiar*
   then you're more likely to use it. This means more reusable code
   across the industry.
#. **Productive discussions around style**. By defining your
   organisation's style guide in code, it means you can version
   control it, discuss changes and ultimately give a concrete output
   to discussions over style.

   *You like leading commas? Make a PR to .sqlfluff and let's*
   *discuss with the team what the implications would be*.

Consider which of these success measures is most important and most
desirable for your team. *Write that down*.

The following steps are a guide, which you should adapt to your
organisation, and in particular its level of data maturity.

1. Assess the situation
-----------------------

This step is done by you, or a small group of people who *already*
*think that linting is a good idea*.

* Run ``sqlfluff lint`` on your project with the stock configuration
  to find out how things work *out of the box*.
* Set up your :ref:`config` so that things run and that you can get
  a readout of the errors which you would want the team to see and
  *not the ones you don't*. Great tools for this are to use
  :ref:`sqlfluffignore`, ``--exclude-rules`` or ``--ignore`` in the
  CLI (see :ref:`cliref`).
* Identify which areas of your project are the worst and which are the
  tidiest. In particular, any areas which are particularly tidy
  already will be particularly useful in the next phase.

2. Make a plan
--------------

There are three sensible rollout phases:

#. **Pre CI/CD**.
#. **Soft CI/CD** (warnings but no strict fails).
#. **Hard CI/CD** (violations mean deployments fail).

In each of these phases you have three levers to play with:

#. Areas of the project in which to apply rules.
#. Depth of rules enforced (this might also include whether
   to ignore parsing errors or not).
#. Whether to just lint changes (:ref:`diff-quality`),
   or to lint all the existing code as well.

Work out a sensible roadmap of how hard you want to go in
each phase. Be clear who is responsible for changes at each
phase. An example plan might look like this:

#. **Pre CI/CD** we get the tidiest area of a project
   to a stage that it fully passes the rules we eventually want to enforce.
   The core project team will do this. Liberal use of
   ``sqlfluff fix`` can be a lifesaver in this phase.
#. **Soft CI/CD** is applied to the whole project, team
   members are encouraged to write tidy SQL, but not *required* to.
#. **Hard CI/CD** is applied to the tidy areas of the project
   and also to any changes to the whole project. Anyone
   making changes is *required* to write SQL which passes check.
#. **Hard CI/CD** is applied to the whole project on not just
   changes, with only a few particularly problematic files
   explicitly ignored using :ref:`sqlfluffignore`.

3. Build the need
-----------------

Bring your team together to introduce both linting as a concept
and also SQLFluff as a tool. At this stage it's **really important**
**that the team understand *why* this is a good thing**.

Consider whether to discuss the whole plan from step 2, or
whether to only talk about the first few steps. Aim to make
this an empowering experience that everyone can get involved with
rather than *another piece of admin they need to do*.

At this stage, you might also want to consider other tools in the
SQLFluff ecosystem such as the :ref:`SQLFluff pre-commit hook
<using-pre-commit>` and the `SQLFluff VSCode plugin`_ or `SQLFluff
online formatter`_.

.. _`SQLFluff VSCode plugin`: https://github.com/sqlfluff/vscode-sqlfluff
.. _`SQLFluff online formatter`: https://online.sqlfluff.com/

4. Do, Review & Reassess
------------------------

Once the plan is in motion, make sure to start putting in place
norms and rituals around how you change the rules. In particular:

* How would someone suggest changing the style guide or
  enabling/disabling a rule?
* How do we assess whether the changes are working for the team
  or whether some are creating unnecessary stress?

It's normal for your usage of tools like SQLFluff to change and
evolve over time. It's important to expect this change in advance,
and welcome it when it happens. Always make sure you're driving
toward the success measures you decided up front, rather than
just resisting the change.

5. Spread the word 😁
---------------------

Did it work? If so, spread the word. Tell a friend about SQLFluff.

If you're lucky they might share your views on comma placement 🤷‍♀️.
