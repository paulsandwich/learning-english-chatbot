import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "bot.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sentences USING fts5(
                episode_name,
                sentence_index UNINDEXED,
                sentence_text,
                tokenize = 'unicode61'
            );

            CREATE TABLE IF NOT EXISTS cache (
                query_key TEXT PRIMARY KEY,
                original_query TEXT NOT NULL,
                explanation TEXT NOT NULL,
                context_sentence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                query_key TEXT NOT NULL UNIQUE,
                explanation TEXT NOT NULL,
                queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS grammar_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_zh TEXT NOT NULL UNIQUE,
                name_en TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL
            );
        """)
