"""Main entry point for spotidry"""

from spotidry import cli, spotify
import sys


def main():
    args = cli.parse_args()
    playback_actions_requested = any((args.save, args.play, args.next, args.previous))

    if args.setup and not playback_actions_requested:
        spotify.Spotidry.setup_only()
        return 0

    s = spotify.Spotidry(
        allow_cached_status=not playback_actions_requested,
        allow_stale_fallback=not playback_actions_requested,
    )
    if not s.track:
        s.print_stopped()
        return 0

    if args.save:
        s.save()
    if args.setup:
        s.setup()
    if args.play:
        s.play()
    if args.next:
        s.next()
    if args.previous:
        s.previous()
    if args.next or args.previous:
        s.refresh(allow_cached_status=False, allow_stale_fallback=False)
        if not s.track:
            s.print_stopped()
            return 0
    s.print_info()

    return 0


if __name__ == '__main__':
    sys.exit(main())
