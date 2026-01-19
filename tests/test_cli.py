from __future__ import annotations

import sys

from spotidry import cli


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['spotidry'])
    args = cli.parse_args()
    assert args.save is False
    assert args.setup is False
    assert args.play is False
    assert args.next is False
    assert args.previous is False


def test_parse_args_flags(monkeypatch):
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'spotidry',
            '--save',
            '--play',
            '--next',
            '--previous',
            '--setup',
        ],
    )
    args = cli.parse_args()
    assert args.save is True
    assert args.setup is True
    assert args.play is True
    assert args.next is True
    assert args.previous is True
