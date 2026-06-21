# Design: Query Modes & Bug Fixes

Date: 2026-06-21

## Summary

Fix two crashes/bugs in the Telegram bot and introduce four input modes with distinct response formats, replacing the single-prompt approach.

---

## Bug Fixes

### 1. Cache Stale After Transcript Upload

**Problem:** `query.explain()` caches results in the `cache` table. If a word is queried before a transcript is uploaded, the result (including the "未在逐字稿中找到此詞" note) is cached. When the transcript is later uploaded and the same word is queried again, the stale cache is returned — bypassing the FTS5 search entirely.

**Fix:** In `indexer.index_transcript()`, after building the index, delete cache entries where `context_sentence IS NULL`. This clears only results that lacked transcript context, preserving entries that already had context.

```sql
DELETE FROM cache WHERE context_sentence IS NULL
```

### 2. FTS5 Crash on Special Characters / Long Input

**Problem:** `indexer.search_context()` passes the raw user input directly to an FTS5 `MATCH ?` query. Inputs containing FTS5 special characters (`:`, `"`, `?`, `(`, `)`, etc.) or multi-line text cause an sqlite3 exception. This propagates to `handle_text()` in `main.py`, which returns "查詢暫時失敗，請稍後再試。"

**Fix:** Wrap the FTS5 query in a try/except in `search_context()`, returning `None` on any exception. Additionally, `passage` mode skips `search_context()` entirely since the input itself is the context.

---

## Input Mode Detection

Detected in `query.py` by `_detect_mode(text: str) -> str` before calling Gemini. Modes are evaluated in priority order:

| Priority | Mode | Condition |
|---|---|---|
| 1 | `passage` | Input contains `\n` |
| 2 | `grammar` | Input contains any of: `文法`, `語法`, `grammar` (case-insensitive) |
| 3 | `term` | `len(text.split()) <= 4` |
| 4 | `sentence` | Everything else |

---

## Response Formats by Mode

### `term` (≤ 4 words — covers single words, compound nouns, phrasal verbs)

Includes KK phonetic. Gemini determines whether to provide usage examples (phrasal verbs) or a concise description (nouns/compound nouns).

```
blue jay /bluː dʒeɪ/

意思：藍樫鳥，北美常見的藍色鳥類

說明：...
```

```
back down /bæk daʊn/

意思：退讓、讓步、放棄立場

使用情境：
1. He refused to back down even when everyone disagreed.
   （他拒絕退讓，即使所有人都反對。）
2. The company backed down after public outcry.
   （公司在輿論強烈反彈後讓步了。）
3. Don't back down from a challenge just because it's difficult.
   （不要因為挑戰很難就退縮。）
```

### `sentence` (> 4 words, no newlines, no grammar keywords)

Explains the meaning and usage of the phrase/sentence in context.

```
意思：...

用法說明：...（2-3 句）
```

### `grammar` (contains grammar keywords)

Strips the grammar keyword from the input before sending to Gemini.

```
文法解析：She has been running since morning

句型：現在完成進行式（Present Perfect Continuous）
結構：She（主詞）+ has been（助動詞）+ running（現在分詞）+ since morning（時間副詞）
說明：表示從過去某時間點開始，持續到現在仍在進行的動作...
```

### `passage` (contains newlines)

Skips FTS5 search. Gemini explains the overall meaning and highlights key phrases.

```
段落說明：

整體意思：...

重點詞句：
• "phrase one" — 解釋
• "phrase two" — 解釋
```

---

## Architecture Changes

All changes are confined to two files:

### `bot/query.py`
- Add `_detect_mode(text)` function
- Add four system prompts: `PROMPT_TERM`, `PROMPT_SENTENCE`, `PROMPT_GRAMMAR`, `PROMPT_PASSAGE`
- Update `explain()` to select prompt by mode; skip `search_context()` for `passage` mode

### `bot/indexer.py`
- `index_transcript()`: add `DELETE FROM cache WHERE context_sentence IS NULL` after indexing
- `search_context()`: wrap FTS5 query in try/except, return `None` on exception

### `bot/main.py`
- No changes required.

---

## Out of Scope

- Stemming / fuzzy matching for FTS5 (e.g., "running" matching "run")
- Multi-language input detection
- Splitting grammar keywords from the sentence in a linguistically precise way (simple string removal is sufficient)
