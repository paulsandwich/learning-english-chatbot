# Transcript List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/transcripts` Telegram command that lists all uploaded transcripts with name, sentence count, and upload date sorted alphabetically.

**Architecture:** Add an `episodes` table to SQLite to persist transcript metadata. `index_transcript()` writes to this table on every upload. A new `/transcripts` handler queries `episodes` and formats the result.

**Tech Stack:** Python, SQLite, python-telegram-bot

## Global Constraints

- Python virtual environment at `.venv/` — run all commands with `.venv/bin/python` or `.venv/bin/pytest`
- DB path: `data/bot.db` (resolved via `DB_PATH` in `bot/db.py`)
- FTS5 `sentences` table: avoid `COUNT(*)` directly — use `sentences_content` shadow table for counting
- Existing patterns: `get_conn()` returns a context-manager connection with `row_factory = sqlite3.Row`

---

### Task 1: Add `episodes` table and backfill migration

**Files:**
- Modify: `bot/db.py`
- Test: `tests/test_db.py` (create if not exists)

**Interfaces:**
- Produces: `episodes(episode_name TEXT PRIMARY KEY, sentence_count INTEGER NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)` — used by Tasks 2 and 3

- [ ] **Step 1: Write the failing test**

```python
# tests/test_db.py
import pytest
from bot.db import init_db, get_conn

def test_episodes_table_created(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    init_db()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='episodes'"
        ).fetchone()
    assert row is not None

def test_episodes_backfill_from_sentences(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    init_db()
    with get_conn() as conn:
        # Insert raw sentences to simulate pre-existing data
        conn.executemany(
            "INSERT INTO sentences (episode_name, sentence_index, sentence_text) VALUES (?, ?, ?)",
            [("ep1", 0, "Hello."), ("ep1", 1, "World."), ("ep2", 0, "Foo.")],
        )
        # Manually run the backfill (call init_db again — INSERT OR IGNORE is idempotent)
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT episode_name, sentence_count FROM episodes ORDER BY episode_name"
        ).fetchall()
    assert len(rows) == 2
    assert rows[0]["episode_name"] == "ep1"
    assert rows[0]["sentence_count"] == 2
    assert rows[1]["episode_name"] == "ep2"
    assert rows[1]["sentence_count"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_db.py -v
```

Expected: FAIL — `no such table: episodes`

- [ ] **Step 3: Add `episodes` table and backfill to `init_db()`**

In `bot/db.py`, extend the `executescript` inside `init_db()` — add after the `grammar_topics` block:

```python
            CREATE TABLE IF NOT EXISTS episodes (
                episode_name TEXT PRIMARY KEY,
                sentence_count INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Backfill episodes from pre-existing sentences (uploaded_at left NULL)
        conn.execute("""
            INSERT OR IGNORE INTO episodes (episode_name, sentence_count)
            SELECT episode_name, COUNT(*)
            FROM sentences_content
            GROUP BY episode_name
        """)
```

Replace the closing `"""` of the existing `executescript` call so the new table is included, then add the backfill `conn.execute(...)` after the `executescript` block (outside of it, still inside `with get_conn() as conn:`).

Full updated `init_db()`:

```python
def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sentences USING fts5(
                episode_name,
                sentence_index UNINDEXED,
                sentence_text,
                tokenize = 'unicode61'
            );

            CREATE TABLE IF NOT EXISTS cache (
                query_key TEXT PRIMARY KEY,
                original_query TEXT NOT NULL,
                explanation TEXT NOT NULL,
                context_sentence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                query_key TEXT NOT NULL UNIQUE,
                explanation TEXT NOT NULL,
                queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS grammar_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_zh TEXT NOT NULL UNIQUE,
                name_en TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS episodes (
                episode_name TEXT PRIMARY KEY,
                sentence_count INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            INSERT OR IGNORE INTO episodes (episode_name, sentence_count)
            SELECT episode_name, COUNT(*)
            FROM sentences_content
            GROUP BY episode_name
        """)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_db.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add bot/db.py tests/test_db.py
git commit -m "feat: add episodes table with backfill migration"
```

---

### Task 2: Write episode metadata on transcript index

**Files:**
- Modify: `bot/indexer.py`
- Test: `tests/test_indexer.py` (create if not exists)

**Interfaces:**
- Consumes: `episodes(episode_name, sentence_count, uploaded_at)` from Task 1
- Produces: `index_transcript(file_path, episode_name) -> int` — unchanged signature; now also upserts `episodes` row

- [ ] **Step 1: Write the failing test**

```python
# tests/test_indexer.py
import pytest
from pathlib import Path
from bot.db import init_db, get_conn
from bot.indexer import index_transcript

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    monkeypatch.setattr("bot.indexer.get_conn", lambda: __import__("bot.db", fromlist=["get_conn"]).get_conn())
    init_db()
    return tmp_path

def test_index_transcript_writes_episode(tmp_db):
    txt = tmp_db / "ep1.txt"
    txt.write_text("Hello world. How are you? I am fine.")
    index_transcript(str(txt), "ep1")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT episode_name, sentence_count, uploaded_at FROM episodes WHERE episode_name = 'ep1'"
        ).fetchone()
    assert row is not None
    assert row["sentence_count"] == 3
    assert row["uploaded_at"] is not None

def test_reindex_updates_episode(tmp_db):
    txt = tmp_db / "ep1.txt"
    txt.write_text("Hello world. How are you?")
    index_transcript(str(txt), "ep1")
    txt.write_text("Hello world. How are you? I am fine. Great.")
    index_transcript(str(txt), "ep1")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT sentence_count FROM episodes WHERE episode_name = 'ep1'"
        ).fetchone()
    assert row["sentence_count"] == 4
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_indexer.py -v
```

