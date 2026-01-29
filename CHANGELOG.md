<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Async API module `yt_dlp_utils.aio` with `AsyncYoutubeDL`, `get_configured_yt_dlp()`, and
  `setup_session()`.
- Optional `asyncio` extra for async support (`pip install yt-dlp-utils[asyncio]`).

## [0.0.6] - 2025-10-11

### Changed

- Use trusted publishing.

### Fixed

- Python upper version requirement.

## [0.0.5] - 2025-06-08

### Changed

- Updated types used from yt-dlp-types.

## [0.0.4] - 2025-05-28

### Changed

- In `utils.get_configured_yt_dlp()`, accept keyword arguments to pass to `YoutubeDL`.

## [0.0.1] - 2025-00-00

First version.

[unreleased]: https://github.com/Tatsh/yt-dlp-utils/compare/v0.0.6...HEAD
[0.0.6]: https://github.com/Tatsh/yt-dlp-utils/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/Tatsh/yt-dlp-utils/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/Tatsh/yt-dlp-utils/compare/v0.0.3...v0.0.4
[0.0.1]: https://github.com/Tatsh/yt-dlp-utils/releases/tag/v0.0.1
