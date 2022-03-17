'''
Spotify CLI client
'''

from spotidry import __version__
import argparse

def parse_args():
    '''Console script for spotidry'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument(
        '-s', '--save', action='store_true', help='toggle liked track status')
    parser.add_argument('-p', '--play', action='store_true', help='play/pause track')
    parser.add_argument('-n', '--next', action='store_true', help='play next track')
    parser.add_argument(
        '--previous',
        action='store_true',
        help='play previous track/skip to beggining of current track')
    return parser.parse_args()
