"""
Spotify API module
"""

from pathlib import Path
import os
import webbrowser as wb
import spotipy
import yaml
from appdirs import user_cache_dir, user_config_dir
from spotipy.oauth2 import SpotifyOAuth


class Spotidry:
    """
    Spotify status/commands
    """

    def __init__(self):
        """
        Initialize all the variables
        Create Spotify API connection
        """

        self.load_config()
        self.connect()

        self.track = self.sp.current_user_playing_track()
        if self.track:
            self.play_status = self.track['is_playing']
            self.track_id = self.track['item']['id']
            self.liked_status = self.sp.current_user_saved_tracks_contains(tracks=[self.track_id])[0]

    def connect(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                cache_path=user_cache_dir('spotidry.json'),
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                redirect_uri=self.config.get('redirect_uri'),
                scope='user-read-currently-playing user-library-read user-library-modify user-modify-playback-state',
            )
        )

    def load_config(self):
        """Load user config from ~/.config/spotidry/spotidry.yaml
        Show error message if config file doesn't exist
        """
        config_file = Path(user_config_dir('spotidry')).joinpath('spotidry.yaml')

        if not os.path.exists(config_file):
            self.setup()

        with open(config_file, 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except FileNotFoundError as exc:
                print(exc)
            except yaml.YAMLError as exc:
                print(exc)

    def next(self):
        self.sp.next_track()

    def play(self):
        if self.play_status:
            self.play_status = False
            self.sp.pause_playback()
        else:
            self.play_status = True
            self.sp.start_playback()

    def previous(self):
        self.sp.previous_track()
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
            with open(config_file, 'w') as file:
                yaml.dump(config, file)

            print(f'Wrote config to {config_file}')
        except KeyboardInterrupt:
            print('\nCancelled')

    def save(self):
        """
        Save song to Liked tracks if not liked yet
        Remove song from Liked tracks if liked already
        """

        if self.liked_status:
            self.liked_status = False
            self.sp.current_user_saved_tracks_delete(tracks=[self.track_id])
        else:
            self.liked_status = True
            self.sp.current_user_saved_tracks_add(tracks=[self.track_id])

    def print_info(self):
        """
        Print a fancy status line
        """
        artist = self.track['item']['artists'][0]['name']
        song = self.track['item']['name']
        play_symbol = '⏸' if self.play_status else '▶'
        liked_symbol = '❤' if self.liked_status else '♡'

        default_fmt = '{play_symbol} {artist} - {song} {liked_symbol}'
        fmt = self.config.get('output_format', default_fmt)

        try:
            print(
                fmt.format(
                    artist=artist,
                    song=song,
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
                    play_symbol=play_symbol,
                    liked_symbol=liked_symbol,
                )
            )

    def print_stopped(self):
        print(' ⏹')
