import pytest
from bot.db import init_db, get_conn


def test_episodes_table_created(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    init_db()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='episodes'"
        ).fetchone()
    assert row is not None


def test_episodes_backfill_from_sentences(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    init_db()
    with get_conn() as conn:
        conn.executemany(
            "INSERT INTO sentences (episode_name, sentence_index, sentence_text) VALUES (?, ?, ?)",
            [("ep1", 0, "Hello."), ("ep1", 1, "World."), ("ep2", 0, "Foo.")],
        )
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT episode_name, sentence_count FROM episodes ORDER BY episode_name"
        ).fetchall()
    assert len(rows) == 2
    assert rows[0]["episode_name"] == "ep1"
    assert rows[0]["sentence_count"] == 2
    assert rows[1]["episode_name"] == "ep2"
    assert rows[1]["sentence_count"] == 1
