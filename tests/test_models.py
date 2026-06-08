import unittest

from pydantic import ValidationError

from mcp_notes_server.models import NoteCreate


class NoteCreateTests(unittest.TestCase):
    def test_normalizes_tags_and_text(self):
        payload = NoteCreate(
            title="  Example  ",
            content="  Body  ",
            tags=[" Work ", "work", "", "Ideas"],
        )

        self.assertEqual(payload.title, "Example")
        self.assertEqual(payload.content, "Body")
        self.assertEqual(payload.tags, ["work", "ideas"])

    def test_rejects_blank_title(self):
        with self.assertRaises(ValidationError):
            NoteCreate(title="   ", content="body")


if __name__ == "__main__":
    unittest.main()
