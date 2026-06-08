import sqlite3
import unittest

from mcp_notes_server.models import NoteCreate, NoteUpdate
from mcp_notes_server.repository import NoteNotFoundError, NoteRepository


class NoteRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.repository = NoteRepository(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_create_get_update_delete_note(self):
        created = self.repository.create(
            NoteCreate(title="First", content="Initial content", tags=["alpha"])
        )

        fetched = self.repository.get(created.id)
        self.assertEqual(fetched.title, "First")
        self.assertEqual(fetched.tags, ["alpha"])

        updated = self.repository.update(
            created.id, NoteUpdate(content="Updated content", tags=["beta"])
        )
        self.assertEqual(updated.content, "Updated content")
        self.assertEqual(updated.tags, ["beta"])

        self.assertTrue(self.repository.delete(created.id))
        with self.assertRaises(NoteNotFoundError):
            self.repository.get(created.id)

    def test_list_and_search_notes(self):
        self.repository.create(NoteCreate(title="Alpha", content="Planning", tags=["work"]))
        self.repository.create(NoteCreate(title="Beta", content="Reference", tags=["home"]))

        listed = self.repository.list(limit=10, offset=0)
        self.assertEqual(len(listed), 2)

        results = self.repository.search("work", limit=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Alpha")


if __name__ == "__main__":
    unittest.main()
