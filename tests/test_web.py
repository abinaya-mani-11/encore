import sys
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import web.app as web_app


class FakeBedrock:
    def __init__(self):
        self.responses = [
            {
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "toolUse": {
                                    "toolUseId": "call-1",
                                    "name": "add_material",
                                    "input": {"title": "Biology", "text": "ATP is cellular energy."},
                                }
                            }
                        ],
                    }
                },
                "stopReason": "tool_use",
            },
            {
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [{"text": "Added three cards from Biology."}],
                    }
                },
                "stopReason": "end_turn",
            },
        ]
        self.requests = []

    def converse(self, **kwargs):
        self.requests.append(kwargs)
        return self.responses.pop(0)


class FakeClientSession:
    def __init__(self, *_):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def initialize(self):
        return None

    async def list_tools(self):
        return SimpleNamespace(
            tools=[
                SimpleNamespace(
                    name="add_material",
                    description="Create flashcards from study notes.",
                    input_schema={
                        "type": "object",
                        "properties": {"title": {"type": "string"}, "text": {"type": "string"}},
                    },
                )
            ]
        )

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return SimpleNamespace(
            structured_content={"cards_added": 3},
            content=[],
            is_error=False,
        )


class WebAgentTests(IsolatedAsyncioTestCase):
    async def test_agent_lists_calls_mcp_tools_and_returns_bedrock_reply(self):
        bedrock = FakeBedrock()
        session = FakeClientSession()

        @asynccontextmanager
        async def fake_transport(_):
            yield object(), object()

        with (
            patch.object(web_app, "streamable_http_client", fake_transport),
            patch.object(web_app, "ClientSession", return_value=session),
            patch.object(web_app, "BEDROCK_MODEL_ID", "test-model"),
        ):
            messages = [
                {"role": "user", "content": [{"text": "I studied ATP."}]},
            ]
            reply = await web_app.run_agent(
                messages,
                bedrock_client=bedrock,
                mcp_server_url="http://example.test/mcp",
            )

        self.assertEqual(reply, "Added three cards from Biology.")
        self.assertEqual(
            session.calls,
            [("add_material", {"title": "Biology", "text": "ATP is cellular energy."})],
        )
        self.assertEqual(len(bedrock.requests), 2)
        self.assertEqual(
            bedrock.requests[0]["toolConfig"]["tools"][0]["toolSpec"]["name"],
            "add_material",
        )
        self.assertEqual(messages[2]["content"][0]["toolResult"]["toolUseId"], "call-1")


if __name__ == "__main__":
    import unittest

    unittest.main()
