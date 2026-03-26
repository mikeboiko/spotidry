from __future__ import annotations

from argparse import Namespace

from spotidry import __main__


class FakeSpotidry:
    def __init__(self, *, track_present=True, **_kwargs):
        self.track = {'dummy': True} if track_present else None
        self.calls = []

    def save(self):
        self.calls.append('save')

    def setup(self):
        self.calls.append('setup')

    def play(self):
        self.calls.append('play')

    def next(self):
        self.calls.append('next')

    def previous(self):
        self.calls.append('previous')

    def refresh(self, *, allow_cached_status, allow_stale_fallback):
        self.calls.append(('refresh', allow_cached_status, allow_stale_fallback))

    def print_info(self):
        self.calls.append('print_info')

    def print_stopped(self):
        self.calls.append('print_stopped')


def test_main_track_missing_prints_stopped(monkeypatch):
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(save=False, setup=False, play=False, next=False, previous=False),
    )
    monkeypatch.setattr(
        __main__.spotify, 'Spotidry', lambda **kwargs: FakeSpotidry(track_present=False, **kwargs)
    )

    rc = __main__.main()
    assert rc == 0


def test_main_invokes_requested_actions(monkeypatch):
    fake = FakeSpotidry(track_present=True)
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(save=True, setup=True, play=True, next=True, previous=True),
    )
    monkeypatch.setattr(__main__.spotify, 'Spotidry', lambda **_kwargs: fake)

    rc = __main__.main()
    assert rc == 0
    assert fake.calls == [
        'save',
        'setup',
        'play',
        'next',
        'previous',
        ('refresh', False, False),
        'print_info',
    ]


def test_main_setup_only_uses_setup_shortcut(monkeypatch):
    called = {}

    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(save=False, setup=True, play=False, next=False, previous=False),
    )
    monkeypatch.setattr(
        __main__.spotify.Spotidry, 'setup_only', classmethod(lambda cls: called.setdefault('setup', 1))
    )

    rc = __main__.main()
    assert rc == 0
    assert called['setup'] == 1
