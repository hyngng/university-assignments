"""Central tool metadata and color registry."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ToolDef:
    tool_id: str
    display_name: str
    category: str
    color_hex: str
    text_color: str = "#000000"


class ToolRegistry:
    """Lookup table for node labels and colors."""

    _TOOLS: List[ToolDef] = [
        ToolDef("orchestrator", "Orchestrator", "agent", "#FFB3BA"),
        ToolDef("search_agent", "Search Agent", "agent", "#B8D8FF"),
        ToolDef("memory_agent", "Memory Agent", "agent", "#D8C4F2"),
        ToolDef("security_monitor", "Security Monitor", "agent", "#FFDFBA"),
        ToolDef("web_search", "Web Search", "legacy", "#FFFFBA"),
        ToolDef("fetch_url", "Fetch URL", "legacy", "#BAFFC9"),
        ToolDef("mcp_filesystem", "MCP: Filesystem", "mcp", "#BAE1FF"),
        ToolDef("mcp_memory", "MCP: Memory", "mcp", "#CBAACB"),
        ToolDef("grep_search", "Grep Search", "skill", "#E2B6CF"),
        ToolDef("str_replace", "Str Replace", "skill", "#A2E1DB"),
        ToolDef("context_compact", "Context Compact", "context", "#CCCCCC"),
        ToolDef("final_response", "Final Response", "terminal", "#FFFFFF"),
    ]

    _INDEX = {tool.tool_id: tool for tool in _TOOLS}

    @classmethod
    def get(cls, tool_id: str) -> ToolDef:
        return cls._INDEX.get(tool_id, cls._INDEX["orchestrator"])

    @classmethod
    def all(cls) -> List[ToolDef]:
        return list(cls._TOOLS)
