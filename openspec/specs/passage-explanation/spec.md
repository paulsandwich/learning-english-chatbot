# Spec: passage-explanation

## Purpose

Defines behavior for `passage` mode: triggered when user input contains newlines. Skips FTS5 search and cache, returns an overall meaning summary with key phrase highlights.

## Requirements

### Requirement: Passage mode summarises overall meaning and highlights key phrases
The system SHALL format `passage` mode responses with an overall meaning summary followed by a bullet list of key phrases with Chinese explanations.

#### Scenario: Multi-line passage response
- **WHEN** user sends a multi-line passage (input contains `\n`)
- **THEN** response contains: an overall meaning section (2–3 sentences in Chinese) and a key phrases section with bullet points, each showing the English phrase and its Chinese meaning

#### Scenario: FTS5 search skipped for passage
- **WHEN** mode is `passage`
- **THEN** no FTS5 `search_context()` call is made and no transcript context is appended to the Gemini request

### Requirement: Passage response is not cached
The system SHALL NOT cache passage mode results, since multi-line passages are unlikely to be queried identically twice and caching them would waste storage.

#### Scenario: Passage result not written to cache
- **WHEN** a `passage` mode query is completed
- **THEN** no row is inserted or updated in the `cache` table
