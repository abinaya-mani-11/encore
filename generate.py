"""Turn study material into flashcards.

OWNER: teammate A. Replace the body with an LLM call (Amazon Bedrock via boto3
for the AWS Builder mini challenge). Keep the signature and return shape.
"""


def make_cards(text: str) -> list[dict]:
    """Return [{"question": str, "answer": str}, ...]."""
    # ponytail: placeholder parses "question? answer" lines so the pipeline runs
    # end to end; teammate A swaps in the Bedrock generator.
    cards = []
    for line in text.splitlines():
        if "?" in line:
            q, _, a = line.partition("?")
            if a.strip():
                cards.append({"question": q.strip() + "?", "answer": a.strip()})
    return cards
