"""Testing utils for working with the CLIs."""

import inspect
from typing import Any, Optional

from click.testing import CliRunner, Result


def invoke_assert_code(
    ret_code: int = 0,
    args: Optional[list[Any]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    cli_input: Optional[str] = None,
    assert_stdout_contains: str = "",
    assert_stderr_contains: str = "",
    raise_exceptions: bool = True,
) -> Result:
    """Invoke a command and check return code."""
    args = args or []
    kwargs = kwargs or {}
    if cli_input:
        kwargs["input"] = cli_input
    if "mix_stderr" in inspect.signature(CliRunner).parameters:  # pragma: no cover
        runner = CliRunner(mix_stderr=False)  # type: ignore[call-arg,unused-ignore]
    else:  # pragma: no cover
        runner = CliRunner()
    result = runner.invoke(*args, **kwargs)
    # Output the CLI code for debugging
    print(result.output)
    if assert_stdout_contains != "":
        # The replace command just accounts for cross platform testing.
        assert assert_stdout_contains in result.stdout.replace("\\", "/")
    if assert_stderr_contains != "":
        # The replace command just accounts for cross platform testing.
        assert assert_stderr_contains in result.stderr.replace("\\", "/")
    # Check return codes, and unless we specifically want to pass back exceptions,
    # we should raise any exceptions which aren't `SystemExit` ones (i.e. ones
    # raised by `sys.exit()`)
    if raise_exceptions and result.exception:
        if not isinstance(result.exception, SystemExit):
            raise result.exception  # pragma: no cover
    assert ret_code == result.exit_code
    return result
