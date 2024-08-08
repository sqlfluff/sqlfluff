"""Testing utils for working with the CLIs."""

from typing import Any, Dict, List, Optional

from click.testing import CliRunner, Result


def invoke_assert_code(
    ret_code: int = 0,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    cli_input: Optional[str] = None,
    mix_stderr: bool = True,
    assert_output_contains: str = "",
    raise_exceptions: bool = True,
) -> Result:
    """Invoke a command and check return code."""
    args = args or []
    kwargs = kwargs or {}
    if cli_input:
        kwargs["input"] = cli_input
    runner = CliRunner(mix_stderr=mix_stderr)
    result = runner.invoke(*args, **kwargs)
    # Output the CLI code for debugging
    print(result.output)
    if assert_output_contains != "":
        # The replace command just accounts for cross platform testing.
        assert assert_output_contains in result.output.replace("\\", "/")
    # Check return codes, and unless we specifically want to pass back exceptions,
    # we should raise any exceptions which aren't `SystemExit` ones (i.e. ones
    # raised by `sys.exit()`)
    if raise_exceptions and result.exception:
        if not isinstance(result.exception, SystemExit):
            raise result.exception  # pragma: no cover
    assert ret_code == result.exit_code
    return result
