# Product feedback and friction log

Fill this in as you go. The submission needs feedback on every tool; friction logs can add up to 10% to the judging score.

## Per-tool feedback
| Tool | Used for | Worked well | Needs work | Onboarding | Build again? |
|---|---|---|---|---|---|
| MCP Python SDK (`mcp` 2.3) | MCP server over Streamable HTTP | Server ran on spec 2025-11-25 with no config | Most tutorials still use v1 `FastMCP`; v2 renamed it `MCPServer` | | |
| Amazon Bedrock (boto3 Converse) | Flashcard generation in `generate.py`; agent loop in `web/app.py` | `converse()` API is clean and consistent across models; streaming variant available | Model ID list not surfaced in the console — had to look up IDs in docs; `nova-lite` not available in all regions | Install `boto3`; set `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID` in `.env` | Yes — Converse API abstracts provider differences well |
| Alexa+ / MCP docs | | | | | |
| MCP Apps | | | | | |

## Friction log
| Date | Task | Steps | Expected | Actual | Severity | Workaround | Suggestion |
|---|---|---|---|---|---|---|---|
| 2026-10-11 | Start an MCP server | `pip install mcp`, then `from mcp.server.fastmcp import FastMCP` | Works as in most tutorials | `ModuleNotFoundError`: v2 renamed FastMCP to MCPServer | Low | `from mcp.server.mcpserver import MCPServer` | Keep a compatibility alias, or update the getting-started examples |
| 2026-10-12 | Find supported Bedrock model IDs | Expect model IDs listed in the Bedrock console | Visible list in console | Had to search docs separately; `amazon.nova-lite-v1:0` not shown in all regions | Medium | Check AWS docs / blog posts for current IDs | Add a "copy model ID" button or a filterable table in the console |
| 2026-10-12 | Parse Bedrock Converse response for text | `response["output"]["message"]["content"][0]["text"]` | Shorter path | Nested structure requires multiple dict accesses; easy to typo | Low | Helper function `_call_bedrock()` wraps the path | Consider a typed SDK response object |

## Feature requests
| Request | Why it matters | Priority |
|---|---|---|
