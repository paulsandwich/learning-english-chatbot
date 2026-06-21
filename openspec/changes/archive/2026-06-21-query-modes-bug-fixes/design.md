## Context

The bot is a Telegram chatbot that accepts English words, phrases, sentences, or transcript files. It uses SQLite FTS5 for transcript indexing and Google Gemini for explanations. Currently it has a single flat response format and two bugs that cause silent failures.

Current flow: user text → `search_context()` (FTS5) → `_call_gemini()` → cache → reply.

## Goals / Non-Goals

**Goals:**
- Fix stale cache after transcript upload
- Fix FTS5 crash on special characters / multi-line input
- Route user input to one of four modes: `term`, `sentence`, `grammar`, `passage`
- Each mode uses a dedicated Gemini system prompt with appropriate response format

**Non-Goals:**
- Stemming or fuzzy FTS5 matching ("running" ≠ "run")
- Multi-language input detection
- Changing the database schema
- Modifying `main.py` or `db.py`

## Decisions

### Decision 1: Mode detection in `query.py`, not `main.py`

`main.py` handles Telegram plumbing. Keeping mode detection in `query.py` means the logic is self-contained and testable without Telegram. `main.py` calls `explain(word)` unchanged.

_Alternative_: Pass a `mode` param from `main.py`. Rejected — splits logic across two files with no benefit.

### Decision 2: Mode priority order

Evaluated top-to-bottom:
1. `passage` — `\n` in input (most unambiguous signal; takes precedence over grammar keywords)
2. `grammar` — any of `文法`, `語法`, `grammar` (case-insensitive)
3. `term` — `len(text.split()) <= 4`
4. `sentence` — everything else

Passage is checked first because a multi-line text might also contain "grammar" but the dominant intent is passage explanation.

### Decision 3: Grammar keyword stripped before sending to Gemini

If the user sends "She has been running 文法", the keyword "文法" is stripped so Gemini receives a clean sentence. Simple `str.replace` for each keyword. This avoids the keyword appearing in the grammar analysis output.

_Alternative_: Send raw text and rely on Gemini to ignore it. Rejected — unpredictable output.

### Decision 4: Cache invalidation on transcript upload clears only context-less entries

`DELETE FROM cache WHERE context_sentence IS NULL` — preserves entries that already had transcript context; only clears words queried before any transcript existed. This is safe because those cached explanations explicitly said "未在逐字稿中找到此詞".

_Alternative_: Clear entire cache on upload. Rejected — loses valid cached explanations needlessly.

### Decision 5: FTS5 errors return `None`, not a re-raise

`search_context()` wraps the FTS5 MATCH in try/except and returns `None` on any sqlite3 error. The caller (`explain()`) already handles `None` context gracefully (uses the no-context prompt). This prevents crashes from propagating.

For `passage` mode, `search_context()` is skipped entirely — the user-provided text is the context.

## Risks / Trade-offs

- **KK phonetic accuracy** → Gemini provides KK phonetic; it may occasionally be imprecise for rare words. Mitigation: acceptable for a learning aid; no dictionary lookup needed.
- **Grammar keyword false positives** → A sentence containing "grammar" as a real word (e.g., "Her grammar is perfect") triggers grammar mode. Mitigation: edge case unlikely in normal use; user can rephrase if needed.
- **`term` mode threshold at 4 words** → A 4-word idiom like "once in a blue moon" is treated as `term`. This is correct behaviour since it's a fixed expression.
- **Cache not invalidated for grammar/passage modes** → These modes are not cached (context varies). Only `term` and `sentence` results are cached. Acceptable.
