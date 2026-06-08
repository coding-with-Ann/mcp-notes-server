# MCP Notes Server

A production-ready Python Model Context Protocol server that stores notes in SQLite and exposes them as MCP tools. The project uses the Python MCP SDK API style, Pydantic validation, and a small repository/service boundary that is straightforward to test.

## Features

- SQLite-backed note storage
- Pydantic request and response models
- MCP tools for creating, reading, updating, deleting, listing, and searching notes
- Standard-library test suite under `tests/`

## Requirements

- Python 3.10+

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running

Run the server over stdio:

```bash
python -m mcp_notes_server
```

By default, the database is created at `./mcp_notes.sqlite3`. Override it with:

```bash
$env:MCP_NOTES_DB = "C:\path\to\notes.sqlite3"
python -m mcp_notes_server
```

## MCP Tools

- `create_note(title, content, tags=None)` creates a note.
- `get_note(note_id)` returns a note by id.
- `update_note(note_id, title=None, content=None, tags=None)` updates note fields.
- `delete_note(note_id)` deletes a note.
- `list_notes(limit=20, offset=0)` returns recent notes.
- `search_notes(query, limit=20)` searches title, content, and tags.

## Testing

Run the standard unittest suite:

```bash
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```
