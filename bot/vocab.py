from bot.db import get_conn


def _normalize(word: str) -> str:
    return word.lower().strip()


def save_word(word: str, explanation: str) -> None:
    key = _normalize(word)
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO vocabulary (word, query_key, explanation, queried_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(query_key) DO UPDATE SET queried_at = CURRENT_TIMESTAMP""",
            (word, key, explanation),
        )


def list_words(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT word, explanation FROM vocabulary ORDER BY queried_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def export_all() -> str:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT word, explanation, queried_at FROM vocabulary ORDER BY queried_at DESC"
        ).fetchall()

    if not rows:
        return "單字本是空的。"

    parts = []
    for r in rows:
        parts.append(f"[{r['queried_at']}] {r['word']}\n{r['explanation']}\n---")
    return "\n".join(parts)
