# Coding Standards

Project-wide coding standards for Voiceinator. Update this file as the team agrees on conventions.

---

## Style and naming

- **Braces:** Allman style (opening brace on its own line).
- **Naming:** camelCase for identifiers. Hungarian notation where appropriate:
  - **Prefixes:** `m_` member variables, `s_` static, `g_` global. Single-letter for primitives (e.g. `i` int, `s` string, `l` 64 bit int, `b` boolean); 3+ letter for complex types.
  - **Collections:** Use descriptive suffixes: `List`, `Dict`, `Set`, `Tuple` (e.g. `iPricesList`, `configDict`).
- **Tables/DB:** Table names start with lowercase `t`, camelCase (e.g. `tChannel`, `tFolder`) and do not have dash or underscore. Column naming: see **Database columns** below.
- **Functions/methods:** No leading underscore unless there is a reason (e.g. private).

**Method and function naming (camelCase):**
Use the camelCase for method and function names.  Do not use underscores in method and functions names unless for compatibility with an external requirement.

**Database columns (Hungarian + camelCase):**

Use the same single-letter type prefix as in code, then camelCase. No separate suffix for timestamps (the prefix indicates type).

| Type | Prefix | Example column names |
|------|--------|----------------------|
| String (TEXT) | `s` | `sFolderPath`, `sChannelId`, `sChannelUrl`, `sVideoId`, `sReason`, `sUtilityName`, `sLastVideoId` |
| Integer (PK/FK or count) | `i` | `id`, `iFolderId`, `iChannelId` (when FK to tChannel.id) |
| 64-bit ms since 1970 | `l` | `lCreatedAt`, `lUpdatedAt` |

Rules: (1) Table name: `t` + camelCase. (2) Column name: type prefix + camelCase. (3) Index names: `idx_` + table + column(s), e.g. `idx_tFolder_sFolderPath`. (4) Foreign keys: integer FKs use `i` (e.g. `iFolderId`, `iChannelId`); string IDs (e.g. YouTube channel ID) use `s` (e.g. `sChannelId`).

**Hungarian examples (code variables):**

| Meaning / DB column | Variable name (code) | Prefix |
|---------------------|----------------------|--------|
| Path string         | `sFolderPath`        | `s` = string |
| Video ID string     | `sLastVideoId`       | `s` = string |
| Timestamp (ms)      | `lUpdatedAt`         | `l` = 64-bit int (long) |

Code variables that hold DB values use the same prefixed name as the column (e.g. column `sFolderPath` → variable `sFolderPath`).

## Python-specific

- **Version:** Target Python 3.x; note version in a comment at top of each file where relevant.
- **Statements:** One statement per line; avoid semicolons.
- **Docs:** Add pydoc comments for modules and public functions.
- **Primitives:** Prefix only primitives with a single letter when appropriate; no prefix required for every identifier.

## Project layout

- **Small functions and files:** Prefer multiple smaller files over large ones.
- **Entry point:** `run.sh` sets up venv and runs the app; keep library list in `requirements.txt` (or equivalent).

