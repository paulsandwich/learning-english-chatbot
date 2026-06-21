from bot.db import get_conn


def search_topics(keyword: str) -> list[dict]:
    pattern = f"%{keyword}%"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name_zh, name_en, category, content FROM grammar_topics "
            "WHERE name_zh LIKE ? OR name_en LIKE ? "
            "ORDER BY category, name_zh",
            (pattern, pattern),
        ).fetchall()
    return [dict(r) for r in rows]


def list_all_topics() -> dict[str, list[dict]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT name_zh, name_en, category FROM grammar_topics ORDER BY category, id"
        ).fetchall()
    grouped: dict[str, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r["category"], []).append(dict(r))
    return grouped


def format_topic(topic: dict) -> str:
    return f"{topic['name_zh']} {topic['name_en']}\n\n{topic['content']}"


def format_candidates(topics: list[dict]) -> str:
    lines = ["找到多個相關文法，請輸入更精確的名稱：\n"]
    for i, t in enumerate(topics, 1):
        lines.append(f"{i}. {t['name_zh']}（{t['name_en']}）")
    return "\n".join(lines)
