"""Spotify API module."""

from __future__ import annotations

from pathlib import Path
import json
import os
import time
import webbrowser as wb

import spotipy
import yaml
from appdirs import user_cache_dir, user_config_dir
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

DEFAULT_STATUS_CACHE_SECONDS = 5.0
STATUS_CACHE_FILENAME = 'status_cache.json'


def _scroll_loop(text: str, *, width: int, offset: int, gap: str = '   ') -> str:
    """Return a fixed-width scrolling window over text in a continuous loop."""
    if width <= 0 or len(text) <= width:
        return text

    loop = f'{text}{gap}'
    start = offset % len(loop)
    doubled = loop + loop
    return doubled[start : start + width]


def _coerce_float(value: object, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class Spotidry:
    """Spotify status/commands."""

    def __init__(
        self,
        *,
        allow_cached_status: bool = False,
        allow_stale_fallback: bool = False,
    ):
        """Initialize state and optionally reuse cached playback status."""

        self.sp: spotipy.Spotify | None = None
        self.track: dict[str, object] | None = None
        self.play_status = False
        self.track_id: str | None = None
        self.liked_status = False
        self.load_config()
        self.refresh(
            allow_cached_status=allow_cached_status,
            allow_stale_fallback=allow_stale_fallback,
        )

    @classmethod
    def setup_only(cls):
        cls.__new__(cls).setup()

    def connect(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                cache_path=user_cache_dir('spotidry.json'),
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                redirect_uri=self.config.get('redirect_uri'),
                scope='user-read-currently-playing user-library-read user-library-modify user-modify-playback-state',
            ),
            retries=0,
            status_retries=0,
            backoff_factor=0,
        )

    def load_config(self):
        """Load user config from ~/.config/spotidry/spotidry.yaml
        Show error message if config file doesn't exist
        """
        config_file = Path(user_config_dir('spotidry')).joinpath('spotidry.yaml')

        if not os.path.exists(config_file):
            self.setup()

        with open(config_file, 'r', encoding='utf-8') as stream:
            try:
                self.config = yaml.safe_load(stream) or {}
            except FileNotFoundError as exc:
                print(exc)
            except yaml.YAMLError as exc:
                print(exc)

    def ensure_connected(self):
        if self.sp is None:
            self.connect()

    def _status_cache_path(self) -> Path:
        return Path(user_cache_dir('spotidry')).joinpath(STATUS_CACHE_FILENAME)

    def _status_cache_seconds(self) -> float:
        cache_seconds = _coerce_float(
            self.config.get('status_cache_seconds', DEFAULT_STATUS_CACHE_SECONDS),
            default=DEFAULT_STATUS_CACHE_SECONDS,
        )
        return max(cache_seconds, 0.0)

    def _load_status_cache(self) -> dict[str, object] | None:
        cache_path = self._status_cache_path()
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as file:
                payload: object = json.load(file)
        except json.JSONDecodeError as exc:
            print(f'Invalid status cache at {cache_path}: {exc}')
            return None
        except OSError as exc:
            print(exc)
            return None

        return payload if isinstance(payload, dict) else None

    def _write_status_cache_payload(self, payload: dict[str, object]):
        cache_path = self._status_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(cache_path, 'w', encoding='utf-8') as file:
                json.dump(payload, file)
        except OSError as exc:
            print(exc)

    def _write_status_cache(
        self,
        *,
        fetched_at: float | None = None,
        rate_limited_until: float | None = None,
    ):
        self._write_status_cache_payload(
            {
                'fetched_at': time.time() if fetched_at is None else fetched_at,
                'rate_limited_until': rate_limited_until,
                'track': self.track,
                'track_id': self.track_id,
                'play_status': self.play_status,
                'liked_status': self.liked_status,
            }
        )

    def _invalidate_status_cache(self):
        cache_path = self._status_cache_path()
        try:
            cache_path.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            print(exc)

    def _cache_is_fresh(self, cache_payload: dict[str, object] | None) -> bool:
        if cache_payload is None:
            return False

        cache_seconds = self._status_cache_seconds()
        if cache_seconds <= 0:
            return False

        fetched_at = _coerce_float(cache_payload.get('fetched_at'), default=0.0)
        return (time.time() - fetched_at) <= cache_seconds

    def _cache_is_rate_limited(self, cache_payload: dict[str, object] | None) -> bool:
        if cache_payload is None:
            return False

        rate_limited_until = _coerce_float(cache_payload.get('rate_limited_until'), default=0.0)
        return rate_limited_until > time.time()

    def _apply_state(
        self,
        track: dict[str, object] | None,
        *,
        liked_status: bool,
        play_status: bool | None = None,
    ):
        item = track.get('item') if isinstance(track, dict) else None
        if not isinstance(track, dict) or not isinstance(item, dict):
            self.track = None
            self.play_status = False
            self.track_id = None
            self.liked_status = False
            return

        self.track = track
        self.play_status = bool(track.get('is_playing') if play_status is None else play_status)
        track_id = item.get('id')
        self.track_id = track_id if isinstance(track_id, str) else None
        self.liked_status = liked_status

    def _apply_cached_state(self, cache_payload: dict[str, object]):
        self._apply_state(
            cache_payload.get('track'),
            liked_status=bool(cache_payload.get('liked_status', False)),
            play_status=bool(cache_payload.get('play_status', False)),
        )

    def _liked_status_for_track(
        self,
        track: dict[str, object] | None,
        *,
        cache_payload: dict[str, object] | None,
        reuse_cached_status: bool,
    ) -> bool:
        item = track.get('item') if isinstance(track, dict) else None
        if not isinstance(item, dict):
            return False

        track_id = item.get('id')
        if not isinstance(track_id, str):
            return False

        if reuse_cached_status and cache_payload and cache_payload.get('track_id') == track_id:
            return bool(cache_payload.get('liked_status', False))

        assert self.sp is not None
        return self.sp.current_user_saved_tracks_contains(tracks=[track_id])[0]

    def _artist_and_song(self) -> tuple[str, str]:
        item = self.track.get('item') if isinstance(self.track, dict) else None
        if not isinstance(item, dict):
            return '', ''

        song_name = item.get('name')
        song = song_name if isinstance(song_name, str) else ''

        artists = item.get('artists')
        if not isinstance(artists, list) or not artists:
            return '', song

        first_artist = artists[0]
        if not isinstance(first_artist, dict):
            return '', song

        artist_name = first_artist.get('name')
        artist = artist_name if isinstance(artist_name, str) else ''
        return artist, song

    def _retry_after_seconds(self, exc: SpotifyException) -> float:
        headers = exc.headers or {}
        retry_after = headers.get('Retry-After') if isinstance(headers, dict) else None
        return max(
            _coerce_float(retry_after, default=0.0),
            self._status_cache_seconds(),
        )

    def refresh(
        self,
        *,
        allow_cached_status: bool = False,
        allow_stale_fallback: bool = False,
    ):
        cache_payload = self._load_status_cache()

        if allow_cached_status and (
            self._cache_is_rate_limited(cache_payload) or self._cache_is_fresh(cache_payload)
        ):
            if cache_payload is not None:
                self._apply_cached_state(cache_payload)
                return

        self.ensure_connected()
        assert self.sp is not None

        try:
            track = self.sp.current_user_playing_track()
            liked_status = self._liked_status_for_track(
                track,
                cache_payload=cache_payload,
                reuse_cached_status=allow_cached_status,
            )
            self._apply_state(track, liked_status=liked_status)
            self._write_status_cache()
        except SpotifyException as exc:
            if allow_stale_fallback and exc.http_status == 429 and cache_payload is not None:
                updated_payload = dict(cache_payload)
                updated_payload['rate_limited_until'] = time.time() + self._retry_after_seconds(exc)
                self._write_status_cache_payload(updated_payload)
                self._apply_cached_state(updated_payload)
                return

            raise

    def next(self):
        self.ensure_connected()
        assert self.sp is not None
        self.sp.next_track()
        self._invalidate_status_cache()

    def play(self):
        self.ensure_connected()
        assert self.sp is not None
        if self.play_status:
            self.play_status = False
            self.sp.pause_playback()
        else:
            self.play_status = True
            self.sp.start_playback()
        self._write_status_cache()

    def previous(self):
        self.ensure_connected()
        assert self.sp is not None
        self.sp.previous_track()
        self._invalidate_status_cache()
        # self.sp.seek_track(0)

    def setup(self):
        try:
            config_path = Path(user_config_dir('spotidry'))
            config_file = config_path.joinpath('spotidry.yaml')

            print('Setting up Spotidry')

            print('Opening Spotify Developer Dashboard...')
            wb.open_new_tab('https://developer.spotify.com/dashboard/login')

            print('1. Create a new App')
            print("2. Ensure the 'Web API' is selected")

            client = input('Enter Client ID: ')
            secret = input('Enter Client Secret: ')
            uri = input('Enter Redirect URI (Eg http://127.0.0.1:9999): ')

            config = dict(
                client_id=client,
                client_secret=secret,
                redirect_uri=uri,
            )
            config_path.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.dump(config, file)

            print(f'Wrote config to {config_file}')
        except KeyboardInterrupt:
            print('\nCancelled')

    def save(self):
        """
        Save song to Liked tracks if not liked yet
        Remove song from Liked tracks if liked already
        """

        self.ensure_connected()
        assert self.sp is not None

        if self.liked_status:
            self.liked_status = False
            self.sp.current_user_saved_tracks_delete(tracks=[self.track_id])
        else:
            self.liked_status = True
            self.sp.current_user_saved_tracks_add(tracks=[self.track_id])
        self._write_status_cache()

    def print_info(self):
        """
        Print a fancy status line
        """
        artist, song = self._artist_and_song()
        play_symbol = '⏸' if self.play_status else '▶'
        liked_symbol = '❤' if self.liked_status else '♡'

        artist_song = f'{artist} - {song}'

        max_width = self.config.get('max_width')
        if max_width is not None:
            try:
                width = int(max_width)
            except (TypeError, ValueError):
                width = 0

            scroll_speed = self.config.get('scroll_speed', 0.5)
            scroll_gap = self.config.get('scroll_gap', '   ')
            speed = _coerce_float(scroll_speed, default=0.5)

            offset = int(time.time() / speed) if speed and speed > 0 else 0
            artist_song = _scroll_loop(artist_song, width=width, offset=offset, gap=str(scroll_gap))

        default_fmt = '{play_symbol} {artist_song} {liked_symbol}'
        fmt = self.config.get('output_format', default_fmt)

        try:
            print(
                fmt.format(
                    artist=artist,
                    song=song,
                    artist_song=artist_song,
                    play_symbol=play_symbol,
                    liked_symbol=liked_symbol,
                )
            )
        except KeyError as e:
            print(f'Invalid key in output_format: {e}')
            print(
                default_fmt.format(
                    artist=artist,
                    song=song,
                    artist_song=artist_song,
                    play_symbol=play_symbol,
                    liked_symbol=liked_symbol,
                )
            )

    def print_stopped(self):
        print(' ⏹')
