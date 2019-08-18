""" Source for the MatchResult class. The default response from
any `match` method """

from collections import namedtuple


def _is_segment(other):
    """ Helper function for testing if something is a
    segment without requiring the import of the class """
    return getattr(other, 'is_segment', False)


class MatchResult(namedtuple('MatchResult', ['matched_segments', 'unmatched_segments'])):
    def initial_match_pos_marker(self):
        if self.has_match():
            return self.matched_segments[0].pos_marker
        else:
            return None

    def __len__(self):
        return len(self.matched_segments)

    def is_complete(self):
        return len(self) == 0

    def has_match(self):
        return len(self) > 0

    def __bool__(self):
        return self.has_match()

    def raw_matched(self):
        return ''.join([seg.raw for seg in self.matched_segments])

    def __str__(self):
        return "<MatchResult {0}/{1}: {2!r}>".format(
            len(self.matched_segments), len(self.matched_segments) + len(self.unmatched_segments),
            self.raw_matched())

    def __eq__(self, other):
        """ Equals function override, means comparison to tuples
        for testing isn't silly """
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
        # NB seg_to_tuple does the type munging
        return cls(
            matched_segments=(),
            unmatched_segments=cls.seg_to_tuple(unmatched)
        )

    @classmethod
    def from_matched(cls, matched):
        # NB seg_to_tuple does the type munging
        return cls(
            unmatched_segments=(),
            matched_segments=cls.seg_to_tuple(matched)
        )

    @classmethod
    def from_empty(cls):
        return cls(unmatched_segments=(),
                   matched_segments=())

    @classmethod
    def unify(cls, other):
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
        """ override + """
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
