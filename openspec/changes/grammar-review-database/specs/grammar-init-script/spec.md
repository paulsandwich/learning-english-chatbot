## ADDED Requirements

### Requirement: init_grammar.py populates all 39 topics idempotently
The system SHALL call Gemini once per topic with a strict format prompt, parse the response, and insert via INSERT OR IGNORE.

#### Scenario: Full run inserts all 39 entries
- **WHEN** init_grammar.py runs on an empty grammar_topics table
- **THEN** all 39 entries are inserted and script prints completion summary

#### Scenario: Re-run skips existing entries
- **WHEN** init_grammar.py runs on an already-populated table
- **THEN** no rows are modified and script exits cleanly

#### Scenario: API error on one topic does not abort the run
- **WHEN** Gemini returns an error for one topic
- **THEN** script logs the error, skips that topic, and continues with remaining topics

### Requirement: Gemini prompt enforces the full response format
The system SHALL use a system prompt that requires Gemini to output content in the exact 6-section format (name header, 📌, 📐, ✅, ❌, ❓, ⚠️).

#### Scenario: Generated content matches expected format
- **WHEN** Gemini response is received for any topic
- **THEN** content contains all required emoji section markers
