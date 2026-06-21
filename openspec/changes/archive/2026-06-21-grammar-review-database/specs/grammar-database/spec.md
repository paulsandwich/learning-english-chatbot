## ADDED Requirements

### Requirement: grammar_topics table stores pre-generated entries
The system SHALL create a `grammar_topics` table with a UNIQUE constraint on `name_zh` to support idempotent insertion.

#### Scenario: Table created on init_db
- **WHEN** `init_db()` is called
- **THEN** `grammar_topics` table exists with columns: id, name_zh, name_en, category, content

#### Scenario: Duplicate insertion is ignored
- **WHEN** `INSERT OR IGNORE` is used with an existing `name_zh`
- **THEN** existing row is preserved and no error is raised

### Requirement: 39 grammar topics across 4 categories
The system SHALL support exactly these categories: 時態, 句型, 詞性與修飾, 助動詞與語氣.

#### Scenario: All categories present after init
- **WHEN** `init_grammar.py` completes successfully
- **THEN** grammar_topics contains entries in all 4 categories with total count of 39
