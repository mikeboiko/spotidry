from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pytest

# Ensure tests import the local repo package even when run from ./tests.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@pytest.fixture
def sample_track():
    return {
        'is_playing': True,
        'item': {
            'id': 'track123',
            'name': 'My Song',
            'artists': [{'name': 'The Artist'}],
        },
    }


@dataclass
class SpotifyCallLog:
    next_track: int = 0
    previous_track: int = 0
    pause_playback: int = 0
    start_playback: int = 0
    saved_tracks_add: list[list[str]] | None = None
    saved_tracks_delete: list[list[str]] | None = None

    def __post_init__(self):
        self.saved_tracks_add = []
        self.saved_tracks_delete = []


class FakeSpotify:
    def __init__(self, *, track=None, liked=False, log: SpotifyCallLog | None = None):
        self._track = track
        self._liked = liked
        self.log = log or SpotifyCallLog()

    def current_user_playing_track(self):
        return self._track

    def current_user_saved_tracks_contains(self, *, tracks):
        assert isinstance(tracks, list)
        return [self._liked]

    def next_track(self):
        self.log.next_track += 1

    def previous_track(self):
        self.log.previous_track += 1

    def pause_playback(self):
        self.log.pause_playback += 1

    def start_playback(self):
        self.log.start_playback += 1

    def current_user_saved_tracks_add(self, *, tracks):
        self.log.saved_tracks_add.append(tracks)

    def current_user_saved_tracks_delete(self, *, tracks):
        self.log.saved_tracks_delete.append(tracks)
