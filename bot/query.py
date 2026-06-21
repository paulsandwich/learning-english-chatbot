import os
import re
import time
from google import genai
from google.genai import types
from bot.db import get_conn
from bot.indexer import search_context

GRAMMAR_KEYWORDS = ['文法', '語法', 'grammar']

PROMPT_TERM = """你是英文學習助手。用戶輸入一個英文單字、複合名詞或片語。
回覆格式（嚴格遵守）：
第一行：單字/片語 + KK音標，例如：accomplish /əˈkɑmplɪʃ/
空一行
中文意思：（一行，精簡）
若輸入為片語動詞或慣用語：
使用情境：
1. 英文例句（中文翻譯）
2. 英文例句（中文翻譯）
3. 英文例句（中文翻譯）
若輸入為名詞或複合名詞：
說明：（2句，描述典型用法或含義）
不可超出以上格式。不加其他說明或補充。"""

PROMPT_TERM_WITH_CONTEXT = """你是英文學習助手。用戶輸入一個英文單字、複合名詞或片語，以及它在 Podcast 中出現的句子（上下文）。
回覆格式（嚴格遵守）：
第一行：單字/片語 + KK音標，例如：accomplish /əˈkɑmplɪʃ/
空一行
中文意思：（一行，精簡）
在此情境的用法：（2-3句，說明在這個對話中的含義和語氣）
若輸入為片語動詞或慣用語，額外補充：
使用情境：
1. 英文例句（中文翻譯）
2. 英文例句（中文翻譯）
不可超出以上格式。不加其他說明或補充。"""

PROMPT_SENTENCE = """你是英文學習助手。用戶輸入一個英文句子或較長片語。
回覆格式（嚴格遵守）：
意思：（一行，精簡說明整句中文含義）
用法說明：（2-3句，說明語氣、情境或使用場合）
不可超出以上格式。不加其他說明或補充。"""

PROMPT_SENTENCE_WITH_CONTEXT = """你是英文學習助手。用戶輸入一個英文句子或較長片語，以及它在 Podcast 中出現的上下文。
回覆格式（嚴格遵守）：
意思：（一行，精簡說明整句中文含義）
在此情境的用法：（2-3句，說明在這個對話中的語氣和含義）
不可超出以上格式。不加其他說明或補充。"""

PROMPT_GRAMMAR = """你是英文學習助手。用戶輸入一個英文句子，請進行文法解析。
回覆格式（嚴格遵守）：
文法解析：（原句）
句型：（時態/句型名稱，中英對照，例如：現在完成進行式 Present Perfect Continuous）
結構：（主詞 + 動詞 + 受詞/補語等，用括號標示詞性）
說明：（2-3句中文解釋此句型的用法和語意）
不可超出以上格式。不加其他說明或補充。"""

PROMPT_PASSAGE = """你是英文學習助手。用戶輸入一段英文對話或文章段落。
回覆格式（嚴格遵守）：
段落說明：
整體意思：（2-3句中文，說明這段內容的主旨）
重點詞句：
• "詞句" — 中文解釋
• "詞句" — 中文解釋
• "詞句" — 中文解釋
不可超出以上格式。不加其他說明或補充。"""


def _normalize(word: str) -> str:
    return word.lower().strip()


def _detect_mode(text: str) -> str:
    if '\n' in text:
        return 'passage'
    lower = text.lower()
    if any(kw in lower for kw in GRAMMAR_KEYWORDS):
        return 'grammar'
    if len(text.split()) <= 4:
        return 'term'
    return 'sentence'


def _strip_grammar_keywords(text: str) -> str:
    result = text
    for kw in GRAMMAR_KEYWORDS:
        result = re.sub(re.escape(kw), '', result, flags=re.IGNORECASE)
    return result.strip()


def _call_gemini(system_prompt: str, user_message: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            )
            return response.text.strip()
        except Exception as e:
            if any(code in str(e) for code in ("429", "503")) and attempt == 0:
                time.sleep(10)
                continue
            raise

    raise RuntimeError("Gemini API 呼叫失敗")


def explain(word: str) -> str:
    mode = _detect_mode(word)

    if mode == 'passage':
        user_message = f'段落內容：\n{word}'
        return _call_gemini(PROMPT_PASSAGE, user_message)

    if mode == 'grammar':
        cleaned = _strip_grammar_keywords(word)
        user_message = f'句子："{cleaned}"'
        return _call_gemini(PROMPT_GRAMMAR, user_message)

    key = _normalize(word)

    with get_conn() as conn:
        cached = conn.execute(
            "SELECT explanation FROM cache WHERE query_key = ?", (key,)
        ).fetchone()
        if cached:
            return cached["explanation"]

    context = search_context(word)

    if mode == 'term':
        system_prompt = PROMPT_TERM_WITH_CONTEXT if context else PROMPT_TERM
    else:
        system_prompt = PROMPT_SENTENCE_WITH_CONTEXT if context else PROMPT_SENTENCE

    user_message = f'單字/片語："{word}"'
    if context:
        user_message += f'\nPodcast 原句上下文：{context}'

    explanation = _call_gemini(system_prompt, user_message)

    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache (query_key, original_query, explanation, context_sentence) VALUES (?, ?, ?, ?)",
            (key, word, explanation, context),
        )

    return explanation
