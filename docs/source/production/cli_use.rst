Using SQLFluff directly as a CLI application
--------------------------------------------

The :ref:`SQLFluff CLI application <cliref>` is a python application which
means if depends on your host python environment
(see :ref:`installingsqlfluff`).

The `exit code`_ provided by SQLFluff when run as a command line utility is
designed to assist usefulness in deployment pipelines. If no violations
are found then the `exit code`_ will be 0. If violations are found then
a non-zero code will be returned which can be interrogated to find out
more.

- An error code of ``0`` means *operation success*, *no issues found*.
- An error code of ``1`` means *operation success*, *issues found*. For
  example this might mean that a linting issue was found, or that one file
  could not be parsed.
- An error code of ``2`` means an error occurred and the operation could
  not be completed. For example a configuration issue or an internal error
  within SQLFluff.

For details of what commands and options are available in the CLI see the
:ref:`cliref`.

.. _`exit code`: https://shapeshed.com/unix-exit-codes/
