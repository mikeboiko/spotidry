"""Main entry point for spotidry"""

from spotidry import cli, spotify
import sys

def main():
    args = cli.parse_args()

    s = spotify.Spotidry()
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
    sys.exit(main())
