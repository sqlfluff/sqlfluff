"""Define FunctionalContext class."""

from sqlfluff.core.rules import RuleContext
from sqlfluff.utils.functional.segments import Segments


class FunctionalContext:
    """RuleContext written in a "functional" style; simplifies writing rules."""

    def __init__(self, context: RuleContext):
        self.context = context

    @property
    def segment(self) -> "Segments":
        """Returns a Segments object for context.segment."""
        return Segments(
            self.context.segment, templated_file=self.context.templated_file
        )

    @property
    def parent_stack(self) -> "Segments":  # pragma: no cover
        """Returns a Segments object for context.parent_stack."""
        return Segments(
            *self.context.parent_stack, templated_file=self.context.templated_file
        )

    @property
    def siblings_pre(self) -> "Segments":  # pragma: no cover
        """Returns a Segments object for context.siblings_pre."""
        return Segments(
            *self.context.siblings_pre, templated_file=self.context.templated_file
        )

    @property
    def siblings_post(self) -> "Segments":  # pragma: no cover
        """Returns a Segments object for context.siblings_post."""
        return Segments(
            *self.context.siblings_post, templated_file=self.context.templated_file
        )

    @property
    def raw_stack(self) -> "Segments":  # pragma: no cover
        """Returns a Segments object for context.raw_stack."""
        return Segments(
            *self.context.raw_stack, templated_file=self.context.templated_file
        )

    @property
    def raw_segments(self) -> Segments:  # pragma: no cover
        """Returns a Segments object for all the raw segments in the file."""
        file_segment = self.context.parent_stack[0]
        return Segments(
            *file_segment.get_raw_segments(), templated_file=self.context.templated_file
        )
