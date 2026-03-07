# Quickstart: Phrase Search Tiers (012)

**Branch**: `012-phrase-search-tiers`

Run the application and database from the repo root. Single entry point: `run.sh`. Control-C stops everything.

---

## Prerequisites

- **Python**: 3.11+ (or version stated in plan/research).
- **OrbStack**: Installed and running (Docker-compatible; used for PostgreSQL and any other DB services).
- **Repo root**: All commands from the Voicinator repository root.

---

## One-command run

From the repository root:

```bash
./run.sh
```

**What `run.sh` does** (implementation must follow this contract):

1. **Venv**: Create a virtualenv in the repo (e.g. `.venv`) if it does not exist; activate it.
2. **Dependencies**: Install Python dependencies from `requirements.txt` (e.g. `pip install -r requirements.txt` or equivalent).
3. **Database**: Start database (and any other services) via OrbStack. For example:
   - `docker compose up -d` (or `orb start` if needed first) so PostgreSQL and required containers are running.
4. **App**: Start the Python application (e.g. `python -m src` or `uvicorn src.api:app`).
5. **Shutdown**: On Control-C (SIGINT), the script traps the signal, stops the application, then brings down containers (e.g. `docker compose down`) so that "Control-C stops everything."

**Result**: Application and DB are running; API (if applicable) is available at the documented base URL (e.g. localhost:8027). Stopping with Control-C leaves no lingering containers.

---

## Manual steps (if not using run.sh)

Only if you need to run pieces separately:

1. **Venv and deps**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database (OrbStack)**:
   ```bash
   docker compose up -d
   ```
   Ensure `docker compose` points at the project’s compose file (e.g. `compose.yaml` or `docker-compose.yml` at repo root).

3. **Application**:
   ```bash
   python -m src
   # or: uvicorn src.api:app --host 0.0.0.0 --port 8027
   ```

4. **Stop**:
   ```bash
   docker compose down
   ```

---

## Configuration

- **DB connection**: Via environment variables or a config file (e.g. `DATABASE_URL`). Defaults should work for local OrbStack PostgreSQL (e.g. host localhost, port 5432).
- **Search**: Exact and approximate tiers use PostgreSQL; meaning-based may require embedding model or API configuration (see research.md and implementation).

---

## Verify

- Health or root endpoint (e.g. `GET /` or `GET /health`) returns success.
- Search endpoints (see [contracts/search-api.md](contracts/search-api.md)) respond with expected shape for a given query and speaker scope.
