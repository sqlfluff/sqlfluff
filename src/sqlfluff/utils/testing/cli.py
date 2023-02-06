"""Testing utils for working with the CLIs."""
from click.testing import CliRunner


def invoke_assert_code(
    ret_code=0,
    args=None,
    kwargs=None,
    cli_input=None,
    mix_stderr=True,
    output_contains="",
):
    """Invoke a command and check return code."""
    args = args or []
    kwargs = kwargs or {}
    if cli_input:
        kwargs["input"] = cli_input
    runner = CliRunner(mix_stderr=mix_stderr)
    result = runner.invoke(*args, **kwargs)
    # Output the CLI code for debugging
    print(result.output)
    # Check return codes
    if output_contains != "":
        assert output_contains in result.output
    if ret_code == 0:
        if result.exception:
            raise result.exception
    assert ret_code == result.exit_code
    return result
