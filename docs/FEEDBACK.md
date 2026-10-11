# Product feedback and friction log

Fill this in as you go. The submission needs feedback on every tool; friction logs can add up to 10% to the judging score.

## Per-tool feedback
| Tool | Used for | Worked well | Needs work | Onboarding | Build again? |
|---|---|---|---|---|---|
| MCP Python SDK (`mcp` 2.3) | MCP server over Streamable HTTP | Server ran on spec 2025-11-25 with no config | Most tutorials still use v1 `FastMCP`; v2 renamed it `MCPServer` | | |
| Amazon Bedrock | Card generation, agent | | | | |
| Alexa+ / MCP docs | | | | | |
| MCP Apps | | | | | |

## Friction log
| Date | Task | Steps | Expected | Actual | Severity | Workaround | Suggestion |
|---|---|---|---|---|---|---|---|
| 2026-10-11 | Start an MCP server | `pip install mcp`, then `from mcp.server.fastmcp import FastMCP` | Works as in most tutorials | `ModuleNotFoundError`: v2 renamed FastMCP to MCPServer | Low | `from mcp.server.mcpserver import MCPServer` | Keep a compatibility alias, or update the getting-started examples |

## Feature requests
| Request | Why it matters | Priority |
|---|---|---|
