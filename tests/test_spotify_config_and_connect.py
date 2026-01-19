from __future__ import annotations

import os

import yaml

from spotidry.spotify import Spotidry


def test_load_config_reads_yaml(tmp_path, monkeypatch):
    cfg_dir = tmp_path / 'spotidry'
    cfg_dir.mkdir(parents=True)
    cfg_file = cfg_dir / 'spotidry.yaml'
    cfg_file.write_text(
        "client_id: id\nclient_secret: secret\nredirect_uri: http://127.0.0.1:9999\noutput_format: '{artist}'\n"
    )

    monkeypatch.setattr('spotidry.spotify.user_config_dir', lambda _: str(cfg_dir))

    s = Spotidry.__new__(Spotidry)
    s.load_config()
    assert s.config['client_id'] == 'id'
    assert s.config['output_format'] == '{artist}'


def test_load_config_calls_setup_when_missing(tmp_path, monkeypatch):
    cfg_dir = tmp_path / 'spotidry'

    monkeypatch.setattr('spotidry.spotify.user_config_dir', lambda _: str(cfg_dir))
    monkeypatch.setattr(os.path, 'exists', lambda p: False)

    def fake_setup(self):
        cfg_dir.mkdir(parents=True, exist_ok=True)
        (cfg_dir / 'spotidry.yaml').write_text(
            'client_id: id\nclient_secret: secret\nredirect_uri: http://127.0.0.1:9999\n'
        )

    monkeypatch.setattr(Spotidry, 'setup', fake_setup)

    s = Spotidry.__new__(Spotidry)
    s.load_config()
    assert s.config['client_secret'] == 'secret'


def test_load_config_yaml_error_does_not_raise(tmp_path, monkeypatch, capsys):
    cfg_dir = tmp_path / 'spotidry'
    cfg_dir.mkdir(parents=True)
    cfg_file = cfg_dir / 'spotidry.yaml'
    cfg_file.write_text('not: [valid: yaml')

    monkeypatch.setattr('spotidry.spotify.user_config_dir', lambda _: str(cfg_dir))

    s = Spotidry.__new__(Spotidry)

    def boom(_stream):
        raise yaml.YAMLError('bad yaml')

    monkeypatch.setattr(yaml, 'safe_load', boom)

    s.load_config()
    out = capsys.readouterr().out
    assert 'bad yaml' in out


def test_connect_wires_spotify_oauth(monkeypatch):
    created = {}

    class FakeOAuth:
        def __init__(self, **kwargs):
            created['oauth_kwargs'] = kwargs

    class FakeSpotify:
        def __init__(self, *, auth_manager):
            created['auth_manager'] = auth_manager

    s = Spotidry.__new__(Spotidry)
    s.config = {'client_id': 'id', 'client_secret': 'secret', 'redirect_uri': 'http://127.0.0.1:9999'}

    monkeypatch.setattr('spotidry.spotify.SpotifyOAuth', FakeOAuth)
    monkeypatch.setattr('spotidry.spotify.spotipy.Spotify', FakeSpotify)
    monkeypatch.setattr('spotidry.spotify.user_cache_dir', lambda _: '/tmp/spotidry.json')

    s.connect()

    assert created['oauth_kwargs']['client_id'] == 'id'
    assert 'user-read-currently-playing' in created['oauth_kwargs']['scope']
    assert created['auth_manager'].__class__ is FakeOAuth
