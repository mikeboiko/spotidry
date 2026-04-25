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

- **Versioning**: Version is managed in `spotidry/__init__.py`. Update it only for explicit release preparation.
- **Changelog**: Update `CHANGELOG.md` only when preparing a release. Do not add `Unreleased` entries intended to be committed to `master`.
- **Release Prep**: When asked to prepare a release, bump `spotidry/__init__.py`, add a versioned changelog section for that release, and move the relevant notes into it.
- **Clarify**: If a task might imply a release, ask before changing versioning or other release metadata.

## Documentation

- Add comments for complex logic.
- Ensure the README is updated as new features or flags are added.
