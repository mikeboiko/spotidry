# Spotidry

[![Tests](https://github.com/mikeboiko/spotidry/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/mikeboiko/spotidry/actions/workflows/tests.yml)
[![Publish to PyPI](https://github.com/mikeboiko/spotidry/actions/workflows/publish.yml/badge.svg?branch=master)](https://github.com/mikeboiko/spotidry/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/spotidry)](https://pypi.org/project/spotidry/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/spotidry)](https://pypi.org/project/spotidry/)

Spotidry is a deliberately minimal Spotify CLI for status bars, hotkeys, and quick playback control.

It prints the current track in a compact one-line format, lets you toggle the current song in your Liked Songs, and exposes the playback controls you need without turning your terminal into a full music client.

![Spotidry demo](https://raw.githubusercontent.com/mikeboiko/spotidry/gif/resources/spotidry.gif)

## What it does well

- Print the current Spotify status in a customizable format.
- Toggle the current track in your Liked Songs with a single command.
- Control playback with play/pause, next, and previous actions.
- Scroll long artist/title strings cleanly in narrow status bars.
- Reuse recent playback data to keep 1 Hz status lines responsive and avoid unnecessary Spotify requests.

## Installation

Install from PyPI with `uv`:

```bash
uv tool install spotidry
spotidry --setup
```

Or install with `pip`:

```bash
pip install --user spotidry
spotidry --setup
```

Spotidry is tested on Linux across Python 3.10 through 3.13.

## Spotify setup

Run `spotidry --setup` to create the config file interactively. The command opens the Spotify Developer Dashboard and prompts you for the values it needs.

1. Create a Spotify app at [My Dashboard](https://developer.spotify.com/dashboard/login).
2. Make sure the app has **Web API** enabled.
3. Set a redirect URI such as `http://127.0.0.1:9999`.
4. Paste the Client ID, Client Secret, and Redirect URI into the setup prompt.

If you prefer to create the config manually, write this file to `~/.config/spotidry/spotidry.yaml`:

```yaml
client_id: '<ID>'
client_secret: '<SECRET>'
redirect_uri: 'http://127.0.0.1:9999'
output_format: '{play_symbol} {artist_song} {liked_symbol}'

# Optional: scrolling for long titles (useful for 1 Hz status lines)
max_width: 30
scroll_speed: 0.5
scroll_gap: '   '

# Optional: reuse recent playback data between CLI invocations
status_cache_seconds: 5
```

On the first normal run, Spotidry opens a browser window so you can authorize access to your Spotify account.

## Configuration

### Output placeholders

`output_format` supports these placeholders:

- `{artist}`: artist name
- `{song}`: track title
- `{artist_song}`: `"{artist} - {song}"`, including scrolling when enabled
- `{play_symbol}`: playback indicator (`▶` or `⏸`)
- `{liked_symbol}`: liked indicator (`❤` or `♡`)

The default output format is:

```text
{play_symbol} {artist_song} {liked_symbol}
```

### Caching and rate limits

`status_cache_seconds` controls how often Spotidry asks Spotify for fresh playback data. The default of `5` works well for 1 Hz status bars while keeping API traffic low.

- Increase it if your status line refreshes frequently and you still hit rate limits.
- Set it to `0` to fetch fresh data on every invocation.

Recent playback data is cached at `~/.cache/spotidry/status_cache.json`. If Spotify temporarily replies with `429 Too Many Requests`, Spotidry can keep showing the most recent cached status instead of waiting on a long retry window.

## Usage

Common commands:

```bash
spotidry
spotidry --save
spotidry --play
spotidry --next
spotidry --previous
spotidry --setup
```

CLI help:

```text
usage: spotidry [-h] [-v] [-s] [-S] [-p] [-n] [--previous]

Spotify CLI client

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -s, --save     toggle liked track status
  -S, --setup    setup spotidry configuration
  -p, --play     play/pause track
  -n, --next     play next track
  --previous     play previous track/skip to beginning of current track
```

If you need to re-authorize Spotify, delete the auth cache at `~/.cache/spotidry.json` and run Spotidry again.

## Tmux integration

Example for the popular [.tmux](https://github.com/gpakosz/.tmux) config:

```tmux
tmux_conf_theme_status_right='#(flock -n /tmp/spotidry.lock spotidry 2>/dev/null; sleep 1) #{prefix}#{pairing} #{?battery_status, #{battery_status},}#{?battery_bar, #{battery_bar},}#{?battery_percentage, #{battery_percentage},} , %R , %d %b | #{username}#{root} | #{hostname} '
```

This redraws once per second for smooth scrolling. With the default `status_cache_seconds: 5`, Spotify is still refreshed only about once every 5 seconds.

If you do not need 1 Hz scrolling, increase the shell `sleep` to reduce API traffic even further.

## Polybar integration

Add this module to `~/.config/polybar/config.ini`:

```ini
[module/spotidry]
type = custom/script
exec = ~/.local/bin/spotidry
exec-if = test -f ~/.local/bin/spotidry
click-left = ~/.local/bin/spotidry --next 2> /dev/null
click-middle = ~/.local/bin/spotidry --save 2> /dev/null
click-right = ~/.local/bin/spotidry --play 2> /dev/null
interval = 1
```

This uses `interval = 1` for smooth scrolling. With the default cache settings, Spotify is still refreshed only about once every 5 seconds.

To reduce API traffic further, either raise `status_cache_seconds` or increase the Polybar `interval`.

![Polybar screenshot](https://raw.githubusercontent.com/mikeboiko/spotidry/gif/resources/polybar.png)

## Development

Set up a local development environment:

```bash
git clone https://github.com/mikeboiko/spotidry.git
cd spotidry
uv sync --extra test
```

Useful development commands:

```bash
uv run pytest -q
uv run basedpyright spotidry
uv run spotidry --help
```

## Release automation

GitHub Actions handles validation and publishing:

- **Tests** runs on every push, pull request, and manual dispatch.
- **Publish to PyPI** runs after a successful `Tests` run on `master`.
- A release is only created when `spotidry/__init__.py` changes and the version is bumped.

Routine commits should leave `spotidry/__init__.py` and `CHANGELOG.md` alone. Update them together only when preparing an actual release.

When a release is triggered, GitHub Actions will:

1. Create and push the matching Git tag.
2. Build the source distribution and wheel.
3. Validate the package with `twine check`.
4. Create a GitHub Release with the built artifacts.
5. Publish the package to PyPI.

Make sure the repository has a `PYPI_API_TOKEN` secret configured.

## Roadmap

- [x] Save the currently playing song to Liked Songs
- [x] Add output string customization
- [x] Add scrolling text for long titles
- [ ] Add volume controls and status

## Contributing

Issues and pull requests are welcome.
