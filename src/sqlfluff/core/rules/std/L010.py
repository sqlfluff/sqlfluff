"""Implementation of Rule L010."""

import logging
import re
from typing import Tuple, List
from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.config_info import get_config_info
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
    _consistent_caps: List[str] = ["upper", "lower", "capitalise"]
    config_keywords = ["capitalisation_policy"]

    def _eval(self, segment, memory, **kwargs):
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of cases known to be
        INconsistent with what we've seen so far as well as the top choice
        for what the possible case is.

        """
        refuted_cases = memory.get("refuted_cases", set())
        
        # Skip if not an element of the specified type/name
        if (
                ("type", segment.type) not in self._target_elems
                and ("name", segment.name) not in self._target_elems
            ):
            return LintResult(memory=memory)
        
        # Which cases are definitely inconsistent with the segment?
        if segment.raw[0] != segment.raw[0].upper():
            refuted_cases.update(["upper", "capitalise", "pascal"])
            if segment.raw != segment.raw.lower():
                refuted_cases.update(["lower"])
        else:
            refuted_cases.update(["lower"])
            if segment.raw != segment.raw.upper():
                refuted_cases.update(["upper"])
            if segment.raw != segment.raw.capitalize():
                refuted_cases.update(["capitalise"])
            if not segment.raw.isalnum():
                refuted_cases.update(["pascal"])
        
        # Update the memory
        memory["refuted_cases"] = refuted_cases
        
        logging.debug(f"[L010] Refuted cases after segment '{segment.raw}': "
                      f"{refuted_cases}")
        
        # Skip if no inconsistencies, otherwise compute a concrete policy
        # to convert to.
        if self.capitalisation_policy == "consistent":
            possible_cases = [c for c in self._consistent_caps
                              if c not in refuted_cases]
            logging.debug(f"[L010] Possible cases after segment "
                          f"'{segment.raw}': {possible_cases}")
            if possible_cases:
                # Save the latest possible case
                memory["latest_possible_case"] = possible_cases[0]
                logging.debug(f"[L010] Consistent capitalization, returning "
                              f"with memory: {memory}")
                return LintResult(memory=memory)
            else:
                concrete_policy = memory.get("latest_possible_case", "upper")
                logging.debug(f"[L010] Getting concrete policy "
                              f"'{concrete_policy}' from memory")
        else:
            if self.capitalisation_policy not in refuted_cases:
                logging.debug(f"[L010] Consistent capitalization "
                              f"{self.capitalisation_policy}, returning with "
                              f"memory: {memory}")
                return LintResult(memory=memory)
            else:
                concrete_policy = self.capitalisation_policy
                logging.debug(f"[L010] Setting concrete policy "
                              f"'{concrete_policy}' from "
                              f"self.capitalisation_policy")
        
        # If we got here, we need to change the case to the top possible case
        # Convert the raw to the concrete policy
        if concrete_policy == "lower":
            fixed_raw = segment.raw.lower()
        elif concrete_policy == "upper":
            fixed_raw = segment.raw.upper()
        elif concrete_policy == "capitalise":
            fixed_raw = segment.raw.capitalize()
        elif concrete_policy == "pascal":
            fixed_raw = re.sub(
                "([^a-zA-Z0-9]+|^)([a-zA-Z0-9])([a-zA-Z0-9]*)",
                lambda match: match.group(2).upper() + match.group(3).lower(),
                segment.raw
            )
        
        if fixed_raw == segment.raw:
            # No need to fix
            logging.debug(f"[L010] Capitalisation of segment '{segment.raw}' "
                          f"already consistent with policy '{concrete_policy}'"
                          f", returning with memory {memory}")
            return LintResult(memory=memory)
        else:
            # Return the fixed segment
            logging.debug(f"[L010] INCONSISTENT Capitalisation of segment "
                          f"'{segment.raw}', fixing to '{fixed_raw}' and "
                          f"returning with memory {memory}")
            return LintResult(
                anchor=segment,
                fixes=[
                    LintFix(
                        "edit",
                        segment,
                        segment.__class__(
                            raw=fixed_raw,
                            pos_marker=segment.pos_marker
                        )
                    )
                ],
                memory=memory,
            )
