# Copilot Instructions for Spotidry Repository

This repository contains a command-line client for Spotify.

## General Guidelines

- **Environment Management**: Always use `uv` for dependency management, environment setup, and running scripts (e.g., `uv run ...`).
- **Code Style**: Run `uv run basedpyright` after changing Python files and make sure there are no errors/warnings reported. Follow standard conventions.
- **Modularity**: Keep functions small and focused on a single task. Separate API logic (Spotify interaction) from CLI/Business logic.
- **Testing**: Add pytest unit tests for any new feature addition or modification. Ensure tests are updated when core logic moves.

## Configuration and API

- **Configuration**: User configuration is handled via YAML files (e.g., `~/.config/spotidry/spotidry.yaml`). ensure new configuration options are documented and backward compatible where possible.
- **Spotify API**: Logic for interacting with the Spotify Web API (authentication, playback control, user library) should remain encapsulated.

## Deployment

- **Versioning**: Version is managed in `spotidry/__init__.py`.
- **Changelog**: All changes must be documented in `CHANGELOG.md` before release.

## Documentation

- Add comments for complex logic.
- Ensure the README is updated as new features or flags are added.
