## Purpose

Telegram `/grammarlist` command that returns all grammar topics grouped by category so users can browse the full grammar database.

## Requirements

### Requirement: /grammarlist displays all topics grouped by category
The system SHALL return all grammar topics sorted by category, with each category as a header.

#### Scenario: All topics listed by category
- **WHEN** user sends `/grammarlist`
- **THEN** bot replies with all 39 topics grouped under 時態, 句型, 詞性與修飾, 助動詞與語氣 headers

#### Scenario: Empty database returns guidance message
- **WHEN** grammar_topics table is empty
- **THEN** bot replies: "文法資料庫尚未初始化，請聯絡管理員執行 init_grammar.py。"
