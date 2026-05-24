"""Configuration loader for the local simulator.

This project intentionally avoids external dependencies, so the loader supports
only the small YAML subset used by ``config.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class AppConfig:
    window_title: str
    window_width: int
    window_height: int
    min_width: int
    min_height: int
    background: str
    panel_background: str
    separator_color: str
    pump_interval_ms: int
    orchestration_enabled: bool
    root_tool_id: str
    root_label: str
    search_agent_id: str
    memory_agent_id: str


DEFAULT_CONFIG = AppConfig(
    window_title="에이전트 동작 시각화 프로그램",
    window_width=900,
    window_height=750,
    min_width=800,
    min_height=700,
    background="#181818",
    panel_background="#2B2B2B",
    separator_color="#3A3A3A",
    pump_interval_ms=100,
    orchestration_enabled=True,
    root_tool_id="orchestrator",
    root_label="사용자 의도를 분석하고 서브 에이전트에게 작업을 위임합니다.",
    search_agent_id="search_agent",
    memory_agent_id="memory_agent",
)


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0] in {'"', "'"} and value[-1:] == value[0]:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _load_yaml_subset(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    stack: list[tuple[int, Dict[str, Any]]] = [(-1, data)]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        current = stack[-1][1]
        if value == "":
            section: Dict[str, Any] = {}
            current[key] = section
            stack.append((indent, section))
        else:
            current[key] = _parse_scalar(value)

    return data


def _section_value(data: Dict[str, Any], section: str, key: str, fallback: Any) -> Any:
    section_data = data.get(section, {})
    if isinstance(section_data, dict):
        return section_data.get(key, fallback)
    return fallback


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULT_CONFIG

    data = _load_yaml_subset(config_path)
    branch_agents = _section_value(data, "orchestration", "branch_agents", {})
    if not isinstance(branch_agents, dict):
        branch_agents = {}

    return AppConfig(
        window_title=str(_section_value(data, "window", "title", DEFAULT_CONFIG.window_title)),
        window_width=int(_section_value(data, "window", "width", DEFAULT_CONFIG.window_width)),
        window_height=int(_section_value(data, "window", "height", DEFAULT_CONFIG.window_height)),
        min_width=int(_section_value(data, "window", "min_width", DEFAULT_CONFIG.min_width)),
        min_height=int(_section_value(data, "window", "min_height", DEFAULT_CONFIG.min_height)),
        background=str(_section_value(data, "window", "background", DEFAULT_CONFIG.background)),
        panel_background=str(_section_value(data, "window", "panel_background", DEFAULT_CONFIG.panel_background)),
        separator_color=str(_section_value(data, "window", "separator_color", DEFAULT_CONFIG.separator_color)),
        pump_interval_ms=int(_section_value(data, "runtime", "pump_interval_ms", DEFAULT_CONFIG.pump_interval_ms)),
        orchestration_enabled=bool(_section_value(data, "orchestration", "enabled", DEFAULT_CONFIG.orchestration_enabled)),
        root_tool_id=str(_section_value(data, "orchestration", "root_tool_id", DEFAULT_CONFIG.root_tool_id)),
        root_label=str(_section_value(data, "orchestration", "root_label", DEFAULT_CONFIG.root_label)),
        search_agent_id=str(branch_agents.get("search", DEFAULT_CONFIG.search_agent_id)),
        memory_agent_id=str(branch_agents.get("memory", DEFAULT_CONFIG.memory_agent_id)),
    )
