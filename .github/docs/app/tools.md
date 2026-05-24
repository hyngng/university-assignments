# Core Specification: `app/tools.py`

## Role
`ToolRegistry` centrally defines visual metadata for every tool, agent, MCP, and
terminal node. UI drawing code must fetch colors through `ToolRegistry.get(...)`
instead of hardcoding tool colors.

## Required Tools
- `orchestrator`: single root coordinator
- `search_agent`: delegated search/retrieval agent
- `memory_agent`: delegated memory/context agent
- `security_monitor`
- `web_search`
- `fetch_url`
- `mcp_filesystem`
- `mcp_memory`
- `grep_search`
- `str_replace`
- `context_compact`
- `final_response`
