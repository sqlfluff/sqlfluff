Using SQLFluff directly as a CLI application
--------------------------------------------

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

.. _`exit code`: https://shapeshed.com/unix-exit-codes/
