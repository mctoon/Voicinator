# Voicinator – Project status

**Last updated**: 2026-03-07

## Overview

Voicinator is a local, quality-first voice fingerprinting and transcription stack for Mac M2. This repo holds docs, specs, and the first feature implementation: **001-inbox-queue-web-ui**.

## 001 Inbox-to-Queue Web UI

**Status**: Implemented (all 41 tasks from `specs/001-inbox-queue-web-ui/tasks.md` completed).

- **Run**: From repo root, `./run.sh` (creates/activates `.venv`, installs deps, starts Flask). Port and bootstrap options from **master config** `voicinator.toml` at repo base (default port 8027). Open http://localhost:8027/ (or the port in `voicinator.toml`).
- **Master config**: `voicinator.toml` at repo root: `[server] port`, optional `[inbox] configPath`. See `voicinator.toml.example`.
- **Inbox config**: TOML or JSON; path from master config `[inbox].configPath`, or `INBOX_CONFIG` env, or default `inbox_queue_config.toml`. See `inbox_queue_config.toml.example`.
- **Stack**: Python 3.11+, Flask, vanilla JS frontend; no database; filesystem-only.
- **Features**: Tabs per path, channel list (with “Move 3”, “Move all”, Explore), explore view with file list and “Queue selected”, media preview subpanel (play/pause, volume, scrubber, jump), two-path tabs (source → destination queue).

## Requirements (from prompts)

- 001-inbox-queue-web-ui: Local web UI to queue media from “Videos not transcribed” to “Videos 1 to be transcribed”; tabbed UI; optional two paths per tab (source/destination); media subpanel; pagination/virtualization; run.sh + requirements.txt; Flask; config file (TOML/JSON).

## Issues / notes

- None currently. Manual verification: run `./run.sh`, open UI, confirm tabs (if config exists), channels, move 3, explore, media subpanel per quickstart.md.
