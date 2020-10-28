"""GreedyUntil and StartsWith Grammars."""

from ..segments_base import trim_non_code
from ..match_result import MatchResult
from ..match_wrapper import match_wrapper

from .base import BaseGrammar


class GreedyUntil(BaseGrammar):
    """Matching for GreedyUntil works just how you'd expect.

    Args:
        enforce_whitespace_preceeding (:obj:`bool`): Should the GreedyUntil
            match only match the content if it's preceeded by whitespace?
            (defaults to False). This is useful for some keywords which may
            have false alarms on some array accessors.

    """

    def __init__(self, *args, **kwargs):
        self.enforce_whitespace_preceeding_terminator = kwargs.pop(
            "enforce_whitespace_preceeding_terminator", False
        )
        super(GreedyUntil, self).__init__(*args, **kwargs)

    @match_wrapper()
    def match(self, segments, parse_context):
        """Matching for GreedyUntil works just how you'd expect."""
        return self.greedy_match(
            segments,
            parse_context,
            matchers=self._elements,
            allow_gaps=self.allow_gaps,
            enforce_whitespace_preceeding_terminator=self.enforce_whitespace_preceeding_terminator,
            include_terminator=False,
        )

    @classmethod
    def greedy_match(
        cls,
        segments,
        parse_context,
        matchers,
        allow_gaps,
        enforce_whitespace_preceeding_terminator,
        include_terminator=False,
    ):
        """Matching for GreedyUntil works just how you'd expect."""
        seg_buff = segments
        seg_bank = ()  # Empty tuple
        # If no terminators then just return the whole thing.
        if matchers == [None]:
            return MatchResult.from_matched(segments)

        while True:
            with parse_context.deeper_match() as ctx:
                pre, mat, _ = cls._bracket_sensitive_look_ahead_match(
                    seg_buff, matchers, parse_context=ctx, allow_gaps=allow_gaps
                )

            # Do we have a match?
            if mat:
                # Do we need to enfore whitespace preceeding?
                if enforce_whitespace_preceeding_terminator:
                    # Does the match include some whitespace already?
                    # Work forward
                    idx = 0
                    while True:
                        elem = mat.matched_segments[idx]
                        if elem.is_meta:
                            idx += 1
                            continue
                        elif elem.is_type("whitespace", "newline"):
                            allow = True
                            break
                        else:
                            # No whitespace before. Not allowed.
                            allow = False
                            break

                    # If we're not ok yet, work backward to the preceeding sections.
                    if not allow:
                        idx = -1
                        while True:
                            if len(pre) < abs(idx):
                                # If we're at the start, it's ok
                                allow = True
                                break
                            if pre[idx].is_meta:
                                idx -= 1
                                continue
                            elif pre[idx].is_type("whitespace", "newline"):
                                allow = True
                                break
                            else:
                                # No whitespace before. Not allowed.
                                allow = False
                                break

                    if not allow:
                        # Update our buffers and continue onward
                        seg_bank = pre + mat.matched_segments
                        seg_buff = mat.unmatched_segments
                        # Loop around, don't return yet
                        continue

                # Depending on whether we found a terminator or not we treat
                # the result slightly differently. If no terminator was found,
                # we just use the whole unmatched segment. If we did find one,
                # we match up until (but not including [unless self.include_terminator
                # is true]) that terminator.
                if mat:
                    # Return everything up to the match.
                    if include_terminator:
                        return MatchResult(
                            seg_bank + pre + mat.matched_segments,
                            mat.unmatched_segments,
                        )

                    # We can't claim any non-code segments, so we trim them off the end.
                    leading_nc, pre_seg_mid, trailing_nc = trim_non_code(seg_bank + pre)
                    return MatchResult(
                        leading_nc + pre_seg_mid,
                        trailing_nc + mat.all_segments(),
                    )
                # No terminator, just return the whole thing.
                return MatchResult.from_matched(mat.unmatched_segments)
            else:
                # Return everything
                return MatchResult.from_matched(segments)


class StartsWith(GreedyUntil):
    """Match if this sequence starts with a match.

    This also has configurable whitespace and comment handling.
    """

    def __init__(self, target, *args, **kwargs):
        self.target = self._resolve_ref(target)
        self.terminator = self._resolve_ref(kwargs.pop("terminator", None))
        self.include_terminator = kwargs.pop("include_terminator", False)
        super(StartsWith, self).__init__(*args, **kwargs)

    def simple(self, parse_context):
        """Does this matcher support a uppercase hash matching route?

        `StartsWith` is simple, if the thing it starts with is also simple.
        """
        return self.target.simple(parse_context=parse_context)

    @match_wrapper()
    def match(self, segments, parse_context):
        """Match if this sequence starts with a match."""
        if self.allow_gaps:
            first_code_idx = None
            # Work through to find the first code segment...
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    first_code_idx = idx
                    break
            else:
                # We've trying to match on a sequence of segments which contain no code.
                # That means this isn't a match.
                return MatchResult.from_unmatched(segments)
            with parse_context.deeper_match() as ctx:
                match = self.target.match(
                    segments=segments[first_code_idx:], parse_context=ctx
                )
            if match:
                # The match will probably have returned a mutated version rather
                # that the raw segment sent for matching. We need to reinsert it
                # back into the sequence in place of the raw one, but we can't
                # just assign at the index because it's a tuple and not a list.
                # to get around that we do this slightly more elaborate construction.

                # NB: This match may be partial or full, either is cool. In the case
                # of a partial match, given that we're only interested in what it STARTS
                # with, then we can still used the unmatched parts on the end.
                # We still need to deal with any non-code segments at the start.
                greedy_match = self.greedy_match(
                    match.unmatched_segments,
                    parse_context,
                    matchers=[self.terminator],
                    allow_gaps=self.allow_gaps,
                    enforce_whitespace_preceeding_terminator=self.enforce_whitespace_preceeding_terminator,
                    include_terminator=self.include_terminator,
                )
                # Combine the results.
                return MatchResult(
                    match.matched_segments + greedy_match.matched_segments,
                    greedy_match.unmatched_segments,
                )
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError(
                "Not expecting to match StartsWith and also not just code!?"
            )
