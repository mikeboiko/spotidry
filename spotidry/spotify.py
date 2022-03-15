'''
Spotify API module
'''

from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import yaml

class Spotidry():
    '''
    Spotify status/commands
    '''

    def load_config(self):
        config_root = Path('~/.config/spotidry').expanduser().resolve()
        with open(config_root.joinpath('spotidry.yaml'), 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.cache_path = config_root.joinpath('.cache')

    def get_play_status(self):
        return self.track['is_playing']

    def get_liked_status(self):
        self.track_id = self.track['item']['id']
        return self.sp.current_user_saved_tracks_contains(tracks=[self.track_id])[0]

    def connect(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                redirect_uri=self.config.get('redirect_uri'),
                scope='user-read-currently-playing user-library-read user-library-modify',
                cache_path=self.cache_path))

    def print_stopped(self):
        print(' ⏹')

    def print_info(self):
        '''
        Print a fancy status line
        '''
        artist = self.track['item']['artists'][0]['name']
        song = self.track['item']['name']
        play_symbol = '▶' if self.get_play_status() else '⏸'
        liked_symbol = '❤' if self.get_liked_status() else '♡'
        print(f'{play_symbol} {artist} - {song} {liked_symbol}')

    def save(self):
        '''
        Save song to Liked tracks if not liked yet
        Remove song from Liked tracks if liked already
        '''

        if self.get_liked_status():
            self.sp.current_user_saved_tracks_delete(tracks=[self.track_id])
        else:
            self.sp.current_user_saved_tracks_add(tracks=[self.track_id])

    def play(self):
        print('play')

    def next(self):
        print('next')

    def previous(self):
        print('previous')

    def __init__(self):
        '''
        Initialize all the variables
        Create Spotify API connection
        '''

        self.load_config()
        self.connect()

        self.track = self.sp.current_user_playing_track()

        self.get_play_status()
        self.get_liked_status()
