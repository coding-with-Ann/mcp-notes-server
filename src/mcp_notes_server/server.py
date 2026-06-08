from __future__ import annotations

from collections.abc import Callable

from .database import connect
from .repository import NoteRepository
from .service import NoteService


McpFactory = Callable[[str], object]


def create_service() -> NoteService:
    return NoteService(NoteRepository(connect()))


def create_app(
    service_factory: Callable[[], NoteService] = create_service,
    mcp_factory: McpFactory | None = None,
) -> object:
    factory = mcp_factory or _load_fastmcp()
    mcp = factory("sqlite-notes")

    def service() -> NoteService:
        return service_factory()

    @mcp.tool()
    def create_note(title: str, content: str, tags: list[str] | None = None) -> dict:
        """Create a note and return the stored record."""
        return service().create_note(title, content, tags).model_dump(mode="json")

    @mcp.tool()
    def get_note(note_id: int) -> dict:
        """Return a note by id."""
        return service().get_note(note_id).model_dump(mode="json")

    @mcp.tool()
    def update_note(
        note_id: int,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Update one or more fields on a note."""
        return service().update_note(note_id, title, content, tags).model_dump(mode="json")

    @mcp.tool()
    def delete_note(note_id: int) -> dict:
        """Delete a note by id."""
        return service().delete_note(note_id).model_dump(mode="json")

    @mcp.tool()
    def list_notes(limit: int = 20, offset: int = 0) -> dict:
        """List notes ordered by most recently updated."""
        return service().list_notes(limit, offset).model_dump(mode="json")

    @mcp.tool()
    def search_notes(query: str, limit: int = 20) -> dict:
        """Search notes by title, content, or tags."""
        return service().search_notes(query, limit).model_dump(mode="json")

    return mcp


def main() -> None:
    create_app().run()


def _load_fastmcp() -> McpFactory:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP SDK is not installed. Run `python -m pip install -r requirements.txt`."
        ) from exc
    return FastMCP
