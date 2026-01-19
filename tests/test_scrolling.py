from __future__ import annotations

from spotidry.spotify import _scroll_loop


def test_scroll_loop_no_scroll_when_shorter_or_equal():
    assert _scroll_loop('abc', width=3, offset=0) == 'abc'
    assert _scroll_loop('abc', width=4, offset=10) == 'abc'


def test_scroll_loop_scrolls_with_gap():
    # loop = "abcd   "
    assert _scroll_loop('abcd', width=3, offset=0, gap='   ') == 'abc'
    assert _scroll_loop('abcd', width=3, offset=1, gap='   ') == 'bcd'
    assert _scroll_loop('abcd', width=3, offset=3, gap='   ') == 'd  '
    assert _scroll_loop('abcd', width=3, offset=4, gap='   ') == '   '
    assert _scroll_loop('abcd', width=3, offset=6, gap='   ') == ' ab'
