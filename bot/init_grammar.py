"""
One-time script to populate grammar_topics table via Gemini.
Run: .venv/bin/python -m bot.init_grammar
"""
import os
import time
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from bot.db import get_conn, init_db

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 模型依序嘗試；免費配額耗盡時自動切換到下一個
MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]

TOPICS = [
    # 時態 (12)
    ("簡單現在式", "Simple Present Tense", "時態"),
    ("現在進行式", "Present Continuous Tense", "時態"),
    ("現在完成式", "Present Perfect Tense", "時態"),
    ("現在完成進行式", "Present Perfect Continuous Tense", "時態"),
    ("簡單過去式", "Simple Past Tense", "時態"),
    ("過去進行式", "Past Continuous Tense", "時態"),
    ("過去完成式", "Past Perfect Tense", "時態"),
    ("過去完成進行式", "Past Perfect Continuous Tense", "時態"),
    ("簡單未來式", "Simple Future Tense", "時態"),
    ("未來進行式", "Future Continuous Tense", "時態"),
    ("未來完成式", "Future Perfect Tense", "時態"),
    ("未來完成進行式", "Future Perfect Continuous Tense", "時態"),
    # 句型 (11)
    ("假設語氣（第一條件句）", "First Conditional", "句型"),
    ("假設語氣（第二條件句）", "Second Conditional", "句型"),
    ("假設語氣（第三條件句）", "Third Conditional", "句型"),
    ("wish / if only 句型", "Wish / If Only Clauses", "句型"),
    ("被動語態", "Passive Voice", "句型"),
    ("間接引語", "Indirect Speech", "句型"),
    ("強調句型", "Cleft Sentence", "句型"),
    ("倒裝句", "Inversion", "句型"),
    ("省略句", "Ellipsis", "句型"),
    ("附加問句", "Question Tags", "句型"),
    ("使役動詞", "Causative Verbs (have/make/get/let)", "句型"),
    # 詞性與修飾 (9)
    ("關係子句", "Relative Clauses", "詞性與修飾"),
    ("分詞構句", "Participial Phrases", "詞性與修飾"),
    ("不定詞用法", "Infinitive Usage", "詞性與修飾"),
    ("動名詞用法", "Gerund Usage", "詞性與修飾"),
    ("比較級與最高級", "Comparatives and Superlatives", "詞性與修飾"),
    ("副詞子句", "Adverbial Clauses", "詞性與修飾"),
    ("名詞子句", "Noun Clauses", "詞性與修飾"),
    ("形容詞子句", "Adjective Clauses", "詞性與修飾"),
    ("冠詞用法", "Article Usage (a/an/the)", "詞性與修飾"),
    # 助動詞與語氣 (7)
    ("can / could 用法", "Can / Could", "助動詞與語氣"),
    ("will / would 用法", "Will / Would", "助動詞與語氣"),
    ("shall / should 用法", "Shall / Should", "助動詞與語氣"),
    ("may / might 用法", "May / Might", "助動詞與語氣"),
    ("must / have to 用法", "Must / Have To", "助動詞與語氣"),
    ("used to 用法", "Used To", "助動詞與語氣"),
    ("had better 用法", "Had Better", "助動詞與語氣"),
]

SYSTEM_PROMPT = """你是英文文法教學專家。用戶給你一個英文文法主題，請用以下格式輸出說明（嚴格遵守，不可增減）：

📌 用法說明：
（2-3句中文，說明此文法的使用時機與語意）

📐 句型結構：
（中文標示句型公式，例如：主詞 + have/has + 過去分詞）

✅ 肯定句：（英文例句，附中文翻譯）
❌ 否定句：（英文例句，附中文翻譯）
❓ 疑問句：（英文例句，附中文翻譯）

⚠️ 常見錯誤：
（1-2句，說明中文母語者最常犯的錯誤）

不可超出以上格式。不加標題行。不加其他說明。"""


def _is_daily_quota_exhausted(error: Exception) -> bool:
    return "GenerateRequestsPerDayPerProjectPerModel-FreeTier" in str(error)


def _is_rate_limit(error: Exception) -> bool:
    return ("429" in str(error) or "503" in str(error)) and not _is_daily_quota_exhausted(error)


def generate_content(name_zh: str, name_en: str, model: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=model,
                contents=f"文法主題：{name_zh}（{name_en}）",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            return response.text.strip()
        except Exception as e:
            if _is_rate_limit(e) and attempt == 0:
                logging.warning(f"  速率限制，等待 15 秒後重試...")
                time.sleep(15)
                continue
            raise


def main() -> None:
    init_db()
    total = len(TOPICS)
    inserted = 0
    skipped = 0
    failed = 0
    model_idx = 0

    logging.info(f"開始產生 {total} 個文法條目...")
    logging.info(f"使用模型：{MODELS[model_idx]}\n")

    for i, (name_zh, name_en, category) in enumerate(TOPICS, 1):
        logging.info(f"[{i}/{total}] {name_zh} ({name_en})")

        with get_conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM grammar_topics WHERE name_zh = ?", (name_zh,)
            ).fetchone()

        if exists:
            logging.info(f"  ✓ 已存在，略過")
            skipped += 1
            continue

        success = False
        while model_idx < len(MODELS):
            model = MODELS[model_idx]
            try:
                content = generate_content(name_zh, name_en, model)
                with get_conn() as conn:
                    conn.execute(
                        "INSERT OR IGNORE INTO grammar_topics (name_zh, name_en, category, content) VALUES (?, ?, ?, ?)",
                        (name_zh, name_en, category, content),
                    )
                logging.info(f"  ✓ 已新增（{model}）")
                inserted += 1
                success = True
                break
            except Exception as e:
                if _is_daily_quota_exhausted(e):
                    model_idx += 1
                    if model_idx < len(MODELS):
                        logging.warning(f"  [{model}] 每日配額耗盡，切換到 {MODELS[model_idx]}")
                    else:
                        logging.error(f"  所有模型配額皆已耗盡，停止。")
                else:
                    logging.error(f"  ✗ 失敗（{model}）：{e}")
                    break

        if not success:
            if model_idx >= len(MODELS):
                logging.error(f"所有模型配額耗盡，共產生 {inserted} 筆後停止。")
                break
            failed += 1

        if i < total:
            time.sleep(3)

    logging.info(f"\n完成！新增 {inserted}，略過 {skipped}，失敗 {failed}")
    logging.info(f"最後使用模型：{MODELS[min(model_idx, len(MODELS)-1)]}")


if __name__ == "__main__":
    main()
