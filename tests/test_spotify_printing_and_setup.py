from __future__ import annotations

import builtins
from pathlib import Path

from spotidry.spotify import Spotidry


def test_print_info_default_format(capsys, sample_track):
    s = Spotidry.__new__(Spotidry)
    s.track = sample_track
    s.play_status = True
    s.liked_status = False
    s.config = {}

    s.print_info()
    assert capsys.readouterr().out.strip() == '⏸ The Artist - My Song ♡'


def test_print_info_custom_format(capsys, sample_track):
    s = Spotidry.__new__(Spotidry)
    s.track = sample_track
    s.play_status = False
    s.liked_status = True
    s.config = {'output_format': '{artist}:{song}:{play_symbol}:{liked_symbol}'}

    s.print_info()
    assert capsys.readouterr().out.strip() == 'The Artist:My Song:▶:❤'


def test_print_info_invalid_key_falls_back(capsys, sample_track):
    s = Spotidry.__new__(Spotidry)
    s.track = sample_track
    s.play_status = True
    s.liked_status = True
    s.config = {'output_format': '{not_a_key}'}

    s.print_info()
    out = capsys.readouterr().out
    assert 'Invalid key in output_format' in out
    assert '⏸ The Artist - My Song ❤' in out


def test_print_stopped(capsys):
    s = Spotidry.__new__(Spotidry)
    s.print_stopped()
    assert capsys.readouterr().out.strip() == ' ⏹'


def test_setup_writes_config_file(tmp_path, monkeypatch):
    cfg_dir = tmp_path / 'spotidry'
    monkeypatch.setattr('spotidry.spotify.user_config_dir', lambda _: str(cfg_dir))

    opened = {}
    monkeypatch.setattr('spotidry.spotify.wb.open_new_tab', lambda url: opened.setdefault('url', url))

    answers = iter(['id', 'secret', 'http://127.0.0.1:9999'])
    monkeypatch.setattr(builtins, 'input', lambda _prompt: next(answers))

    s = Spotidry.__new__(Spotidry)
    s.setup()

    cfg_file = Path(cfg_dir) / 'spotidry.yaml'
    assert cfg_file.exists()
    text = cfg_file.read_text()
    assert 'client_id' in text
    assert opened['url'].startswith('https://developer.spotify.com/')
