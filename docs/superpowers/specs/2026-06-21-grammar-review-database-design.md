# Design: Grammar Review Database

Date: 2026-06-21

## Summary

Add a pre-built English grammar reference database to the bot. Users can query grammar topics via `/review` and list all available topics via `/grammarlist`. Content is generated once by Gemini and stored in SQLite.

---

## Goals / Non-Goals

**Goals:**
- Pre-generate ~39 grammar topic entries (Gemini, one-time script)
- `/review <keyword>` — fuzzy search by Chinese or English name; one result → show full content; multiple → list candidates
- `/grammarlist` — list all grammar topics grouped by category
- Full response format: usage explanation + sentence structure + affirmative/negative/question examples + common mistakes

**Non-Goals:**
- Semantic/embedding-based search
- User-editable grammar entries
- Changing existing `grammar` analysis mode (sentence + 文法 keyword)

---

## Grammar Topics (39 total)

### 時態 (12)
簡單現在式、現在進行式、現在完成式、現在完成進行式、簡單過去式、過去進行式、過去完成式、過去完成進行式、簡單未來式、未來進行式、未來完成式、未來完成進行式

### 句型 (11)
假設語氣（第一條件句）、假設語氣（第二條件句）、假設語氣（第三條件句）、wish / if only 句型、被動語態、間接引語、強調句型（cleft sentence）、倒裝句、省略句、附加問句（Question Tags）、使役動詞（have/make/get/let）

### 詞性與修飾 (9)
關係子句、分詞構句、不定詞用法、動名詞用法、比較級與最高級、副詞子句、名詞子句、形容詞子句、冠詞 a/an/the 用法

### 助動詞與語氣 (7)
can/could、will/would、shall/should、may/might、must/have to、used to、had better

---

## DB Schema

```sql
CREATE TABLE grammar_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_zh TEXT NOT NULL,
    name_en TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL
);
```

Search: `WHERE name_zh LIKE '%<keyword>%' OR name_en LIKE '%<keyword>%'`

---

## Response Format

```
現在完成式 Present Perfect

📌 用法說明：
表示過去發生、對現在仍有影響的動作，或從過去持續到現在的狀態。

📐 句型結構：
主詞 + have/has + 過去分詞 (V-pp)

✅ 肯定句：I have visited Japan twice.
❌ 否定句：She hasn't finished her homework yet.
❓ 疑問句：Have you ever tried sushi?

⚠️ 常見錯誤：
與過去式混淆。有明確過去時間點（yesterday, in 2010）應用過去式，不可用現在完成式。
```

---

## Architecture Changes

| File | Change |
|---|---|
| `bot/db.py` | Add `grammar_topics` table to `init_db()` |
| `bot/grammar.py` | New: `search_topics()`, `list_all_topics()`, `format_topic()` |
| `bot/init_grammar.py` | New: one-time script to generate 39 entries via Gemini and insert into DB |
| `bot/main.py` | Add `/review` and `/grammarlist` command handlers |

---

## init_grammar.py Flow

1. For each of 39 topics, call Gemini with a prompt requesting the full format
2. Parse response, insert into `grammar_topics`
3. Print progress; skip if entry already exists (idempotent)
4. Run once on local machine and on GCP VM after deployment
