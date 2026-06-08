import unittest
from unittest.mock import Mock

from mcp_notes_server.models import Note
from mcp_notes_server.service import NoteService


class NoteServiceTests(unittest.TestCase):
    def test_create_note_validates_and_calls_repository(self):
        repository = Mock()
        repository.create.return_value = _note()
        service = NoteService(repository)

        note = service.create_note(" Title ", " Body ", ["Tag", "tag"])

        self.assertEqual(note.id, 1)
        repository.create.assert_called_once()
        payload = repository.create.call_args.args[0]
        self.assertEqual(payload.title, "Title")
        self.assertEqual(payload.tags, ["tag"])

    def test_update_requires_at_least_one_field(self):
        service = NoteService(Mock())

        with self.assertRaises(ValueError):
            service.update_note(1)

    def test_list_bounds_limit(self):
        service = NoteService(Mock())

        with self.assertRaises(ValueError):
            service.list_notes(limit=101)


def _note() -> Note:
    return Note.model_validate(
        {
            "id": 1,
            "title": "Title",
            "content": "Body",
            "tags": ["tag"],
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
    )


if __name__ == "__main__":
    unittest.main()
