# Spec: grammar-analysis

## Purpose

Defines behavior for `grammar` mode: triggered when user input contains grammar keywords (`文法`, `語法`, `grammar`). Strips keywords before analysis and returns a structured grammar breakdown.

## Requirements

### Requirement: Grammar mode strips trigger keywords before analysis
The system SHALL remove grammar trigger keywords (`文法`, `語法`, `grammar`) from the user input before sending to Gemini, so Gemini receives a clean sentence.

#### Scenario: Keyword stripped from end of sentence
- **WHEN** user sends `She has been running since morning 文法`
- **THEN** Gemini receives `She has been running since morning` with no trailing keyword

#### Scenario: Keyword stripped case-insensitively
- **WHEN** user sends `I gave up Grammar`
- **THEN** Gemini receives `I gave up` with keyword removed

### Requirement: Grammar mode response includes tense, structure, and explanation
The system SHALL format `grammar` mode responses with: the sentence being analyzed, tense/pattern name, structural breakdown, and a Chinese explanation.

#### Scenario: Grammar response format
- **WHEN** user sends a sentence with a grammar keyword
- **THEN** response contains: the cleaned sentence as a header, tense/sentence pattern name, subject/verb/object structural breakdown, and a 2–3 sentence Chinese explanation of the usage
