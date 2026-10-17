"""Unit tests for generate.make_cards.

All tests run without a real Bedrock connection: boto3 is fully mocked via
unittest.mock so no AWS credentials are needed (CI-safe).

Covers:
- Happy path: well-formed JSON array from model
- Long input: chunking into multiple Bedrock calls
- Malformed JSON: first attempt bad → retry → success
- Total failure: both attempts raise → regex fallback
- Deduplication of repeated questions across chunks
"""
from __future__ import annotations

import json
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# make sure the repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["LLM_PROVIDER"] = "bedrock"  # these tests mock the Bedrock client; never call a real model

# ── helpers ───────────────────────────────────────────────────────────────────

def _bedrock_response(cards: list[dict]) -> dict:
    """Build a minimal Converse API response dict."""
    return {
        "output": {
            "message": {
                "content": [{"text": json.dumps(cards)}]
            }
        }
    }


def _make_client(side_effects):
    """Return a mock boto3 client whose converse() yields *side_effects* in order."""
    client = MagicMock()
    client.converse.side_effect = side_effects
    return client


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMakeCards(unittest.TestCase):

    def _patch_client(self, mock_client):
        """Patch generate._bedrock() to return *mock_client* and reset singleton."""
        import generate
        generate._client = None  # reset cached singleton
        return patch("generate._bedrock", return_value=mock_client)

    # ------------------------------------------------------------------
    def test_happy_path(self):
        """Single call, valid JSON → cards returned as-is."""
        import generate

        expected = [
            {"question": "What is ATP?", "answer": "The energy currency of the cell."},
            {"question": "What is DNA?", "answer": "The molecule that carries genetic information."},
        ]
        mock_client = _make_client([_bedrock_response(expected)])

        with self._patch_client(mock_client):
            cards = generate.make_cards("What is ATP? energy\nWhat is DNA? code")

        self.assertEqual(cards, expected)
        self.assertEqual(mock_client.converse.call_count, 1)

    # ------------------------------------------------------------------
    def test_strips_markdown_fences(self):
        """Model wraps JSON in ```json ... ``` — should still parse."""
        import generate

        raw_text = "```json\n[{\"question\":\"Q?\",\"answer\":\"A\"}]\n```"
        mock_client = MagicMock()
        mock_client.converse.return_value = {
            "output": {"message": {"content": [{"text": raw_text}]}}
        }

        with self._patch_client(mock_client):
            cards = generate.make_cards("some notes")

        self.assertEqual(cards, [{"question": "Q?", "answer": "A"}])

    # ------------------------------------------------------------------
    def test_chunking_splits_long_input(self):
        """Text longer than CHUNK_CHARS triggers multiple Bedrock calls."""
        import generate

        chunk_cards_1 = [{"question": "Q1?", "answer": "A1"}]
        chunk_cards_2 = [{"question": "Q2?", "answer": "A2"}]
        mock_client = _make_client([
            _bedrock_response(chunk_cards_1),
            _bedrock_response(chunk_cards_2),
        ])

        # build a text that is definitely longer than CHUNK_CHARS
        para1 = "Para one. " * (generate.CHUNK_CHARS // 8)
        para2 = "Para two. " * (generate.CHUNK_CHARS // 8)
        long_text = para1 + "\n\n" + para2

        with self._patch_client(mock_client):
            cards = generate.make_cards(long_text)

        self.assertGreaterEqual(mock_client.converse.call_count, 2)
        self.assertIn({"question": "Q1?", "answer": "A1"}, cards)
        self.assertIn({"question": "Q2?", "answer": "A2"}, cards)

    # ------------------------------------------------------------------
    def test_malformed_json_retries_once(self):
        """First response is bad JSON → retry → second response succeeds."""
        import generate

        good = [{"question": "What is H2O?", "answer": "Water."}]

        bad_response = {
            "output": {"message": {"content": [{"text": "not valid json!!!"}]}}
        }
        good_response = _bedrock_response(good)

        mock_client = _make_client([bad_response, good_response])

        with self._patch_client(mock_client):
            cards = generate.make_cards("Some notes about water.")

        self.assertEqual(cards, good)
        self.assertEqual(mock_client.converse.call_count, 2)

    # ------------------------------------------------------------------
    def test_total_failure_falls_back_to_regex(self):
        """Both attempts raise an exception → regex fallback returns cards."""
        import generate

        mock_client = MagicMock()
        mock_client.converse.side_effect = RuntimeError("network error")

        with self._patch_client(mock_client):
            cards = generate.make_cards("What is ATP? Energy currency\nWhat is DNA? Genetic code")

        # regex fallback should extract at least one card
        self.assertGreater(len(cards), 0)
        questions = [c["question"] for c in cards]
        self.assertIn("What is ATP?", questions)

    # ------------------------------------------------------------------
    def test_deduplication(self):
        """Identical questions from different chunks appear only once."""
        import generate

        dupe_cards = [{"question": "What is ATP?", "answer": "Energy."}]
        mock_client = _make_client([
            _bedrock_response(dupe_cards),
            _bedrock_response(dupe_cards),  # same card from second chunk
        ])

        para1 = "chunk one. " * (generate.CHUNK_CHARS // 9)
        para2 = "chunk two. " * (generate.CHUNK_CHARS // 9)
        long_text = para1 + "\n\n" + para2

        with self._patch_client(mock_client):
            cards = generate.make_cards(long_text)

        atp_cards = [c for c in cards if c["question"] == "What is ATP?"]
        self.assertEqual(len(atp_cards), 1)

    # ------------------------------------------------------------------
    def test_empty_items_filtered(self):
        """Cards with empty question or answer are dropped."""
        import generate

        raw = [
            {"question": "", "answer": "A"},
            {"question": "Q?", "answer": ""},
            {"question": "Good?", "answer": "Yes"},
        ]
        mock_client = _make_client([_bedrock_response(raw)])

        with self._patch_client(mock_client):
            cards = generate.make_cards("some notes")

        self.assertEqual(cards, [{"question": "Good?", "answer": "Yes"}])


if __name__ == "__main__":
    unittest.main()
