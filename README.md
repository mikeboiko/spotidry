# Spotidry 

- [Spotidry](#spotidry-)
- [Summary](#summary)
- [Installation](#installation)
- [Setup](#setup)
  - [Spotify API](#spotify-api)
  - [Configuration](#configuration)
  - [Tmux Integration](#tmux-integration)
  - [i3 Integration](#i3-integration)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributions](#contributions)

# Summary

Spotidry is a real dry & boring command-line client for Spotify.

My main motivation for this project is to have a simple client that allows me to save the currently-playing song to my Liked Tracks. I also added play/pause/next/previous commands.

One of the best use cases for `spotidry` is to integrate it into an i3/tmux/vim status line. You can also map some key-bindings or foot-pedals to send `spotidry` command.

Below, is a demo video showing some basic `spotidry` commands, along with a tmux integration.

![](https://raw.githubusercontent.com/mikeboiko/spotidry/gif/resources/spotidry.gif)

# Installation

Install `spotidry` from PyPI:

```
pip install --user spotidry
```

Note: I have only tested `spotidry` on Linux.

# Setup

## Spotify API

You will need to register your app at [My Dashboard](https://developer.spotify.com/dashboard/login) to get the credentials necessary to make authorized calls (a client id and client secret).

You can set your redirect URI to something like "http://127.0.0.1:9999"

## Configuration

Configure your Spotify API variables in `~/.config/spotidry/spotidry.yaml`

```
client_id: "<ID>"
client_secret: "<SECRET>"
redirect_uri: "http://127.0.0.1:9999"
```

## Tmux Integration

I'm using the popular [.tmux](https://github.com/gpakosz/.tmux) config.

I have configured `spotidry` to update 1/s in `~/.tmux/.tmux.conf.local`:

```
tmux_conf_theme_status_right='#(spotidry 2>/dev/null; sleep 1) #{prefix}#{pairing} #{?battery_status, #{battery_status},}#{?battery_bar, #{battery_bar},}#{?battery_percentage, #{battery_percentage},} , %R , %d %b | #{username}#{root} | #{hostname} '
```

## i3 Integration

TODO: Add sample code for i3

# Usage

The first time you run `spotidry`, you will be prompted to authorize the app in your browser.

Run `spotidry --help` to see all commands/options.

```
usage: spotidry [-h] [-v] [-s] [-p] [-n] [--previous]

Spotify CLI client

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -s, --save     toggle liked track status
  -p, --play     play/pause track
  -n, --next     play next track
  --previous     play previous track/skip to beggining of current track

```

# Roadmap

- [x] Save currently playing song to Liked Tracks
- [ ] Add output string customization
- [ ] Add optional socks/https proxy

# Contributions

Contributions are always welcome!

Feel free to submit an issue or a pull request.
