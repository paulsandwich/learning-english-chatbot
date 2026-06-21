import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bot.db import init_db
from bot import indexer, query, vocab, grammar

load_dotenv()
logging.basicConfig(level=logging.INFO)

TRANSCRIPTS_DIR = Path(__file__).parent.parent / "transcripts"
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

START_TEXT = """👋 歡迎使用 Podcast 英文學習 Bot！

使用方式：
• 直接輸入英文單字或片語 → 取得翻譯與使用情境說明
• 傳送 .txt 逐字稿檔案 → 建立索引，之後查詢時會附上原始情境

指令：
/list — 查看最近查過的 50 個單字
/export — 匯出完整單字本
/review <關鍵字> — 查詢英文文法（例：/review 現在完成式）
/grammarlist — 列出所有文法主題
/start — 顯示此說明"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(START_TEXT)


async def list_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    words = vocab.list_words()
    if not words:
        await update.message.reply_text("單字本是空的，開始查詢後會記錄在這裡。")
        return
    lines = [f"{r['word']} — {r['explanation'].splitlines()[0]}" for r in words]
    await update.message.reply_text("\n".join(lines))


async def export_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = vocab.export_all()
    # Telegram 訊息上限 4096 字，超出截斷
    if len(text) > 4096:
        text = text[:4090] + "\n..."
    await update.message.reply_text(text)


async def review_grammar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = " ".join(context.args).strip() if context.args else ""
    if not keyword:
        await update.message.reply_text("請輸入文法關鍵字，例如：/review 現在完成式")
        return

    topics = grammar.search_topics(keyword)
    if not topics:
        await update.message.reply_text(
            f"找不到「{keyword}」相關的文法。輸入 /grammarlist 查看所有文法清單。"
        )
    elif len(topics) == 1:
        await update.message.reply_text(grammar.format_topic(topics[0]))
    else:
        await update.message.reply_text(grammar.format_candidates(topics))


async def grammar_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    grouped = grammar.list_all_topics()
    if not grouped:
        await update.message.reply_text("文法資料庫尚未初始化，請聯絡管理員執行 init_grammar.py。")
        return

    lines = []
    for category, topics in grouped.items():
        lines.append(f"📚 {category}")
        for t in topics:
            lines.append(f"  • {t['name_zh']}（{t['name_en']}）")
        lines.append("")
    await update.message.reply_text("\n".join(lines).strip())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    word = update.message.text.strip()
    if not word:
        await update.message.reply_text("請輸入一個英文單字或片語。")
        return

    await update.message.chat.send_action("typing")
    try:
        explanation = query.explain(word)
        vocab.save_word(word, explanation)
        await update.message.reply_text(explanation)
    except Exception:
        logging.exception("查詢失敗")
        await update.message.reply_text("查詢暫時失敗，請稍後再試。")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("目前只支援 .txt 格式的逐字稿。")
        return

    await update.message.reply_text("處理中...")
    file = await doc.get_file()
    dest = TRANSCRIPTS_DIR / doc.file_name
    await file.download_to_drive(dest)

    try:
        episode_name = Path(doc.file_name).stem
        count = indexer.index_transcript(dest, episode_name)
        await update.message.reply_text(f"✅ 已完成索引，共 {count} 句")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception:
        logging.exception("索引失敗")
        await update.message.reply_text("索引失敗，請稍後再試。")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("未預期錯誤", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("查詢暫時失敗，請稍後再試。")


def main() -> None:
    init_db()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_vocab))
    app.add_handler(CommandHandler("export", export_vocab))
    app.add_handler(CommandHandler("review", review_grammar))
    app.add_handler(CommandHandler("grammarlist", grammar_list))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
