# Implementation Plan: Phrase Search Tiers (Exact, Approximate, Meaning-Based)

**Branch**: `012-phrase-search-tiers` | **Date**: 2026-03-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/012-phrase-search-tiers/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add three search tiers over the searchable voice database: (1) exact phrase search with boolean word search (AND, OR, NOT, grouping; default AND for multiple words); (2) approximate phrase search (typo-tolerant, phrase-only); (3) meaning-based (semantic) search. All tiers support speaker scope (any, list, one). Store transcript text at segment level with one speaker and one media per segment. Application is Python-based; started via `run.sh` at repo root (venv + requirements.txt, OrbStack for DB); Control-C stops everything.

## Technical Context

**Language/Version**: Python 3.x (e.g. 3.11+); version documented in run.sh and requirements.txt  
**Primary Dependencies**: See research.md; likely FastAPI or Flask for search API, SQLAlchemy or async equivalent for DB, PostgreSQL client; embedding/vector lib for meaning-based tier  
**Storage**: PostgreSQL in OrbStack container; segment-level tables; full-text and optional vector extension (pgvector) per research  
**Testing**: pytest; contract tests for search API; integration tests with test DB  
**Target Platform**: macOS (M2); local; OrbStack for containers  
**Project Type**: Web service (search API) + CLI/scripts for ingestion; run.sh is single entry point  
**Performance Goals**: Implementation-defined and documented at release (no explicit target in spec)  
**Constraints**: run.sh at repo root; venv created/used and libraries from requirements.txt; database apps run in OrbStack container; Control-C stops venv process and containers  
**Coding standards**: [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md) — camelCase and Hungarian notation for identifiers; table names `t` + camelCase; column names type prefix + camelCase; Allman braces; small functions/files; run.sh + requirements.txt. Python: version in file header comment, pydoc for modules and public functions, one statement per line.  
**Scale/Scope**: Segment-level storage; pagination/result limit for large result sets; hundreds of channels / thousands of segments in scope (per related specs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file (`.specify/memory/constitution.md`) is a template and not yet ratified; no formal gates are enforced. Principles to align with when ratified: library-first, clear interfaces, test coverage, observability.

## Project Structure

### Documentation (this feature)

```text
specs/012-phrase-search-tiers/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (search API)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Python app; run.sh at repo root
run.sh                   # Entry point: activate venv, install deps from requirements.txt, start OrbStack containers, run app; Control-C stops all
requirements.txt         # Python dependencies

src/
├── models/              # Domain models (Segment, Speaker, Media, search result shapes)
├── services/            # Search services (exact, approximate, meaning-based); segment ingestion
├── api/                 # HTTP API for search (if web-facing)
└── db/                  # DB connection, migrations, repository layer

tests/
├── contract/            # Search API contract tests
├── integration/         # DB + search integration tests
└── unit/                # Unit tests for services/models
```

**Structure Decision**: Single Python project at repo root. `run.sh` is the only entry point: it ensures a venv, installs from `requirements.txt`, starts OrbStack (database) containers, then runs the application process; Control-C terminates the app and container orchestration. Search is exposed via API (and/or CLI) for operators; segment data is stored in PostgreSQL.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

None at this time.
