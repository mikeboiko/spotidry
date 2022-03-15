'''
Spotify CLI client
'''

# TODO-MB [220315] - fix import bug
# from spotidry.spotify import Spotidry
from spotify import Spotidry
import argparse
import sys

def parse_args():
    '''Parse CLI arguments'''
    parser = argparse.ArgumentParser(
        usage='spotidry [-h] [-s] [-p] [--next] [-previous]', description=__doc__)
    parser.add_argument(
        '-s', '--save', action='store_true', help='Toggle liked track status')
    parser.add_argument('-p', '--play', action='store_true', help='Play/Pause track')
    parser.add_argument('--next', action='store_true', help='Play next track')
    parser.add_argument(
        '--previous',
        action='store_true',
        help='Play previous track/skip to beggining of current track')

    return parser.parse_args()

def main(args):
    '''Console script for spotidry'''

    s = Spotidry()
    if not s.track:
        s.print_stopped()
        return 0

    if args.save:
        s.save()
    if args.play:
        s.play()
    if args.next:
        s.next()
    if args.previous:
        s.previous()
    s.print_info()

    return 0

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
