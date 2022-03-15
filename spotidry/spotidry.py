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

    def connect(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                redirect_uri=self.config.get('redirect_uri'),
                scope='user-read-currently-playing user-library-read user-library-modify',
                cache_path=self.cache_path))

    def get_status(self):
        track = self.sp.current_user_playing_track()

        if not track:
            print(' ⏹')
            exit()

        artist = track['item']['artists'][0]['name']
        song = track['item']['name']
        play_status = '▶' if track['is_playing'] else '⏸'

        track_id = track['item']['id']
        liked_status = '❤' if self.sp.current_user_saved_tracks_contains(
            tracks=[track_id])[0] else '♡'

        print(f'{play_status} {artist} - {song} {liked_status}')

        # sp.current_user_saved_tracks_delete(tracks=[track_id])
        # sp.current_user_saved_tracks_add(tracks=[track_id])

    def __init__(self, **kwargs):
        '''
        Initialize all the variables
        '''
        self.load_config()
        self.connect()
