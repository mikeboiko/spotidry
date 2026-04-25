"""
Spotify CLI client
"""

from spotidry import __version__
import argparse


def parse_args():
    """Console script for spotidry"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-s', '--save', action='store_true', help='toggle liked track status')
    parser.add_argument('-S', '--setup', action='store_true', help='setup spotidry configuration')
    parser.add_argument('-p', '--play', action='store_true', help='play/pause track')
    parser.add_argument('-n', '--next', action='store_true', help='play next track')
    parser.add_argument(
        '--previous', action='store_true', help='play previous track/skip to beginning of current track'
    )
    parser.add_argument('--volume-show', action='store_true', help='print current device volume')
    parser.add_argument('--volume-up', action='store_true', help='increase current device volume by 10%%')
    parser.add_argument('--volume-down', action='store_true', help='decrease current device volume by 10%%')
    return parser.parse_args()
