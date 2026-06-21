## 1. Database Schema (db.py)

- [x] 1.1 Add `grammar_topics` table to `init_db()` with columns: id, name_zh, name_en, category, content; UNIQUE on name_zh

## 2. grammar.py (new file)

- [x] 2.1 Implement `search_topics(keyword: str) -> list[dict]` — LIKE search on name_zh and name_en
- [x] 2.2 Implement `list_all_topics() -> dict[str, list[dict]]` — return all topics grouped by category
- [x] 2.3 Implement `format_topic(topic: dict) -> str` — format single topic for Telegram reply
- [x] 2.4 Implement `format_candidates(topics: list[dict]) -> str` — format numbered candidate list

## 3. init_grammar.py (new file)

- [x] 3.1 Define TOPICS list with all 39 entries (name_zh, name_en, category)
- [x] 3.2 Write Gemini system prompt enforcing the 6-section format (📌 📐 ✅ ❌ ❓ ⚠️)
- [x] 3.3 Implement main loop: for each topic, call Gemini, INSERT OR IGNORE, print progress
- [x] 3.4 Add 3s sleep between calls and error handling (log + skip on failure)

## 4. Telegram Handlers (main.py)

- [x] 4.1 Add `/review` handler: call `search_topics()`, reply with full content or candidate list or not-found message
- [x] 4.2 Add `/grammarlist` handler: call `list_all_topics()`, format by category, reply
- [x] 4.3 Register both handlers with `CommandHandler` in `main()`
- [x] 4.4 Update `START_TEXT` to mention `/review` and `/grammarlist`

## 5. Run init_grammar.py

- [ ] 5.1 Run `init_grammar.py` locally to populate grammar_topics in local DB
- [ ] 5.2 Copy `bot/db.py`, `bot/grammar.py`, `bot/init_grammar.py`, `bot/main.py` to GCP VM
- [ ] 5.3 Run `init_grammar.py` on GCP VM to populate remote DB
- [ ] 5.4 Restart `podcast-bot` service on GCP VM

## 6. Verification

- [ ] 6.1 `/grammarlist` — confirm all 39 topics appear grouped by category
- [ ] 6.2 `/review 完成` — confirm candidate list with 6 entries
- [ ] 6.3 `/review 現在完成式` — confirm full format with all 6 sections
- [ ] 6.4 `/review present perfect` — confirm English keyword matches
- [ ] 6.5 `/review xyz123` — confirm not-found message with /grammarlist hint
- [ ] 6.6 `/review wish` — confirm wish / if only 句型 appears
- [ ] 6.7 `/review question tag` — confirm 附加問句 appears
