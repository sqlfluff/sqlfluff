"""A Segment Generator.

Used to create Segments upon calling the expand function first.
Helpful when using the sets attribute of the dialect.
"""


class SegmentGenerator:
    """Defines a late-bound dialect object.

    It returns a single dialect object on expansion.

    These are defined using a callable, which is only called
    once everything else is defined. Very useful for template
    inheritance.
    """

    def __init__(self, func):
        self.func = func

    # For all functions, use the function call
    def expand(self, dialect):
        """Expand this object into its true dialect object.

        The inner function is passed an instance of the current dialect
        and so has access to the current sets of that dialect.
        """
        return self.func(dialect)
