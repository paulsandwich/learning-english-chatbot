## ADDED Requirements

### Requirement: Term mode response includes KK phonetic on first line
The system SHALL format `term` mode responses with the word/phrase and its KK phonetic transcription on the first line, followed by Chinese meaning and usage content.

#### Scenario: Single word response
- **WHEN** user inputs a single word (e.g., `accomplish`)
- **THEN** response first line is `accomplish /əˈkɑmplɪʃ/`, followed by Chinese meaning and usage explanation

#### Scenario: Compound noun response
- **WHEN** user inputs a compound noun (e.g., `blue jay`)
- **THEN** response first line is `blue jay /bluː dʒeɪ/`, followed by Chinese meaning and brief description

#### Scenario: Phrasal verb includes usage examples
- **WHEN** user inputs a phrasal verb (e.g., `back down`)
- **THEN** response includes KK phonetic, Chinese meaning, and 2–3 numbered usage example sentences with Chinese translations

### Requirement: Gemini determines noun vs phrasal verb formatting
The system SHALL instruct Gemini to provide usage examples for phrasal verbs and idioms, and a concise description for nouns and compound nouns, based on the nature of the input.

#### Scenario: Noun gets description not examples
- **WHEN** input is a noun or compound noun
- **THEN** Gemini provides meaning and description without numbered example list

#### Scenario: Phrasal verb gets numbered examples
- **WHEN** input is a phrasal verb or idiom
- **THEN** Gemini provides meaning and 2–3 numbered example sentences with Chinese translations
