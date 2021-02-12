"""Implementation of Rule L020."""

import itertools

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L020(BaseCrawler):
    """Table aliases should be unique within each clause."""

    def _lint_references_and_aliases(
        self,
        table_aliases,
        value_table_function_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        for a1, a2 in itertools.combinations(table_aliases, 2):
            # Compare the strings
            if a1.ref_str == a2.ref_str and a1.ref_str:
                # If there are any, then the rest of the code
                # won't make sense so just return here.
                return [
                    LintResult(
                        # Reference the element, not the string.
                        anchor=a2.segment,
                        description=(
                            "Duplicate table alias {0!r}. Table "
                            "aliases should be unique."
                        ).format(a2.ref_str),
                    )
                ]
        return None

    @staticmethod
    def _has_value_table_function(table_expr, dialect):
        if not dialect:
            # We need the dialect to get the value table function names. If
            # we don't have it, assume the clause does not have a value table
            # function.
            return False

        for function_name in table_expr.recursive_crawl("function_name"):
            if function_name.raw.lower() in dialect.sets("value_table_functions"):
                return True
        return False

    @classmethod
    def _get_aliases_from_select(cls, segment, dialect=None):
        """Gets the aliases referred to in the FROM clause.

        Returns a tuple of two lists:
        - Table aliases
        - Value table function aliases
        """
        fc = segment.get_child("from_clause")
        if not fc:
            # If there's no from clause then just abort.
            return None, None
        aliases = fc.get_eventual_aliases()

        # We only want table aliases, so filter out aliases for value table
        # functions.
        table_aliases = []
        value_table_function_aliases = []
        for table_expr, alias_info in aliases:
            if not cls._has_value_table_function(table_expr, dialect):
                table_aliases.append(alias_info)
            else:
                value_table_function_aliases.append(alias_info)
        return table_aliases, value_table_function_aliases

    def _eval(self, segment, parent_stack, **kwargs):
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        if segment.is_type("select_statement"):
            table_aliases, value_table_function_aliases = self._get_aliases_from_select(
                segment, kwargs.get("dialect")
            )
            if not table_aliases and not value_table_function_aliases:
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
                for seg in join_clause.segments:
                    if seg.is_type("keyword") and seg.name == "USING":
                        seen_using = True
                    elif seg.is_type("join_on_condition"):
                        for on_seg in seg.segments:
                            if on_seg.is_type("expression"):
                                # Deal with expressions
                                reference_buffer += list(
                                    seg.recursive_crawl("object_reference")
                                )
                    elif seen_using and seg.is_type("start_bracket"):
                        in_using_brackets = True
                    elif seen_using and seg.is_type("end_bracket"):
                        in_using_brackets = False
                        seen_using = False
                    elif in_using_brackets and seg.is_type("identifier"):
                        using_cols.append(seg.raw)

            # Work out if we have a parent select function
            parent_select = None
            for seg in reversed(parent_stack):
                if seg.is_type("select_statement"):
                    parent_select = seg
                    break

            # Pass them all to the function that does all the work.
            # NB: Subclasses of this rules should override the function below
            return self._lint_references_and_aliases(
                table_aliases,
                value_table_function_aliases,
                reference_buffer,
                col_aliases,
                using_cols,
                parent_select,
            )
        return None
