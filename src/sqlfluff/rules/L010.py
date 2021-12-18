"""Implementation of Rule L010."""

import regex
from typing import Tuple, List
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.config_info import get_config_info
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L010(BaseRule):
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
    # Human readable target elem for description
    _description_elem = "Keywords"

    def _eval(self, context: RuleContext) -> LintResult:
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of cases known to be
        INconsistent with what we've seen so far as well as the top choice
        for what the possible case is.

        """
        # Skip if not an element of the specified type/name
        if not self.matches_target_tuples(context.segment, self._target_elems):
            return LintResult(memory=context.memory)

        # Get the capitalisation policy configuration.
        try:
            cap_policy = self.cap_policy
            cap_policy_opts = self.cap_policy_opts
        except AttributeError:
            # First-time only, read the settings from configuration. This is
            # very slow.
            cap_policy, cap_policy_opts = self._init_capitalisation_policy()

        memory = context.memory
        refuted_cases = memory.get("refuted_cases", set())

        # Which cases are definitely inconsistent with the segment?
        if context.segment.raw[0] != context.segment.raw[0].upper():
            refuted_cases.update(["upper", "capitalise", "pascal"])
            if context.segment.raw != context.segment.raw.lower():
                refuted_cases.update(["lower"])
        else:
            refuted_cases.update(["lower"])
            if context.segment.raw != context.segment.raw.upper():
                refuted_cases.update(["upper"])
            if context.segment.raw != context.segment.raw.capitalize():
                refuted_cases.update(["capitalise"])
            if not context.segment.raw.isalnum():
                refuted_cases.update(["pascal"])

        # Update the memory
        memory["refuted_cases"] = refuted_cases

        self.logger.debug(
            f"Refuted cases after segment '{context.segment.raw}': {refuted_cases}"
        )

        # Skip if no inconsistencies, otherwise compute a concrete policy
        # to convert to.
        if cap_policy == "consistent":
            possible_cases = [c for c in cap_policy_opts if c not in refuted_cases]
            self.logger.debug(
                f"Possible cases after segment '{context.segment.raw}': {possible_cases}"
            )
            if possible_cases:
                # Save the latest possible case and skip
                memory["latest_possible_case"] = possible_cases[0]
                self.logger.debug(
                    f"Consistent capitalization, returning with memory: {memory}"
                )
                return LintResult(memory=memory)
            else:
                concrete_policy = memory.get("latest_possible_case", "upper")
                self.logger.debug(
                    f"Getting concrete policy '{concrete_policy}' from memory"
                )
        else:
            if cap_policy not in refuted_cases:
                # Skip
                self.logger.debug(
                    f"Consistent capitalization {cap_policy}, returning with "
                    f"memory: {memory}"
                )
                return LintResult(memory=memory)
            else:
                concrete_policy = cap_policy
                self.logger.debug(
                    f"Setting concrete policy '{concrete_policy}' from cap_policy"
                )

        # Set the fixed to same as initial in case any of below don't match
        fixed_raw = context.segment.raw
        # We need to change the segment to match the concrete policy
        if concrete_policy in ["upper", "lower", "capitalise"]:
            if concrete_policy == "upper":
                fixed_raw = fixed_raw.upper()
            elif concrete_policy == "lower":
                fixed_raw = fixed_raw.lower()
            elif concrete_policy == "capitalise":
                fixed_raw = fixed_raw.capitalize()
        elif concrete_policy == "pascal":
            # For Pascal we set the first letter in each "word" to uppercase
            # We do not lowercase other letters to allow for PascalCase style
            # words. This does mean we allow all UPPERCASE and also don't
            # correct Pascalcase to PascalCase, but there's only so much we can
            # do. We do correct underscore_words to Underscore_Words.
            fixed_raw = regex.sub(
                "([^a-zA-Z0-9]+|^)([a-zA-Z0-9])([a-zA-Z0-9]*)",
                lambda match: match.group(1) + match.group(2).upper() + match.group(3),
                context.segment.raw,
            )

        if fixed_raw == context.segment.raw:
            # No need to fix
            self.logger.debug(
                f"Capitalisation of segment '{context.segment.raw}' already OK with policy "
                f"'{concrete_policy}', returning with memory {memory}"
            )
            return LintResult(memory=memory)
        else:
            # build description based on the policy in use
            consistency = "consistently " if cap_policy == "consistent" else ""

            if concrete_policy in ["upper", "lower"]:
                policy = f"{concrete_policy} case."
            elif concrete_policy == "capitalise":
                policy = "capitalised."
            elif concrete_policy == "pascal":
                policy = "pascal case."

            # Return the fixed segment
            self.logger.debug(
                f"INCONSISTENT Capitalisation of segment '{context.segment.raw}', fixing to "
                f"'{fixed_raw}' and returning with memory {memory}"
            )

            return LintResult(
                anchor=context.segment,
                fixes=[self._get_fix(context.segment, fixed_raw)],
                memory=memory,
                description=f"{self._description_elem} must be {consistency}{policy}",
            )

    def _get_fix(self, segment, fixed_raw):
        """Given a segment found to have a fix, returns a LintFix for it.

        May be overridden by subclasses, which is useful when the parse tree
        structure varies from this simple base case.
        """
        return LintFix.replace(segment, [segment.edit(fixed_raw)])

    def _init_capitalisation_policy(self):
        """Called first time rule is evaluated to fetch & cache the policy."""
        cap_policy_name = next(
            k for k in self.config_keywords if k.endswith("capitalisation_policy")
        )
        self.cap_policy = getattr(self, cap_policy_name)
        self.cap_policy_opts = [
            opt
            for opt in get_config_info()[cap_policy_name]["validation"]
            if opt != "consistent"
        ]
        self.logger.debug(
            f"Selected '{cap_policy_name}': '{self.cap_policy}' from options "
            f"{self.cap_policy_opts}"
        )
        cap_policy = self.cap_policy
        cap_policy_opts = self.cap_policy_opts
        return cap_policy, cap_policy_opts
