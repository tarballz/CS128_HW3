"""
    vclock
    ~~~~~~

    Functions for manipulating vector clocks.

    :copyright: (C) 2016 by Eeo Jun
    :license: MIT, see LICENSE for details.

    API
    ===

    >>> import vclock
    >>> vclock.from_size(3)
    (0, 0, 0)
    >>> vclock.merge((1, 2), (3, 2))
    (3, 2)
    >>> [vclock.compare(a, b) for a, b in [
        [(1, 1), (1, 2)],
        [(1, 1), (1, 1)],
        [(1, 1), (1, 0)],
        [(1, 2), (2, 1)],
        ]]
    [-1, 0, 1, 0]
    >>> vclock.sort([(1, 2), (3, 2)], reverse=True)
    [(3, 2), (1, 2)]
    >>> vclock.is_concurrent((1, 2), (2, 1))
    True
    >>> vclock.increment((0, 1), 0)
    (1, 1)


"""

import sys
import itertools
from functools import cmp_to_key

if sys.version_info[0] == 2:
    zip = itertools.izip
    map = itertools.imap


def from_size(n):
    """
    Constructs a zeroed, *n* sized vector clock.
    """
    return (0,) * n


def merge(a, b):
    """
    Given two clocks, return a new clock with all
    values greater or equal to those of the merged
    clocks.
    """
    return tuple(map(max, zip(a, b)))


def compare(a, b):
    """
    Compares two vector clocks, returns -1 if ``a < b``,
    1 if ``a > b`` else 0 for concurrent events
    or identical values.
    """
    gt = False
    lt = False
    for j, k in zip(a, b):
        gt |= j > k
        lt |= j < k
        if gt and lt:
            break
    return int(gt) - int(lt)


def sort(xs, key=None, reverse=False):
    """
    Sort iterable *xs* using the ``vclock.compare``
    algorithm, optionally with a *key* function and
    whether to *reverse* the sorting (defaults to
    ascending order).
    """
    cmpfunc = (
            compare if key is None else
            lambda a, b: compare(key(a), key(b))
        )
    return sorted(xs, key=cmp_to_key(cmpfunc),
                      reverse=reverse)


def is_concurrent(a, b):
    """
    Returns whether the given clocks are concurrent.
    They must not be equal in value.
    """
    return (a != b) and compare(a, b) == 0


def increment(clock, index):
    """
    Increment the clock at *index*.
    """
    return clock[:index] \
            + (clock[index] + 1,) \
            + clock[index+1:]
