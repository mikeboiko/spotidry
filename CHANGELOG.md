# Unreleased

# 0.0.10 (2026-03-26)

- Cache playback status between frequent CLI invocations so 1Hz status bars do not hit Spotify on every refresh.
- Reuse stale cached status during Spotify `429` responses and fail fast instead of waiting on long retry windows.

# 0.0.9 (2026-01-19)

- Scrolling Text for Long Titles

# 0.0.8 (2026-01-18)

- Added output string customization

# 0.0.7 (2026-01-18)

- Switch to uv package manager
- Deploy via GH Actions

# 0.0.6 (2025-02-26)

- Version bump

# 0.0.5 (2025-02-26)

- Merged --setup PR from [nigel-dev](https://github.com/mikeboiko/spotidry/pull/1)

# 0.0.4 (2024-09-20)

- Swapped play/pause symbols to align with the standard convention

# 0.0.3 (2024-09-04)

- Fixed playback control permissions

# 0.0.2 (2022-04-04)

- Updated instructions

# 0.0.1 (2022-04-03)

- Initial release
