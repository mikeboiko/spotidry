#!/usr/bin/env python

from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from dotenv import load_dotenv

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    redirect_uri=os.getenv('redirect_uri'),
    scope='user-read-currently-playing user-library-read user-library-modify',
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
