from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from .models import Note, NoteCreate, NoteUpdate


class NoteNotFoundError(LookupError):
    """Raised when a note id does not exist."""


class NoteRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self.initialize()

    def initialize(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC)"
        )

    def create(self, payload: NoteCreate) -> Note:
        now = _utc_now()
        cursor = self._connection.execute(
            """
            INSERT INTO notes (title, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.title, payload.content, _dump_tags(payload.tags), now, now),
        )
        self._connection.commit()
        return self.get(int(cursor.lastrowid))

    def get(self, note_id: int) -> Note:
        row = self._connection.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        if row is None:
            raise NoteNotFoundError(f"note {note_id} was not found")
        return _row_to_note(row)

    def update(self, note_id: int, payload: NoteUpdate) -> Note:
        current = self.get(note_id)
        updated = {
            "title": payload.title if payload.title is not None else current.title,
            "content": payload.content if payload.content is not None else current.content,
            "tags": payload.tags if payload.tags is not None else current.tags,
        }
        now = _utc_now()
        self._connection.execute(
            """
            UPDATE notes
               SET title = ?, content = ?, tags = ?, updated_at = ?
             WHERE id = ?
            """,
            (
                updated["title"],
                updated["content"],
                _dump_tags(updated["tags"]),
                now,
                note_id,
            ),
        )
        self._connection.commit()
        return self.get(note_id)

    def delete(self, note_id: int) -> bool:
        cursor = self._connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._connection.commit()
        return cursor.rowcount > 0

    def list(self, limit: int = 20, offset: int = 0) -> list[Note]:
        rows = self._connection.execute(
            """
            SELECT * FROM notes
             ORDER BY updated_at DESC, id DESC
             LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [_row_to_note(row) for row in rows]

    def search(self, query: str, limit: int = 20) -> list[Note]:
        pattern = f"%{query.lower()}%"
        rows = self._connection.execute(
            """
            SELECT * FROM notes
             WHERE lower(title) LIKE ?
                OR lower(content) LIKE ?
                OR lower(tags) LIKE ?
             ORDER BY updated_at DESC, id DESC
             LIMIT ?
            """,
            (pattern, pattern, pattern, limit),
        ).fetchall()
        return [_row_to_note(row) for row in rows]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dump_tags(tags: list[str]) -> str:
    return json.dumps(tags, separators=(",", ":"))


def _row_to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=int(row["id"]),
        title=str(row["title"]),
        content=str(row["content"]),
        tags=json.loads(str(row["tags"])),
        created_at=datetime.fromisoformat(str(row["created_at"])),
        updated_at=datetime.fromisoformat(str(row["updated_at"])),
    )
