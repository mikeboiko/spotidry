from __future__ import annotations

import json

from spotipy.exceptions import SpotifyException

from spotidry.spotify import Spotidry

from tests.conftest import FakeSpotify, SpotifyCallLog


def test_status_only_uses_fresh_cache_without_connect(tmp_path, monkeypatch, sample_track):
    cache_dir = tmp_path / 'cache'
    cache_dir.mkdir()
    cache_file = cache_dir / 'status_cache.json'
    cache_file.write_text(
        json.dumps(
            {
                'fetched_at': 100.0,
                'rate_limited_until': None,
                'track': sample_track,
                'track_id': 'track123',
                'play_status': True,
                'liked_status': True,
            }
        ),
        encoding='utf-8',
    )

    def fake_load_config(self):
        self.config = {
            'client_id': 'id',
            'client_secret': 'secret',
            'redirect_uri': 'http://127.0.0.1:9999',
            'status_cache_seconds': 5,
        }

    monkeypatch.setattr('spotidry.spotify.user_cache_dir', lambda _: str(cache_dir))
    monkeypatch.setattr('spotidry.spotify.time.time', lambda: 102.0)
    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(
        Spotidry, 'connect', lambda self: (_ for _ in ()).throw(AssertionError('should not connect'))
    )

    s = Spotidry(allow_cached_status=True, allow_stale_fallback=True)
    assert s.track == sample_track
    assert s.play_status is True
    assert s.track_id == 'track123'
    assert s.liked_status is True


def test_refresh_reuses_cached_like_status_for_same_track(tmp_path, monkeypatch, sample_track):
    cache_dir = tmp_path / 'cache'
    cache_dir.mkdir()
    cache_file = cache_dir / 'status_cache.json'
    cache_file.write_text(
        json.dumps(
            {
                'fetched_at': 100.0,
                'rate_limited_until': None,
                'track': sample_track,
                'track_id': 'track123',
                'play_status': True,
                'liked_status': True,
            }
        ),
        encoding='utf-8',
    )

    log = SpotifyCallLog()

    def fake_load_config(self):
        self.config = {
            'client_id': 'id',
            'client_secret': 'secret',
            'redirect_uri': 'http://127.0.0.1:9999',
            'status_cache_seconds': 1,
        }

    def fake_connect(self):
        self.sp = FakeSpotify(track=sample_track, liked=False, log=log)

    monkeypatch.setattr('spotidry.spotify.user_cache_dir', lambda _: str(cache_dir))
    monkeypatch.setattr('spotidry.spotify.time.time', lambda: 105.0)
    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry(allow_cached_status=True, allow_stale_fallback=True)
    assert s.track == sample_track
    assert s.liked_status is True
    assert log.current_user_playing_track == 1
    assert log.saved_tracks_contains == 0


def test_refresh_uses_stale_cache_when_rate_limited(tmp_path, monkeypatch, sample_track):
    cache_dir = tmp_path / 'cache'
    cache_dir.mkdir()
    cache_file = cache_dir / 'status_cache.json'
    cache_file.write_text(
        json.dumps(
            {
                'fetched_at': 100.0,
                'rate_limited_until': None,
                'track': sample_track,
                'track_id': 'track123',
                'play_status': True,
                'liked_status': False,
            }
        ),
        encoding='utf-8',
    )

    class RateLimitedSpotify:
        def current_user_playing_track(self):
            raise SpotifyException(
                429,
                -1,
                'rate limited',
                headers={'Retry-After': '30'},
            )

    def fake_load_config(self):
        self.config = {
            'client_id': 'id',
            'client_secret': 'secret',
            'redirect_uri': 'http://127.0.0.1:9999',
            'status_cache_seconds': 5,
        }

    def fake_connect(self):
        self.sp = RateLimitedSpotify()

    monkeypatch.setattr('spotidry.spotify.user_cache_dir', lambda _: str(cache_dir))
    monkeypatch.setattr('spotidry.spotify.time.time', lambda: 200.0)
    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry(allow_cached_status=True, allow_stale_fallback=True)

    assert s.track == sample_track
    assert s.liked_status is False

    cache_payload = json.loads(cache_file.read_text(encoding='utf-8'))
    assert cache_payload['rate_limited_until'] == 230.0
