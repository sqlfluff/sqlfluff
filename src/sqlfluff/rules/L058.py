"""Implementation of Rule L058."""
from typing import Optional

from sqlfluff.core.parser import KeywordSegment
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L058(BaseRule):
    """Postgres triggers should execute "FUNCTION" not "PROCEDURE".

    | **Anti-pattern**
    | In the syntax of CREATE TRIGGER, the keywords FUNCTION and PROCEDURE
    | are equivalent. The use of the keyword PROCEDURE here is
    | historical and deprecated.

    .. code-block:: sql
       :force:

        CREATE TRIGGER my_trigger
            AFTER INSERT ON my_table
            FOR EACH ROW
            EXECUTE PROCEDURE my_function();


    | **Best practice**
    | Use EXECUTE FUNCTION rather than EXECUTE PROCEDURE.

    .. code-block:: sql
       :force:

        CREATE TRIGGER my_trigger
            AFTER INSERT ON my_table
            FOR EACH ROW
            EXECUTE FUNCTION my_function();
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use FUNCTION not PROCEDURE when creating Postgres triggers.

        This is recommended in the current docs:
        https://www.postgresql.org/docs/14/sql-createtrigger.html
        And was changed in Postgres 11:
        https://www.postgresql.org/docs/release/11.0/
        """
        if context.dialect.name != "postgres":
            return None

        if context.segment.type != "create_trigger":
            return None

        for segment in context.segment.segments:
            if segment.name == "procedure":
                return LintResult(
                    segment,
                    fixes=[
                        LintFix(
                            "edit",
                            anchor=segment,
                            edit=KeywordSegment("FUNCTION"),
                        )
                    ],
                )

        return None
