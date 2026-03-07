# Quickstart: Inbox-to-Queue Web UI (001)

**Branch**: `001-inbox-queue-web-ui`

Run the inbox-queue web app from the repo root. Single entry point: `run.sh`. Control-C stops the app. No database; config file and filesystem only.

---

## Prerequisites

- **Python**: 3.11+ (or version stated in plan/research).
- **Config**: Create or edit the inbox-queue config file (TOML or JSON) with at least one tab and one or two paths per tab. Paths must point to existing base directories under which channel folders (with "Videos not transcribed" and "Videos 1 to be transcribed") exist.
- **Repo root**: All commands from the Voicinator repository root.

---

## One-command run

From the repository root:

```bash
./run.sh
```

**What `run.sh` does** (implementation must follow this contract):

1. **Venv**: Create a virtualenv in the repo (e.g. `.venv`) if it does not exist; activate it.
2. **Dependencies**: Install Python dependencies from `requirements.txt` (e.g. `pip install -r requirements.txt`).
3. **App**: Start the web application (Flask per research.md) serving the inbox-queue UI and API.
4. **Shutdown**: On Control-C (SIGINT), the script stops the application.

**Result**: Web UI is available at the documented base URL (e.g. `http://localhost:8027/` or the port in `voicinator.toml`). Open in browser; no authentication. Stopping with Control-C leaves no lingering processes.

---

## Manual steps (if not using run.sh)

1. **Venv and deps**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Application**:
   ```bash
   python -m backend
   # or: flask run --host 0.0.0.0 --port 8027
   ```
   Ensure the app is configured to read the inbox-queue config file (path via env or default location).

3. **Stop**: Control-C in the terminal.

---

## Configuration

- **Master config**: `voicinator.toml` at repo root (see `voicinator.toml.example`). Sets `[server] port` (default 8027) and optional `[inbox] configPath` for the inbox tabs config file.
- **Inbox config file**: TOML or JSON (see research.md and data-model.md). Define tabs; each tab has optional display name and one or two paths (source, optional destination). Path from master config, `INBOX_CONFIG` env, or default `inbox_queue_config.toml` at repo root.
- **Paths**: Base paths under which channel folders are discovered. A channel is listed if it has "Videos not transcribed"; "Videos 1 to be transcribed" need not exist (it is created when moving media into that channel).

---

## Verify

- Open the web UI in a browser; tabs appear per config.
- Select a tab; channel list loads (paginated or virtualized).
- For a channel with inbox media: use "move 3", "move all", or explore and queue selected; verify files move to "Videos 1 to be transcribed" and are logged.
- In explore view, select a media file; media subpanel shows and play/pause, volume, scrubber, jump forward/back work (per spec 010).
- API: see [contracts/inbox-queue-api.md](contracts/inbox-queue-api.md) for endpoints and response shapes.
