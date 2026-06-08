import unittest
from unittest.mock import Mock

from mcp_notes_server.models import DeleteResult, ListResult, Note, SearchResult
from mcp_notes_server.server import create_app


class ServerRegistrationTests(unittest.TestCase):
    def test_create_app_registers_expected_tools(self):
        app = create_app(lambda: Mock(), mcp_factory=FakeMCP)

        registered = set(app.tools)

        self.assertTrue(
            {
                "create_note",
                "get_note",
                "update_note",
                "delete_note",
                "list_notes",
                "search_notes",
            }.issubset(registered)
        )

    def test_tool_function_uses_service_factory(self):
        service = Mock()
        service.create_note.return_value = _note()
        app = create_app(lambda: service, mcp_factory=FakeMCP)
        tool = app.tools["create_note"]

        result = tool("Title", "Body", ["tag"])

        self.assertEqual(result["id"], 1)
        service.create_note.assert_called_once_with("Title", "Body", ["tag"])

    def test_response_models_are_json_serializable(self):
        note = _note()

        self.assertEqual(DeleteResult(deleted=True, note_id=1).model_dump(mode="json"), {"deleted": True, "note_id": 1})
        self.assertEqual(ListResult(items=[note], limit=1, offset=0).model_dump(mode="json")["items"][0]["id"], 1)
        self.assertEqual(SearchResult(items=[note], query="tag", limit=1).model_dump(mode="json")["query"], "tag")


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


class FakeMCP:
    def __init__(self, name):
        self.name = name
        self.tools = {}

    def tool(self):
        def register(fn):
            self.tools[fn.__name__] = fn
            return fn

        return register

    def run(self):
        return None


if __name__ == "__main__":
    unittest.main()
