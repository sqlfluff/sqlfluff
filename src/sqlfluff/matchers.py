""" Classes for string and chunk matching """

import re


class CharMatchPattern(object):
    """ Intended for things like quote characters """
    def __init__(self, c, name):
        self._char = c
        self.name = name

    def _repr_pattern(self):
        return self._char * 2

    def __repr__(self):
        return "<{classname}: '{pattern}'>".format(classname=self.__class__.__name__, pattern=self._repr_pattern())

    def first_match_pos(self, s):
        # Assume s is a string
        for idx, c in enumerate(s):
            if c == self._char:
                return idx
        else:
            return None

    def span(self, s):
        # SPAN should return the index from and to of the match
        # a single character match will have a difference of span
        # equal to 1.
        first = self.first_match_pos(s)
        # check that we're not matching in the last position
        # (otherwise we can't add one to it)
        if first is not None and first < len(s):
            # Look or the next match after this
            second = self.first_match_pos(s[first + 1:])
            if second:
                # we add one here because we add it above
                return first, second + 2 + first
        # unless both first AND second match, then return here
        return first, None

    def chunkmatch(self, c):
        """ Given a full chunk, rather than just a string, return the first matching subchunk """
        span = self.span(c.chunk)
        if span[0] is not None:
            # there's a start!
            if span[1] is not None:
                # there's a defined end!
                return c.subchunk(start=span[0], end=span[1], context='match')
            else:
                # start but no end
                return c.subchunk(start=span[0], context='match')
        else:
            return None


class SingleCharMatchPattern(CharMatchPattern):
    """
    Intended for things like commas and newlines which come along
    This is a simplification of the standard CharMatchPattern
    """

    def _repr_pattern(self):
        return self._char

    def span(self, s):
        # SPAN should return the index from and to of the match
        # a single character match will have a difference of span
        # equal to 1.
        first = self.first_match_pos(s)
        # NB: Zero is still an acceptable answer here.
        if first is not None:
            return first, first + 1
        else:
            return None, None


class RegexMatchPattern(CharMatchPattern):
    def __init__(self, r, name):
        self._pattern = re.compile(r)
        self.name = name

    def _repr_pattern(self):
        return self._pattern.pattern

    def span(self, s):
        # Assume s is a string
        m = self._pattern.search(s)
        if m:
            return m.span()
        else:
            return None, None

    def first_match_pos(self, s):
        span = self.span(s)
        return span[0]


class MatcherBag(object):
    def __init__(self, *matchers):
        expanded_matchers = []
        for elem in matchers:
            if isinstance(elem, MatcherBag):
                expanded_matchers += elem._matchers
            elif isinstance(elem, CharMatchPattern):
                # matches any match pattern or derivative
                expanded_matchers.append(elem)
            else:
                raise TypeError("Unexpected Class in Bag: {0}".format(elem))
        # Check that names are unique
        assert len(expanded_matchers) == len(set([elem.name for elem in expanded_matchers]))
        # store them as a list
        self._matchers = expanded_matchers

    def __add__(self, other):
        # combining bags is just like making a bag with the combination of the matchers.
        # there will be a uniqueness check in this operation
        return MatcherBag(*(self._matchers + other._matchers))

    def __len__(self):
        return len(self._matchers)

    def chunkmatch(self, c):
        """
        Given a full chunk, compare against matchers in the bag and then order by first match

        Return a list of tuples (subchunk, pos, matcher)
        """
        match_buffer = []
        for matcher in self._matchers:
            chk = matcher.chunkmatch(c)
            if chk:
                match_buffer.append((chk, chk.start_pos - c.start_pos, matcher))
        return sorted(match_buffer, key=lambda x: x[1])
