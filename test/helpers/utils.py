from sqlfluff.core.parser.markers import FilePositionMarker
from sqlfluff.core.parser.segments.raw import RawSegment

def generate_test_segments(elems):
    """Roughly generate test segments.

    This function isn't totally robust, but good enough
    for testing. Use with caution.
    """
    buff = []
    raw_buff = ""
    for elem in elems:
        if set(elem) <= {" ", "\t"}:
            cls = RawSegment.make(" ", name="whitespace", type="whitespace")
        elif set(elem) <= {"\n"}:
            cls = RawSegment.make("\n", name="newline", type="newline")
        elif elem == "(":
            cls = RawSegment.make("(", name="bracket_open", _is_code=True)
        elif elem == ")":
            cls = RawSegment.make(")", name="bracket_close", _is_code=True)
        elif elem.startswith("--"):
            cls = RawSegment.make("--", name="inline_comment")
        elif elem.startswith('"'):
            cls = RawSegment.make('"', name="double_quote", _is_code=True)
        elif elem.startswith("'"):
            cls = RawSegment.make("'", name="single_quote", _is_code=True)
        else:
            cls = RawSegment.make("", _is_code=True)

        buff.append(cls(elem, FilePositionMarker().advance_by(raw_buff)))
        raw_buff += elem
    return tuple(buff)  # Make sure we return a tuple
