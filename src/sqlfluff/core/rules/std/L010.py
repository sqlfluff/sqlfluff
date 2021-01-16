"""Implementation of Rule L010."""

from typing import Tuple, List
from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L010(BaseCrawler):
    """Inconsistent capitalisation of keywords.

    | **Anti-pattern**
    | In this example, 'select 'is in lower-case whereas 'FROM' is in upper-case.

    .. code-block:: sql

        select
            a
        FROM foo

    | **Best practice**
    | Make all keywords either in upper-case or in lower-case

    .. code-block:: sql

        SELECT
            a
        FROM foo

        -- Also good

        select
            a
        from foo
    """

    # Binary operators behave like keywords too.
    _target_elems: List[Tuple[str, str]] = [
        ("type", "keyword"),
        ("type", "binary_operator"),
    ]
    config_keywords = ["capitalisation_policy"]

    def _eval(self, segment, memory, **kwargs):
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        cases_seen = memory.get("cases_seen", set())

        if ("type", segment.type) in self._target_elems or (
            "name",
            segment.name,
        ) in self._target_elems:
            raw = segment.raw
            uc = raw.upper()
            lc = raw.lower()
            cap = raw.capitalize()
            seen_case = None
            if uc == lc:
                # Caseless
                pass
            elif raw == uc:
                seen_case = "upper"
            elif raw == lc:
                seen_case = "lower"
            elif raw == cap:
                seen_case = "capitalise"
            else:
                seen_case = "inconsistent"

            # NOTE: We'll only add to cases_seen if we DON'T
            # also raise an error, so that we can focus in.

            def make_replacement(seg, policy):
                """Make a replacement segment, based on seen capitalisation."""
                if policy == "lower":
                    new_raw = seg.raw.lower()
                elif policy == "upper":
                    new_raw = seg.raw.upper()
                elif policy == "capitalise":
                    new_raw = seg.raw.capitalize()
                elif policy == "consistent":
                    # The only case we DON'T allow here is "inconsistent",
                    # because it doesn't actually help us.
                    filtered_cases_seen = [c for c in cases_seen if c != "inconsistent"]
                    if filtered_cases_seen:
                        # Get an element from what we've already seen.
                        return make_replacement(seg, list(filtered_cases_seen)[0])
                    else:
                        # If we haven't seen anything yet, then let's default
                        # to upper
                        return make_replacement(seg, "upper")
                # Make a new class and return it.
                return seg.__class__(raw=new_raw, pos_marker=seg.pos_marker)

            if not seen_case:
                # Skip this if we haven't seen anything good.
                # No need to update memory
                return LintResult(memory=memory)
            elif (
                # Are we required to be consistent? (and this is inconsistent?)
                (
                    self.capitalisation_policy == "consistent"
                    and (
                        # Either because we've seen multiple
                        (cases_seen and seen_case not in cases_seen)
                        # Or just because this one is inconsistent internally
                        or seen_case == "inconsistent"
                    )
                )
                # Are we just required to be specific?
                # Policy is either upper, lower or capitalize
                or (
                    self.capitalisation_policy != "consistent"
                    and seen_case != self.capitalisation_policy
                )
            ):
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix(
                            "edit",
                            segment,
                            make_replacement(segment, self.capitalisation_policy),
                        )
                    ],
                    memory=memory,
                )
            else:
                # Update memory and carry on
                cases_seen.add(seen_case)
                memory["cases_seen"] = cases_seen
                return LintResult(memory=memory)

        # If it's not a keyword just carry on
        return LintResult(memory=memory)
