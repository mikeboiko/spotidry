from __future__ import annotations

from argparse import Namespace

from spotidry import __main__
from spotipy.exceptions import SpotifyOauthError


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

    def volume_up(self):
        self.calls.append('volume_up')
        return 60

    def volume_down(self):
        self.calls.append('volume_down')
        return 40

    def refresh(self, *, allow_cached_status, allow_stale_fallback):
        self.calls.append(('refresh', allow_cached_status, allow_stale_fallback))

    def print_info(self):
        self.calls.append('print_info')

    def print_volume(self, *, volume_percent=None):
        self.calls.append(('print_volume', volume_percent))

    def print_stopped(self):
        self.calls.append('print_stopped')


def test_main_track_missing_prints_stopped(monkeypatch):
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(
            save=False,
            setup=False,
            reauth=False,
            play=False,
            next=False,
            previous=False,
            volume_show=False,
            volume_up=False,
            volume_down=False,
        ),
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
        lambda: Namespace(
            save=True,
            setup=True,
            reauth=False,
            play=True,
            next=True,
            previous=True,
            volume_show=False,
            volume_up=False,
            volume_down=False,
        ),
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
        lambda: Namespace(
            save=False,
            setup=True,
            reauth=False,
            play=False,
            next=False,
            previous=False,
            volume_show=False,
            volume_up=False,
            volume_down=False,
        ),
    )
    monkeypatch.setattr(
        __main__.spotify.Spotidry, 'setup_only', classmethod(lambda cls: called.setdefault('setup', 1))
    )

    rc = __main__.main()
    assert rc == 0
    assert called['setup'] == 1


def test_main_volume_flags_print_volume(monkeypatch):
    fake = FakeSpotidry(track_present=False)
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(
            save=False,
            setup=False,
            reauth=False,
            play=False,
            next=False,
            previous=False,
            volume_show=False,
            volume_up=True,
            volume_down=False,
        ),
    )
    monkeypatch.setattr(__main__.spotify, 'Spotidry', lambda **_kwargs: fake)

    rc = __main__.main()
    assert rc == 0
    assert fake.calls == ['volume_up', ('print_volume', 60)]


def test_main_volume_show_calls_print_volume_without_arg(monkeypatch):
    fake = FakeSpotidry(track_present=False)
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(
            save=False,
            setup=False,
            reauth=False,
            play=False,
            next=False,
            previous=False,
            volume_show=True,
            volume_up=False,
            volume_down=False,
        ),
    )
    monkeypatch.setattr(__main__.spotify, 'Spotidry', lambda **_kwargs: fake)

    rc = __main__.main()
    assert rc == 0
    # volume_show alone should call print_volume with no explicit volume
    # so it uses AUTO_VOLUME to fetch the current volume from the API
    assert fake.calls == [('print_volume', None)]


def test_main_reauth_clears_auth_cache_and_skips_status_cache(monkeypatch):
    calls = []
    fake = FakeSpotidry(track_present=True)

    class FakeSpotidryFactory:
        @staticmethod
        def clear_auth_cache():
            calls.append('clear_auth_cache')

        def __new__(cls, **kwargs):
            calls.append(kwargs)
            return fake

    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(
            save=False,
            setup=False,
            reauth=True,
            play=False,
            next=False,
            previous=False,
            volume_show=False,
            volume_up=False,
            volume_down=False,
        ),
    )
    monkeypatch.setattr(__main__.spotify, 'Spotidry', FakeSpotidryFactory)

    rc = __main__.main()

    assert rc == 0
    assert calls == [
        'clear_auth_cache',
        {'allow_cached_status': False, 'allow_stale_fallback': False},
    ]
    assert fake.calls == ['print_info']


def test_main_invalid_grant_suggests_reauthentication(monkeypatch, capsys):
    monkeypatch.setattr(
        __main__.cli,
        'parse_args',
        lambda: Namespace(
            save=False,
            setup=False,
            reauth=False,
            play=False,
            next=False,
            previous=False,
            volume_show=False,
            volume_up=False,
            volume_down=False,
        ),
    )

    def fail_to_connect(**_kwargs):
        raise SpotifyOauthError(
            'invalid grant',
            error='invalid_grant',
            error_description='Refresh token revoked',
        )

    monkeypatch.setattr(__main__.spotify, 'Spotidry', fail_to_connect)

    rc = __main__.main()

    assert rc == 1
    assert capsys.readouterr().err == (
        'Spotify rejected the cached refresh token. Run `spotidry --reauth` to sign in again.\n'
    )
