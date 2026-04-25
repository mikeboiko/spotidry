"""Main entry point for spotidry"""

from spotidry import cli, spotify
import sys


def main():
    args = cli.parse_args()
    track_actions_requested = any((args.save, args.play, args.next, args.previous))
    volume_actions_requested = any((args.volume_show, args.volume_up, args.volume_down))
    actions_requested = track_actions_requested or volume_actions_requested

    if args.setup and not actions_requested:
        spotify.Spotidry.setup_only()
        return 0

    s = spotify.Spotidry(
        allow_cached_status=not actions_requested,
        allow_stale_fallback=not actions_requested,
    )
    if not s.track and not volume_actions_requested:
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
    current_volume: int | None = None
    if args.volume_up:
        current_volume = s.volume_up()
    if args.volume_down:
        current_volume = s.volume_down()
    if (args.next or args.previous) and not volume_actions_requested:
        s.refresh(allow_cached_status=False, allow_stale_fallback=False)
        if not s.track:
            s.print_stopped()
            return 0
    if volume_actions_requested:
        if current_volume is not None:
            s.print_volume(volume_percent=current_volume)
        else:
            s.print_volume()
        return 0
    s.print_info()

    return 0


if __name__ == '__main__':
    sys.exit(main())
