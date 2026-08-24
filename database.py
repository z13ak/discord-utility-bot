"""SQLite persistence for the bot — warnings and tags."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bot.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (guild_id, name)
            )
            """
        )
    conn.close()


# ---- Warnings ----

def add_warning(guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
    conn = get_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason),
        )
        warning_id = cur.lastrowid
    conn.close()
    return warning_id


def get_warnings(guild_id: int, user_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY id DESC",
        (guild_id, user_id),
    ).fetchall()
    conn.close()
    return rows


def clear_warnings(guild_id: int, user_id: int) -> int:
    conn = get_connection()
    with conn:
        cur = conn.execute(
            "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        )
        deleted = cur.rowcount
    conn.close()
    return deleted


# ---- Tags ----

def create_tag(guild_id: int, name: str, content: str, created_by: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO tags (guild_id, name, content, created_by) VALUES (?, ?, ?, ?)",
                (guild_id, name.lower(), content, created_by),
            )
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_tag(guild_id: int, name: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM tags WHERE guild_id = ? AND name = ?", (guild_id, name.lower())
    ).fetchone()
    conn.close()
    return row


def delete_tag(guild_id: int, name: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.execute(
            "DELETE FROM tags WHERE guild_id = ? AND name = ?", (guild_id, name.lower())
        )
        deleted = cur.rowcount
    conn.close()
    return deleted > 0


def list_tags(guild_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT name FROM tags WHERE guild_id = ? ORDER BY name ASC", (guild_id,)
    ).fetchall()
    conn.close()
    return rows
