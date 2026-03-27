# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Runtime dependency on **replayt** `>=0.4.25` (lower bound only). The package does not import **replayt** yet; this
  floor matches the first integration surface and PyPI versions verified at pin time.

### Documentation

- **README:** compatibility one-liner, how to check the installed **replayt** version, PyPI and release-history links,
  and [GitHub Issues](https://github.com/flogat/replayt-lifecycle-webhooks/issues) for breakage reports.
- **`pyproject.toml`:** `Homepage` and `Issues` URLs for this repository.

## [0.1.0] - 2026-03-27

### Added

- Initial scaffold and package layout.