Expected: FAIL — episodes row not written

- [ ] **Step 3: Update `index_transcript()` in `bot/indexer.py`**

Add the upsert after the existing `DELETE FROM cache` line:

```python
def index_transcript(file_path: str | Path, episode_name: str) -> int:
    sentences = _split_sentences(Path(file_path).read_text(encoding="utf-8"))
    if not sentences:
        raise ValueError("檔案內容為空，無法建立索引")

    with get_conn() as conn:
        conn.execute("DELETE FROM sentences WHERE episode_name = ?", (episode_name,))
        conn.executemany(
            "INSERT INTO sentences (episode_name, sentence_index, sentence_text) VALUES (?, ?, ?)",
            [(episode_name, i, s) for i, s in enumerate(sentences)],
        )
        conn.execute("DELETE FROM cache WHERE context_sentence IS NULL")
        conn.execute(
            "INSERT OR REPLACE INTO episodes (episode_name, sentence_count, uploaded_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (episode_name, len(sentences)),
        )

    return len(sentences)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_indexer.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add bot/indexer.py tests/test_indexer.py
git commit -m "feat: write episode metadata to episodes table on index"
```

---

### Task 3: Add `/transcripts` command handler

**Files:**
- Modify: `bot/main.py`
- Test: manual test via Telegram (or inspect handler registration)

**Interfaces:**
- Consumes: `episodes(episode_name, sentence_count, uploaded_at)` from Task 1

- [ ] **Step 1: Add `list_transcripts` handler in `bot/main.py`**

Add after the `grammar_list` function:

```python
async def list_transcripts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with indexer.get_conn() as conn:
        rows = conn.execute(
            "SELECT episode_name, sentence_count, uploaded_at FROM episodes ORDER BY episode_name"
        ).fetchall()
    if not rows:
        await update.message.reply_text("尚未上傳任何逐字稿。")
        return
    lines = [f"📄 已上傳的逐字稿（共 {len(rows)} 份）\n"]
    for r in rows:
        date = r["uploaded_at"][:10] if r["uploaded_at"] else "-"
        lines.append(f"{r['episode_name']}（{r['sentence_count']} 句）｜{date}")
    await update.message.reply_text("\n".join(lines))
```

Note: `indexer.get_conn` isn't exposed — import `get_conn` from `bot.db` directly. Update the import at the top of `main.py`:

```python
from bot.db import init_db, get_conn
```

Then use `get_conn()` in the handler:

```python
async def list_transcripts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT episode_name, sentence_count, uploaded_at FROM episodes ORDER BY episode_name"
        ).fetchall()
    if not rows:
        await update.message.reply_text("尚未上傳任何逐字稿。")
        return
    lines = [f"📄 已上傳的逐字稿（共 {len(rows)} 份）\n"]
    for r in rows:
        date = r["uploaded_at"][:10] if r["uploaded_at"] else "-"
        lines.append(f"{r['episode_name']}（{r['sentence_count']} 句）｜{date}")
    await update.message.reply_text("\n".join(lines))
```

- [ ] **Step 2: Register the handler and update `/start` text**

In `main()`, add after the `grammarlist` handler:

```python
app.add_handler(CommandHandler("transcripts", list_transcripts))
```

Update `START_TEXT` to include the new command:

```python
START_TEXT = """👋 歡迎使用 Podcast 英文學習 Bot！

使用方式：
• 直接輸入英文單字或片語 → 取得翻譯與使用情境說明
• 傳送 .txt 逐字稿檔案 → 建立索引，之後查詢時會附上原始情境

指令：
/list — 查看最近查過的 50 個單字
/export — 匯出完整單字本
/transcripts — 列出已上傳的逐字稿
/review <關鍵字> — 查詢英文文法（例：/review 現在完成式）
/grammarlist — 列出所有文法主題
/start — 顯示此說明"""
```

- [ ] **Step 3: Verify registration**

```bash
.venv/bin/python -c "
from bot.main import main
import inspect
src = inspect.getsource(main)
assert 'transcripts' in src
print('OK — transcripts handler registered')
"
```

Expected: `OK — transcripts handler registered`

- [ ] **Step 4: Commit**

```bash
git add bot/main.py
git commit -m "feat: add /transcripts command to list uploaded transcripts"
```

---

### Task 4: Deploy to GCP VM

- [ ] **Step 1: Deploy changed files**

```bash
gcloud compute scp bot/db.py bot/indexer.py bot/main.py \
    instance-for-oneapi:~/learning-english-chatbot/bot/ \
    --zone=us-west1-b --project=oneapi-496006
```

- [ ] **Step 2: Restart service**

```bash
gcloud compute ssh instance-for-oneapi --zone=us-west1-b --project=oneapi-496006 \
    --command="sudo systemctl restart podcast-bot && sleep 2 && sudo systemctl status podcast-bot --no-pager"
```

Expected: `Active: active (running)`

- [ ] **Step 3: Push to GitHub**

```bash
git push origin main
```
