# Design: /transcripts Command

## Overview

Add a `/transcripts` Telegram command that lists all uploaded transcripts with their name, sentence count, and upload date — sorted alphabetically.

## Data Layer

**New table in `bot/db.py`:**

```sql
CREATE TABLE IF NOT EXISTS episodes (
    episode_name TEXT PRIMARY KEY,
    sentence_count INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Migration for existing data:** `init_db()` runs a one-time backfill after creating the table:

```sql
INSERT OR IGNORE INTO episodes (episode_name, sentence_count)
SELECT episode_name, COUNT(*) FROM sentences_content GROUP BY episode_name
```

Upload time for backfilled rows is `NULL` (cannot be recovered).

## Indexer Layer

In `bot/indexer.py`, `index_transcript()` inserts or replaces the episode record after indexing sentences:

```sql
INSERT OR REPLACE INTO episodes (episode_name, sentence_count, uploaded_at)
VALUES (?, ?, CURRENT_TIMESTAMP)
```

Re-uploading the same filename updates sentence count and timestamp.

## Command Layer

New handler in `bot/main.py`:

- Command: `/transcripts`
- Query: `SELECT episode_name, sentence_count, uploaded_at FROM episodes ORDER BY episode_name`
- Format each row: `<name>（<count> 句）｜<YYYY-MM-DD or ->` 
- Header: `📄 已上傳的逐字稿（共 N 份）`
- Empty state: `尚未上傳任何逐字稿。`

## Output Example

```
📄 已上傳的逐字稿（共 3 份）

no-stupid-questions-ep1（342 句）｜2026-06-15
no-stupid-questions-ep2（289 句）｜2026-06-18
ted-talk-vulnerability（415 句）｜-
```

## Notes

- No Gemini API calls — purely local DB reads.
- Rows with `uploaded_at = NULL` (backfilled) display `-` for date.
- `/start` help text should mention `/transcripts`.
