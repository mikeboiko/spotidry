from __future__ import annotations

import sys

from spotidry import cli
import pytest


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['spotidry'])
    args = cli.parse_args()
    assert args.save is False
    assert args.setup is False
    assert args.play is False
    assert args.next is False
    assert args.previous is False
    assert args.volume_show is False
    assert args.volume_up is False
    assert args.volume_down is False


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
            '--volume-show',
            '--volume-up',
            '--volume-down',
        ],
    )
    args = cli.parse_args()
    assert args.save is True
    assert args.setup is True
    assert args.play is True
    assert args.next is True
    assert args.previous is True
    assert args.volume_show is True
    assert args.volume_up is True
    assert args.volume_down is True


def test_parse_args_help_text(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['spotidry', '--help'])

    with pytest.raises(SystemExit) as exc:
        cli.parse_args()

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert '-S, --setup' in out
    assert 'play previous track/skip to beginning of current track' in out
    assert '--volume-show' in out
    assert '--volume-up' in out
    assert '--volume-down' in out
