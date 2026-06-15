import re
from pathlib import Path
from bot.db import get_conn


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.?!])\s+', text.strip())
    return [s.strip() for s in parts if s.strip()]


def index_transcript(file_path: str | Path, episode_name: str) -> int:
    sentences = _split_sentences(Path(file_path).read_text(encoding="utf-8"))
    if not sentences:
        raise ValueError("檔案內容為空，無法建立索引")

    with get_conn() as conn:
        conn.execute("DELETE FROM sentences WHERE episode_name = ?", (episode_name,))
        conn.executemany(
            "INSERT INTO sentences (episode_name, sentence_index, sentence_text) VALUES (?, ?, ?)",
            [(episode_name, i, s) for i, s in enumerate(sentences)],
        )

    return len(sentences)


def search_context(query: str) -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT episode_name, sentence_index FROM sentences WHERE sentence_text MATCH ? LIMIT 1",
            (query,),
        ).fetchone()

        if row is None:
            return None

        episode, idx = row["episode_name"], row["sentence_index"]
        indices = [i for i in (idx - 1, idx, idx + 1) if i >= 0]
        placeholders = ",".join("?" * len(indices))
        rows = conn.execute(
            f"SELECT sentence_text FROM sentences WHERE episode_name = ? AND sentence_index IN ({placeholders}) ORDER BY sentence_index",
            (episode, *indices),
        ).fetchall()

    return " ".join(r["sentence_text"] for r in rows)
