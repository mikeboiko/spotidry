"""Main module."""

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

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=config.get('client_id'),
    client_secret=config.get('client_secret'),
    redirect_uri=config.get('redirect_uri'),
    scope='user-read-currently-playing user-library-read user-library-modify',
    cache_path=config_root.joinpath('.cache')
))

track = sp.current_user_playing_track()
# print(track)
if not track:
    print('No track currently playing')
    exit()

print('Artist:', track['item']['artists'][0]['name'])
print('Song:', track['item']['name'])

if not track['is_playing']:
    print('Track is paused.')
    exit()

track_id = track['item']['id']
saved = sp.current_user_saved_tracks_contains(tracks=[track_id])[0]

if saved:
    print('Track is liked')
    # print('Un-liking Song')
    # sp.current_user_saved_tracks_delete(tracks=[track_id])
else:
    print('Track is not liked')
    # print('Liking Song')
    # sp.current_user_saved_tracks_add(tracks=[track_id])
