## 1. Bug Fixes (indexer.py)

- [x] 1.1 In `index_transcript()`, add `DELETE FROM cache WHERE context_sentence IS NULL` after the `executemany` insert
- [x] 1.2 In `search_context()`, wrap the FTS5 `MATCH` query in try/except and return `None` on any exception

## 2. Mode Detection (query.py)

- [x] 2.1 Add `GRAMMAR_KEYWORDS = ['文法', '語法', 'grammar']` constant
- [x] 2.2 Implement `_detect_mode(text: str) -> str` with priority: `passage` → `grammar` → `term` → `sentence`
- [x] 2.3 Implement `_strip_grammar_keywords(text: str) -> str` that removes grammar trigger words (case-insensitive)

## 3. System Prompts (query.py)

- [x] 3.1 Replace existing `SYSTEM_PROMPT` / `SYSTEM_PROMPT_NO_CONTEXT` with `PROMPT_TERM`; instruct Gemini to output word + KK phonetic on first line, then meaning, then usage examples or description based on input type
- [x] 3.2 Add `PROMPT_SENTENCE` for > 4-word inputs; meaning + 2–3 sentence usage explanation
- [x] 3.3 Add `PROMPT_GRAMMAR` for grammar analysis; sentence as header, tense/pattern name, structural breakdown, Chinese explanation
- [x] 3.4 Add `PROMPT_PASSAGE` for multi-line input; overall meaning summary + key phrases bullet list

## 4. Update explain() (query.py)

- [x] 4.1 Call `_detect_mode(word)` at the start of `explain()`
- [x] 4.2 For `passage` mode: skip `search_context()`, call Gemini with `PROMPT_PASSAGE`, skip cache write, return result directly
- [x] 4.3 For `grammar` mode: strip grammar keywords from input, call `search_context()` on cleaned text, call Gemini with `PROMPT_GRAMMAR`, skip cache write, return result
- [x] 4.4 For `term` and `sentence` modes: keep existing `search_context()` + cache logic; select `PROMPT_TERM` or `PROMPT_SENTENCE` accordingly

## 5. Verification

- [ ] 5.1 Start the bot and upload a transcript; query a word that appears in the transcript — confirm context is found
- [ ] 5.2 Query the same word before uploading transcript, then upload and query again — confirm stale cache is cleared
- [ ] 5.3 Input a single word (e.g., `accomplish`) — confirm KK phonetic appears on first line
- [ ] 5.4 Input a compound noun (e.g., `blue jay`) — confirm KK phonetic on first line
- [ ] 5.5 Input a phrasal verb (e.g., `back down`) — confirm usage examples appear
- [ ] 5.6 Input a sentence with `文法` (e.g., `She has been running since morning 文法`) — confirm grammar breakdown appears
- [ ] 5.7 Paste a multi-line passage — confirm overall meaning + key phrases appear, no crash
- [ ] 5.8 Input text with FTS5 special characters (e.g., `give: up`) — confirm no crash, graceful response
<!-- 5.1–5.8 require manual testing with a running bot -->
