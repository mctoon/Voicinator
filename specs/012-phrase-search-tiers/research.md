# Research: Phrase Search Tiers (012)

**Branch**: `012-phrase-search-tiers` | **Phase 0 output**

## 1. Exact phrase + boolean search (Tier 1)

**Decision**: Use PostgreSQL built-in full-text search with `tsvector` and `tsquery`.

**Rationale**: PostgreSQL supports AND (`&`), OR (`|`), NOT (`!`) and grouping in `tsquery`; `@@` matches documents against a query. Multiple words can be normalized to AND by default; OR and NOT map directly. No extra service required; fits "locally hosted PostgreSQL" (009) and keeps all tiers in one DB.

**Alternatives considered**: Elasticsearch/OpenSearch (heavier, separate stack); external search service (rejected for local-first). Keeping search in PostgreSQL avoids operational and consistency complexity.

---

## 2. Approximate / typo-tolerant phrase search (Tier 2)

**Decision**: Use PostgreSQL extension `pg_trgm` for similarity-based phrase matching.

**Rationale**: `pg_trgm` provides `similarity()`, `word_similarity()`, and the `%` operator with configurable `pg_trgm.similarity_threshold`. GIN/GiST indexes on trigrams make phrase-level fuzzy search efficient. Phrase-only (no boolean) aligns with spec; same DB as exact tier.

**Alternatives considered**: Full-text with dictionary/stemming only (not typo-tolerant); external fuzzy engine (adds dependency). pg_trgm is standard, well-documented, and keeps storage in PostgreSQL.

---

## 3. Meaning-based / semantic search (Tier 3)

**Decision**: Use **pgvector** extension in PostgreSQL to store segment embeddings; compute embeddings in Python (e.g. sentence-transformers or similar) at ingestion; query by embedding similarity (e.g. cosine).

**Rationale**: pgvector is a PostgreSQL extension for vector columns and nearest-neighbor search; works with Psycopg, SQLAlchemy, asyncpg. Embeddings can be generated locally (sentence-transformers) to keep operation local. Same DB as 009 and other tiers; optional synthesis/summary can use same retrieval.

**Alternatives considered**: Dedicated vector DB (e.g. Qdrant, Weaviate) — adds another system; external embedding API only — rejected if "operation remains local" is required. Hybrid: pgvector for storage + local embedding model is the chosen approach.

---

## 4. Python runtime and entry point (run.sh, venv, OrbStack)

**Decision**: Single `run.sh` at repo root that: (1) creates/activates a virtualenv if missing, (2) installs dependencies from `requirements.txt`, (3) starts database (and any other services) via OrbStack/Docker Compose, (4) runs the Python application; on Control-C (SIGINT), script traps and runs `docker compose down` (or equivalent) so everything stops.

**Rationale**: User requirement: "run.sh in base dir", "venv by ensuring all libraries loaded", "libraries in requirements.txt", "database apps in container using OrbStack", "control-c stops everything". OrbStack is Docker-compatible; `docker compose up -d` (or `docker compose up` in foreground) starts containers; trapping SIGINT allows clean shutdown of app and `docker compose down`.

**Alternatives considered**: Separate scripts for DB vs app — rejected in favor of one entry point. systemd/supervisor — overkill for local Mac dev; run.sh + trap is sufficient.

---

## 5. Python API framework and DB layer

**Decision**: Use **FastAPI** for the search API (if HTTP is the primary interface) and **SQLAlchemy 2.x** (with async optional) or **asyncpg** for PostgreSQL. Document in plan and requirements.txt.

**Rationale**: FastAPI gives OpenAPI docs and async support; fits "search API" and future UI consumers. SQLAlchemy is widely used and supports PostgreSQL full-text and raw SQL for tsquery/pg_trgm/pgvector; asyncpg can be used for async-only paths. Choice is implementation detail; spec does not mandate a framework.

**Alternatives considered**: Flask (simpler but no built-in async/OpenAPI); Django (heavier). FastAPI + SQLAlchemy/asyncpg is a common, lightweight stack for a Python API over PostgreSQL.

---

## 6. Segment storage shape (for all tiers)

**Decision**: One or more tables keyed by segment identity: segment id, media id, speaker id, transcript text, start/end timing, and optionally embedding vector (for tier 3). Exact tier: `tsvector` column (or generated) for full-text; approximate: same text column with pg_trgm index; meaning: same table + vector column (pgvector). Normalize to one segment = one row with text + optional vector.

**Rationale**: Spec requires "segment-level transcript text and speaker–media association"; "each segment with exactly one speaker and one media item". Single logical segment table (or segment + FTS/vector tables) keeps scope and speaker filtering consistent across tiers. Details in data-model.md.
