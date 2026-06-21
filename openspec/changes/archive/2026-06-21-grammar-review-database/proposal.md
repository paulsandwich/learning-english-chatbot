## Why

The bot currently only analyzes grammar of user-provided sentences. There is no way to look up or review English grammar concepts proactively. Adding a pre-built grammar reference database lets users review specific grammar topics on demand without needing to form example sentences first.

## What Changes

- **New**: `grammar_topics` SQLite table storing 39 pre-generated grammar entries
- **New**: `bot/grammar.py` — search, list, and format grammar topics
- **New**: `bot/init_grammar.py` — one-time script to populate the DB via Gemini
- **New**: `/review <keyword>` command — fuzzy search grammar topics by Chinese or English name
- **New**: `/grammarlist` command — list all grammar topics grouped by category

## Capabilities

### New Capabilities

- `grammar-database`: SQLite schema and CRUD for grammar_topics table
- `grammar-review-command`: `/review` command with fuzzy search and full-format response
- `grammar-list-command`: `/grammarlist` command listing all topics by category
- `grammar-init-script`: One-time Gemini-powered script to populate 39 grammar entries

### Modified Capabilities

_(none)_

## Impact

- `bot/db.py`: Add `grammar_topics` table creation to `init_db()`
- `bot/grammar.py`: New file
- `bot/init_grammar.py`: New file (run once)
- `bot/main.py`: Add two new command handlers
- `bot/vocab.py`: No changes
- `bot/query.py`: No changes
- `bot/indexer.py`: No changes
