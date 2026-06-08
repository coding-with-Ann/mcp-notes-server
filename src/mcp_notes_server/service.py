from __future__ import annotations

from .models import DeleteResult, ListResult, Note, NoteCreate, NoteUpdate, SearchResult
from .repository import NoteRepository


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    def create_note(self, title: str, content: str, tags: list[str] | None = None) -> Note:
        return self._repository.create(
            NoteCreate(title=title, content=content, tags=tags or [])
        )

    def get_note(self, note_id: int) -> Note:
        return self._repository.get(_positive_id(note_id))

    def update_note(
        self,
        note_id: int,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> Note:
        if title is None and content is None and tags is None:
            raise ValueError("at least one field must be provided")
        return self._repository.update(
            _positive_id(note_id),
            NoteUpdate(title=title, content=content, tags=tags),
        )

    def delete_note(self, note_id: int) -> DeleteResult:
        checked_id = _positive_id(note_id)
        return DeleteResult(deleted=self._repository.delete(checked_id), note_id=checked_id)

    def list_notes(self, limit: int = 20, offset: int = 0) -> ListResult:
        checked_limit = _bounded_limit(limit)
        checked_offset = _non_negative(offset, "offset")
        return ListResult(
            items=self._repository.list(checked_limit, checked_offset),
            limit=checked_limit,
            offset=checked_offset,
        )

    def search_notes(self, query: str, limit: int = 20) -> SearchResult:
        clean_query = query.strip()
        if not clean_query:
            raise ValueError("query must not be blank")
        checked_limit = _bounded_limit(limit)
        return SearchResult(
            items=self._repository.search(clean_query, checked_limit),
            query=clean_query,
            limit=checked_limit,
        )


def _positive_id(value: int) -> int:
    if value < 1:
        raise ValueError("note_id must be positive")
    return value


def _bounded_limit(value: int) -> int:
    if value < 1 or value > 100:
        raise ValueError("limit must be between 1 and 100")
    return value


def _non_negative(value: int, field_name: str) -> int:
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return value
