"""These Exceptions are for unexpected errors relating to configuration and the sqlfluff context (macros, variables).

For "violations", or "common usage errors" such as parsing errors, refer
to sqlfluff/errors.py
"""


class MacroExtractError(Exception):
    """When loading macros fails."""
    def __init__(self, message=None):
        Exception.__init__(self, message)

    @property
    def message(self):
        """Error details."""
        if self.args:
            message = self.args[0]
            if message is not None:
                return message
