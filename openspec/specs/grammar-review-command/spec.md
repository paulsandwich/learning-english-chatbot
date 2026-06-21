## Purpose

Telegram `/review` command that performs fuzzy search on grammar topic names and returns the full pre-generated explanation or a candidate list.

## Requirements

### Requirement: /review performs fuzzy search on grammar topic names
The system SHALL search `name_zh` and `name_en` columns using LIKE '%keyword%' (case-insensitive for English).

#### Scenario: Exact match returns full content
- **WHEN** user sends `/review 現在完成式`
- **THEN** bot replies with full formatted content for that single entry

#### Scenario: Partial match returns candidate list
- **WHEN** user sends `/review 完成`
- **THEN** bot replies with a numbered list of matching topic names (e.g., 現在完成式, 過去完成式...)

#### Scenario: No match returns helpful message
- **WHEN** user sends `/review xyz123`
- **THEN** bot replies: "找不到「xyz123」相關的文法。輸入 /grammarlist 查看所有文法清單。"

#### Scenario: English keyword matches
- **WHEN** user sends `/review present perfect`
- **THEN** bot finds and returns 現在完成式 entry

### Requirement: Full response format includes 4 sections
The system SHALL format grammar topic responses with: 用法說明, 句型結構, 肯定/否定/疑問句, 常見錯誤.

#### Scenario: Response contains all required sections
- **WHEN** a single grammar topic is returned
- **THEN** response contains 📌 用法說明, 📐 句型結構, ✅ 肯定句, ❌ 否定句, ❓ 疑問句, ⚠️ 常見錯誤
