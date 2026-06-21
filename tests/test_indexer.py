import pytest
from pathlib import Path
from bot.db import init_db, get_conn
from bot.indexer import index_transcript


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("bot.db.DB_PATH", tmp_path / "bot.db")
    init_db()
    return tmp_path


def test_index_transcript_writes_episode(tmp_db):
    txt = tmp_db / "ep1.txt"
    txt.write_text("Hello world. How are you? I am fine.")
    index_transcript(str(txt), "ep1")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT episode_name, sentence_count, uploaded_at FROM episodes WHERE episode_name = 'ep1'"
        ).fetchone()
    assert row is not None
    assert row["sentence_count"] == 3
    assert row["uploaded_at"] is not None


def test_reindex_updates_episode(tmp_db):
    txt = tmp_db / "ep1.txt"
    txt.write_text("Hello world. How are you?")
    index_transcript(str(txt), "ep1")
    txt.write_text("Hello world. How are you? I am fine. Great.")
    index_transcript(str(txt), "ep1")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT sentence_count FROM episodes WHERE episode_name = 'ep1'"
        ).fetchone()
    assert row["sentence_count"] == 4
