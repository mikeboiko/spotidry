'''
Spotify API module
'''

from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import yaml

config_root = Path('~/.config/spotidry').expanduser().resolve()
with open(config_root.joinpath('spotidry.yaml'), 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=config.get('client_id'),
        client_secret=config.get('client_secret'),
        redirect_uri=config.get('redirect_uri'),
        scope='user-read-currently-playing user-library-read user-library-modify',
        cache_path=config_root.joinpath('.cache')))

track = sp.current_user_playing_track()
# print(track)
if not track:
    print('No track currently playing')
    exit()

artist = track['item']['artists'][0]['name']
song = track['item']['name']
play_status = '▶' if track['is_playing'] else '⏸'

track_id = track['item']['id']
liked_status = '❤' if sp.current_user_saved_tracks_contains(tracks=[track_id])[0] else '♡'

print(f'{play_status} {artist} - {song} {liked_status}')

# sp.current_user_saved_tracks_delete(tracks=[track_id])
# sp.current_user_saved_tracks_add(tracks=[track_id])
