"""Read an ANTLR SQL grammar's keywords, reserved and not.

Usage: python antlr_keywords.py LEXER.g4 PARSER.g4

A keyword is a lexer rule whose body is only quoted words, e.g.
``ADD: 'ADD';`` or ``KEYS: 'KEYS' | 'KEY';``. The parser's name rule accepts
``IDENTIFIER | quotedIdentifier | nonReserved``, so a keyword listed in the
``nonReserved`` rule can be a name (unreserved) and any other keyword can't
(reserved). Prints JSON: {"reserved": [...], "unreserved": [...]}.
"""

import json
import re
import sys

WORD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def lexer_keywords(lexer: str) -> dict[str, set[str]]:
    """Token name -> the words it matches, for tokens that are only words."""
    keywords: dict[str, set[str]] = {}
    for name, body in re.findall(
        r"^([A-Z][A-Z0-9_]*)\s*:\s*(.*?);", _strip_comments(lexer), re.S | re.M
    ):
        alternatives = [part.strip() for part in body.split("|")]
        words = set()
        for part in alternatives:
            literal = re.fullmatch(r"'([^']*)'", part)
            if not literal or not WORD.match(literal.group(1)):
                break
            words.add(literal.group(1).upper())
        else:
            keywords[name] = words
    return keywords


def non_reserved_tokens(parser: str) -> set[str]:
    """The token names listed in the parser's nonReserved rule."""
    text = _strip_comments(parser)
    match = re.search(r"^nonReserved\b[^:]*?:(.*?)^\s*;", text, re.S | re.M)
    if not match:
        sys.exit("no nonReserved rule found: the grammar isn't laid out as expected")
    return set(re.findall(r"\b([A-Z][A-Z0-9_]*)\b", match.group(1)))


def main() -> None:
    """Print the keywords of the grammar named on the command line."""
    lexer, parser = (open(path).read() for path in sys.argv[1:3])
    keywords = lexer_keywords(lexer)
    non_reserved = non_reserved_tokens(parser)
    # nonReserved can also list punctuation tokens (braces, comment markers)
    # for the parser's own reasons, and tokens the lexer doesn't define. They
    # aren't words, so they can't be keywords; report them and carry on.
    ignored = non_reserved - set(keywords)
    if ignored:
        print(f"ignored, not keyword tokens: {sorted(ignored)}", file=sys.stderr)
    reserved = set().union(*(w for t, w in keywords.items() if t not in non_reserved))
    unreserved = set().union(*(w for t, w in keywords.items() if t in non_reserved))
    print(
        json.dumps(
            {"reserved": sorted(reserved), "unreserved": sorted(unreserved - reserved)}
        )
    )


if __name__ == "__main__":
    main()
