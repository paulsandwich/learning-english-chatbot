## Context

The bot uses SQLite for all persistent storage. Existing tables: `sentences` (FTS5), `cache`, `vocabulary`. New `grammar_topics` table fits naturally into this schema. Content is generated once via Gemini and stored as plain text — no re-generation needed at query time.

## Goals / Non-Goals

**Goals:**
- Pre-populate 39 grammar entries across 4 categories via a one-time script
- `/review` with fuzzy LIKE search on name_zh and name_en
- `/grammarlist` listing all entries grouped by category
- Full response format: explanation + structure + examples + common mistakes

**Non-Goals:**
- FTS5 or embedding-based semantic search (LIKE on names is sufficient for 39 entries)
- User-editable grammar content
- Modifying existing grammar analysis mode (sentence + 文法 keyword)

## Decisions

### Decision 1: Plain text content column, no structured sub-fields

Grammar content (explanation, structure, examples, mistakes) is stored as a single pre-formatted `content` TEXT column rather than separate columns. This simplifies the schema and avoids parsing complexity — the content is written once by Gemini and displayed as-is.

_Alternative_: Separate columns per section. Rejected — adds schema complexity with no query benefit since we never filter by section.

### Decision 2: LIKE search on name columns only

Search targets `name_zh` and `name_en` only, not the full `content` column. With 39 entries, content-level search would surface too many false positives (e.g., searching "現在" would match every tense that mentions 現在 in its explanation).

_Alternative_: FTS5 on content. Rejected — overkill for 39 entries, harder to control result quality.

### Decision 3: init_grammar.py is idempotent

Uses `INSERT OR IGNORE` with a UNIQUE constraint on `name_zh`. Re-running the script safely skips existing entries. This allows partial re-runs if Gemini API errors interrupt the initial population.

### Decision 4: `/review` returns list when multiple matches

If search returns > 1 result, reply with a numbered list of names. User then sends the exact name to get the full entry. Keeps responses clean and avoids sending multiple full entries at once.

## Risks / Trade-offs

- **Gemini content quality** → Prompt specifies exact format; spot-check a few entries after init. If any are malformed, re-run for specific entries.
- **init_grammar.py run time** → 39 Gemini calls ≈ 2-3 minutes. Script shows progress. Add 3s sleep between calls to avoid 429s.
- **Content staleness** → Grammar rules don't change, so pre-generated content has indefinite shelf life.
