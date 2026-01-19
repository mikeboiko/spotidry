from __future__ import annotations

from spotidry.spotify import Spotidry

from conftest import FakeSpotify, SpotifyCallLog


def test_init_sets_state_from_current_track(monkeypatch, sample_track):
    def fake_load_config(self):
        self.config = {'client_id': 'id', 'client_secret': 'secret', 'redirect_uri': 'http://127.0.0.1:9999'}

    def fake_connect(self):
        self.sp = FakeSpotify(track=sample_track, liked=True)

    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry()
    assert s.track == sample_track
    assert s.play_status is True
    assert s.track_id == 'track123'
    assert s.liked_status is True


def test_play_toggles_pause_and_resume(monkeypatch, sample_track):
    log = SpotifyCallLog()

    def fake_load_config(self):
        self.config = {'client_id': 'id', 'client_secret': 'secret', 'redirect_uri': 'http://127.0.0.1:9999'}

    def fake_connect(self):
        self.sp = FakeSpotify(track=sample_track, liked=False, log=log)

    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry()
    assert s.play_status is True

    s.play()
    assert s.play_status is False
    assert log.pause_playback == 1

    s.play()
    assert s.play_status is True
    assert log.start_playback == 1


def test_save_toggles_like_and_calls_api(monkeypatch, sample_track):
    log = SpotifyCallLog()

    def fake_load_config(self):
        self.config = {'client_id': 'id', 'client_secret': 'secret', 'redirect_uri': 'http://127.0.0.1:9999'}

    def fake_connect(self):
        self.sp = FakeSpotify(track=sample_track, liked=False, log=log)

    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry()
    assert s.liked_status is False

    s.save()
    assert s.liked_status is True
    assert log.saved_tracks_add == [['track123']]

    s.save()
    assert s.liked_status is False
    assert log.saved_tracks_delete == [['track123']]


def test_next_previous_call_api(monkeypatch, sample_track):
    log = SpotifyCallLog()

    def fake_load_config(self):
        self.config = {'client_id': 'id', 'client_secret': 'secret', 'redirect_uri': 'http://127.0.0.1:9999'}

    def fake_connect(self):
        self.sp = FakeSpotify(track=sample_track, liked=False, log=log)

    monkeypatch.setattr(Spotidry, 'load_config', fake_load_config)
    monkeypatch.setattr(Spotidry, 'connect', fake_connect)

    s = Spotidry()
    s.next()
    s.previous()
    assert log.next_track == 1
    assert log.previous_track == 1
