from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator


DEFAULT_DB_PATH = Path("mcp_notes.sqlite3")


def resolve_database_path() -> Path:
    configured = os.getenv("MCP_NOTES_DB")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_DB_PATH


def connect(database_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(database_path) if database_path is not None else resolve_database_path()
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def managed_connection(database_path: Path | str | None = None) -> Iterator[sqlite3.Connection]:
    connection = connect(database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
