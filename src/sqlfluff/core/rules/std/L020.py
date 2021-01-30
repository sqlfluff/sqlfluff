"""Implementation of Rule L020."""

import itertools

from ..base import BaseCrawler, LintResult


class Rule_L020(BaseCrawler):
    """Table aliases should be unique within each clause."""

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        for a1, a2 in itertools.combinations(aliases, 2):
            # Compare the strings
            if a1[0] == a2[0] and a1[0]:
                # If there are any, then the rest of the code
                # won't make sense so just return here.
                return [
                    LintResult(
                        # Reference the element, not the string.
                        anchor=a2[1],
                        description=(
                            "Duplicate table alias {0!r}. Table "
                            "aliases should be unique."
                        ).format(a2[0]),
                    )
                ]
        return None

    @staticmethod
    def _has_value_table_function(clause, dialect):
        function = clause.get_child('function')
        if not function:
            return False

        function_name = function.get_child('function_name')
        if not function_name:
            return False

        return function_name.raw in dialect.sets("value_table_functions")

    @classmethod
    def _get_aliases_from_select(cls, segment, dialect):
        # Get the aliases referred to in the clause
        fc = segment.get_child("from_clause")
        if not fc:
            # If there's no from clause then just abort.
            return None
        aliases = fc.get_table_expressions_and_eventual_aliases()

        # We only want table aliases, so filter out:
        # * None values
        # * Aliases for table value functions
        result = []
        for clause, alias in aliases:
            if alias and not cls._has_value_table_function(clause, dialect):
                result.append(alias)
        return result

    def _eval(self, segment, parent_stack, dialect, **kwargs):
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        if segment.is_type("select_statement"):
            aliases = self._get_aliases_from_select(segment, dialect)
            if not aliases:
                return None

            # Iterate through all the references, both in the select clause, but also
            # potential others.
            sc = segment.get_child("select_clause")
            reference_buffer = list(sc.recursive_crawl("object_reference"))
            # Add any wildcard references
            reference_buffer += list(sc.recursive_crawl("wildcard_identifier"))
            for potential_clause in (
                "where_clause",
                "groupby_clause",
                "having_clause",
                "orderby_clause",
            ):
                clause = segment.get_child(potential_clause)
                if clause:
                    reference_buffer += list(clause.recursive_crawl("object_reference"))
            # PURGE any references which are in nested select statements
            for ref in reference_buffer.copy():
                ref_path = segment.path_to(ref)
                # is it in a subselect? i.e. a select which isn't this one.
                if any(
                    seg.is_type("select_statement") and seg is not segment
                    for seg in ref_path
                ):
                    reference_buffer.remove(ref)

            # Get all column aliases
            col_aliases = []
            for col_seg in list(sc.recursive_crawl("alias_expression")):
                for seg in col_seg.segments:
                    if seg.is_type("identifier"):
                        col_aliases.append(seg.raw)

            # Get any columns referred to in a using clause, and extract anything
            # from ON clauses.
            using_cols = []
            fc = segment.get_child("from_clause")
            for join_clause in fc.recursive_crawl("join_clause"):
                in_using_brackets = False
                seen_using = False
                seen_on = False
                for seg in join_clause.segments:
                    if seg.is_type("keyword") and seg.name == "USING":
                        seen_using = True
                    elif seg.is_type("keyword") and seg.name == "ON":
                        seen_on = True
                    elif seen_using and seg.is_type("start_bracket"):
                        in_using_brackets = True
                    elif seen_using and seg.is_type("end_bracket"):
                        in_using_brackets = False
                        seen_using = False
                    elif in_using_brackets and seg.is_type("identifier"):
                        using_cols.append(seg.raw)
                    elif seen_on and seg.is_type("expression"):
                        # Deal with expressions
                        reference_buffer += list(
                            seg.recursive_crawl("object_reference")
                        )

            # Work out if we have a parent select function
            parent_select = None
            for seg in reversed(parent_stack):
                if seg.is_type("select_statement"):
                    parent_select = seg
                    break

            # Pass them all to the function that does all the work.
            # NB: Subclasses of this rules should override the function below
            return self._lint_references_and_aliases(
                aliases, reference_buffer, col_aliases, using_cols, parent_select
            )
        return None
