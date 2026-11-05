"""Test the identity helpers."""

import itertools
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import pytest

from sqlfluff.core.helpers import identity
from sqlfluff.core.helpers.identity import get_cache_key
from sqlfluff.core.parser import Ref


def test__helpers_identity__cache_keys_unique():
    """Test that cache keys made in one process are all different."""
    keys = [get_cache_key() for _ in range(1000)]
    assert len(set(keys)) == len(keys)


def test__helpers_identity__new_prefix_gives_new_keys(monkeypatch):
    """Test that keys made after drawing a new prefix never repeat earlier ones.

    This is what a forked child does, so we also rewind the counter to stand in
    for the child carrying on from the same counter value as its parent.
    """
    # Setting the prefix to itself lets monkeypatch restore it afterwards.
    monkeypatch.setattr(identity, "_cache_key_prefix", identity._cache_key_prefix)
    monkeypatch.setattr(identity, "_counter", itertools.count(1))
    before = [get_cache_key() for _ in range(3)]
    monkeypatch.setattr(identity, "_counter", itertools.count(1))
    identity._draw_cache_key_prefix()
    after = [get_cache_key() for _ in range(3)]
    assert set(before).isdisjoint(after)


def test__helpers_identity__spawned_process_keys_differ():
    """Test that spawned processes never make a key another process made.

    Fresh worker processes have made the same number of keys as each other, so
    without the random prefix their next keys would be equal.
    """
    spawn = multiprocessing.get_context("spawn")
    with (
        ProcessPoolExecutor(1, mp_context=spawn) as first,
        ProcessPoolExecutor(1, mp_context=spawn) as second,
    ):
        first_keys = [first.submit(get_cache_key).result() for _ in range(3)]
        second_keys = [second.submit(get_cache_key).result() for _ in range(3)]
        # Grammars pickle by value, so one made in the first worker keeps its key
        # when it is pickled to the second, which then makes a grammar of its own.
        grammar = first.submit(Ref.keyword, "SELECT").result()
        key_in_second = second.submit(Ref.cache_key, grammar).result()
        own_grammar = second.submit(Ref.keyword, "SELECT").result()
    parent_keys = [get_cache_key() for _ in range(3)]

    assert len({*first_keys, *second_keys, *parent_keys}) == 9
    assert key_in_second == grammar.cache_key()
    assert own_grammar.cache_key() != grammar.cache_key()


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(),
    reason="The fork start method is not available.",
)
@pytest.mark.filterwarnings(
    "ignore:This process .* is multi-threaded:DeprecationWarning"
)
def test__helpers_identity__forked_process_keys_differ():
    """Test that a forked child never makes a key its parent makes next.

    A forked child carries on from the parent's counter, so only its new prefix
    keeps its keys apart from the ones the parent goes on to make.
    """
    fork = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(1, mp_context=fork) as executor:
        child_keys = [executor.submit(get_cache_key).result() for _ in range(3)]
    parent_keys = [get_cache_key() for _ in range(3)]

    assert set(child_keys).isdisjoint(parent_keys)
