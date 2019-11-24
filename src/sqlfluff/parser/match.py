"""Source for the MatchResult class.

This should be the default response from any `match` method.
"""

from collections import namedtuple


def _is_segment(other):
    """Return true if this is a Segment.

    The purpose of this helper function is for testing if something
    is a segment without requiring the import of the class.
    """
    return getattr(other, 'is_segment', False)


def curtail_string(s, length=20):
    """Trim a string nicely to length."""
    if len(s) > length:
        return s[:length] + '...'
    else:
        return s


def join_segments_raw(segments):
    """Make a string from the joined `raw` attributes of an iterable of segments."""
    return ''.join([s.raw for s in segments])


def join_segments_raw_curtailed(segments, length=20):
    """Make a string up to a certain length from an iterable of segments."""
    return curtail_string(
        join_segments_raw(segments),
        length=length
    )


class MatchResult(namedtuple('MatchResult', ['matched_segments', 'unmatched_segments'])):
    """This should be the default response from any `match` method.

    Args:
        matched_segments (:obj:`tuple`): A tuple of the segments which have been
            matched in this matching operation.
        unmatched_segments (:obj:`tuple`): A tuple of the segments, which come after
            the `matched_segments` which could not be matched.

    """

    def initial_match_pos_marker(self):
        """Return the position marker of the first matched segment in this result."""
        if self.has_match():
            return self.matched_segments[0].pos_marker
        else:
            return None

    def all_segments(self):
        """Return a tuple of all the segments, matched or otherwise."""
        return self.matched_segments + self.unmatched_segments

    def __len__(self):
        return len(self.matched_segments)

    def is_complete(self):
        """Return true if everything has matched.

        Note: An empty match is not a match so will return False.
        """
        return len(self.unmatched_segments) == 0 and len(self.matched_segments) > 0

    def has_match(self):
        """Return true if *anything* has matched."""
        return len(self) > 0

    def __bool__(self):
        return self.has_match()

    def raw_matched(self):
        """Make a string from the raw matched segments."""
        return join_segments_raw(self.matched_segments)

    def __str__(self):
        return "<MatchResult {0}/{1}: {2!r}>".format(
            len(self.matched_segments), len(self.matched_segments) + len(self.unmatched_segments),
            self.raw_matched())

    def __eq__(self, other):
        """Equals function override.

        This allows comparison to tuples for testing.
        """
        if isinstance(other, MatchResult):
            return (self.matched_segments == other.matched_segments
                    and self.unmatched_segments == other.unmatched_segments)
        elif isinstance(other, tuple):
            return self.matched_segments == other
        elif isinstance(other, list):
            return self.matched_segments == tuple(other)
        else:
            raise TypeError(
                "Unexpected equality comparison: type: {0}".format(
                    type(other)))

    @staticmethod
    def seg_to_tuple(segs):
        """Munge types to a tuple."""
        if _is_segment(segs):
            return (segs,)
        elif isinstance(segs, tuple):
            return segs
        elif isinstance(segs, list):
            return tuple(segs)
        else:
            raise TypeError("Unexpected input to `seg_to_tuple`: {0}".format(segs))

    @classmethod
    def from_unmatched(cls, unmatched):
        """Construct a `MatchResult` from just unmatched segments."""
        return cls(
            matched_segments=(),
            unmatched_segments=cls.seg_to_tuple(unmatched)
        )

    @classmethod
    def from_matched(cls, matched):
        """Construct a `MatchResult` from just matched segments."""
        return cls(
            unmatched_segments=(),
            matched_segments=cls.seg_to_tuple(matched)
        )

    @classmethod
    def from_empty(cls):
        """Construct an empty `MatchResult`."""
        return cls(unmatched_segments=(),
                   matched_segments=())

    @classmethod
    def unify(cls, other):
        """A helper method for type munging into a `MatchResult`."""
        # TODO: Do we need this?
        if isinstance(other, cls):
            # It's already a MatchResult
            return other
        elif other is None:
            # It's none, equivalent to an empty match
            return cls.from_empty()
        else:
            # It's something else, so lets assume a match.
            # If we've been passed garbage, then seg_to_tuple will
            # pick it up. If it fails it will raise a TypeError.
            return cls.from_matched(other)

    def __add__(self, other):
        """Override add for concatenating things onto this match."""
        if _is_segment(other):
            return self.__class__(
                matched_segments=self.matched_segments + (other,),
                unmatched_segments=self.unmatched_segments
            )
        elif isinstance(other, MatchResult):
            return self.__class__(
                matched_segments=self.matched_segments + other.matched_segments,
                unmatched_segments=self.unmatched_segments
            )
        elif isinstance(other, tuple):
            if len(other) > 0 and not _is_segment(other[0]):
                raise TypeError(
                    "Unexpected type passed to MatchResult.__add__: tuple of {0}.\n{1}".format(
                        type(other[0]), other))
            return self.__class__(
                matched_segments=self.matched_segments + other,
                unmatched_segments=self.unmatched_segments
            )
        elif isinstance(other, list):
            if len(other) > 0 and not _is_segment(other[0]):
                raise TypeError(
                    "Unexpected type passed to MatchResult.__add__: list of {0}".format(
                        type(other[0])))
            return self.__class__(
                matched_segments=self.matched_segments + tuple(other),
                unmatched_segments=self.unmatched_segments
            )
        else:
            raise TypeError(
                "Unexpected type passed to MatchResult.__add__: {0}".format(
                    type(other)))
