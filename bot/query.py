import os
import time
import google.generativeai as genai
from bot.db import get_conn
from bot.indexer import search_context

SYSTEM_PROMPT = """你是英文學習助手。用戶輸入一個英文單字或片語，以及它在 Podcast 中出現的句子（上下文）。
回覆格式（嚴格遵守）：
1. 中文意思：（一行，精簡）
2. 在此情境的用法：（2-3句，說明在這個對話中的含義和語氣）
不可超出以上格式。不加其他說明或補充。"""

SYSTEM_PROMPT_NO_CONTEXT = """你是英文學習助手。用戶輸入一個英文單字或片語。
回覆格式（嚴格遵守）：
1. 中文意思：（一行，精簡）
2. 常見用法說明：（2-3句，說明這個詞的典型使用情境）
不可超出以上格式。不加其他說明或補充。"""


def _normalize(word: str) -> str:
    return word.lower().strip()


def _call_gemini(word: str, context: str | None) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT if context else SYSTEM_PROMPT_NO_CONTEXT,
    )

    user_message = f'單字/片語："{word}"'
    if context:
        user_message += f'\nPodcast 原句上下文：{context}'

    for attempt in range(2):
        try:
            response = model.generate_content(user_message)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt == 0:
                time.sleep(5)
                continue
            raise

    raise RuntimeError("Gemini API 呼叫失敗")


def explain(word: str) -> str:
    key = _normalize(word)

    with get_conn() as conn:
        cached = conn.execute(
            "SELECT explanation FROM cache WHERE query_key = ?", (key,)
        ).fetchone()
        if cached:
            return cached["explanation"]

    context = search_context(word)
    explanation = _call_gemini(word, context)

    if context is None:
        explanation += "\n\n（未在逐字稿中找到此詞）"

    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache (query_key, original_query, explanation, context_sentence) VALUES (?, ?, ?, ?)",
            (key, word, explanation, context),
        )

    return explanation
