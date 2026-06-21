## Why

The bot has two crashes/bugs that cause valid queries to return errors, and a single flat response format that does not adapt to different input types — single words, compound nouns, phrasal verbs, sentences, grammar questions, and passages all deserve different explanations and formatting.

## What Changes

- **Bug fix**: Stale cache causes words queried before a transcript was uploaded to permanently show "未在逐字稿中找到此詞" even after the transcript is indexed
- **Bug fix**: FTS5 MATCH crashes when user input contains special characters (`:`, `"`, `?`, etc.) or newlines, returning a generic error instead of a graceful result
- **New**: `term` mode — inputs ≤ 4 words get KK phonetic transcription, meaning, and usage examples (covers single words, compound nouns like "blue jay", and phrasal verbs like "back down")
- **New**: `sentence` mode — inputs > 4 words with no newlines and no grammar keywords get meaning + usage explanation
- **New**: `grammar` mode — inputs containing "文法", "語法", or "grammar" trigger grammar analysis with sentence breakdown
- **New**: `passage` mode — inputs containing newlines get an overall meaning summary plus key phrase highlights

## Capabilities

### New Capabilities

- `query-mode-detection`: Detect input mode (`term`, `sentence`, `grammar`, `passage`) from user text and route to the appropriate Gemini prompt
- `term-response`: Format responses for single words, compound nouns, and phrasal verbs with KK phonetic + meaning + usage examples
- `grammar-analysis`: Format responses for grammar analysis requests with sentence structure breakdown
- `passage-explanation`: Format responses for multi-line passages with overall meaning and key phrases

### Modified Capabilities

_(none — no existing specs)_

## Impact

- `bot/query.py`: Add `_detect_mode()`, four system prompts, update `explain()` to branch by mode; skip FTS5 search for passage mode
- `bot/indexer.py`: Clear stale cache entries (`context_sentence IS NULL`) after indexing; wrap FTS5 query in try/except
- `bot/main.py`: No changes required
- `bot/db.py`: No changes required
