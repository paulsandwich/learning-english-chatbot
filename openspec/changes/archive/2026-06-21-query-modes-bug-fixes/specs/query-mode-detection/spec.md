## ADDED Requirements

### Requirement: Mode detection routes input to the correct prompt
The system SHALL detect the input mode from user text before calling Gemini, using the following priority order: `passage` → `grammar` → `term` → `sentence`.

#### Scenario: Input with newline is passage mode
- **WHEN** user input contains one or more `\n` characters
- **THEN** mode is `passage` regardless of word count or grammar keywords

#### Scenario: Input with grammar keyword is grammar mode
- **WHEN** user input contains any of `文法`, `語法`, `grammar` (case-insensitive) and has no newlines
- **THEN** mode is `grammar`

#### Scenario: Short input is term mode
- **WHEN** user input has no newlines, no grammar keywords, and `len(text.split()) <= 4`
- **THEN** mode is `term`

#### Scenario: Long input is sentence mode
- **WHEN** user input has no newlines, no grammar keywords, and `len(text.split()) > 4`
- **THEN** mode is `sentence`

### Requirement: Stale cache is cleared on transcript upload
The system SHALL delete all `cache` rows where `context_sentence IS NULL` after successfully indexing a new transcript.

#### Scenario: Cache cleared after indexing
- **WHEN** `index_transcript()` completes successfully
- **THEN** all cache entries with `context_sentence IS NULL` are deleted from the `cache` table

### Requirement: FTS5 errors are handled gracefully
The system SHALL return `None` from `search_context()` when the FTS5 MATCH query raises any exception, rather than propagating the error.

#### Scenario: Special characters in query do not crash
- **WHEN** user input contains FTS5 special characters such as `:`, `"`, `?`, `(`, `)`
- **THEN** `search_context()` returns `None` and the query proceeds with no-context prompt

#### Scenario: Passage mode skips FTS5 search
- **WHEN** mode is `passage`
- **THEN** `search_context()` is not called; the user's text is the context
