"""Keyword-driven fake scenario engine.

The engine always creates one root Orchestrator. Agent/tool branches are added
only when the prompt implies work that needs delegation.
"""

from __future__ import annotations

import random
from typing import List, Optional, Sequence

from app.config import AppConfig, load_config
from app.events import SimulationEvent


class ScenarioEngine:
    """Build fake orchestration scenarios from a user prompt."""

    _SEARCH_KEYWORDS = {"검색", "찾아", "search", "web", "url"}
    _CODE_KEYWORDS = {"코드", "파일", "문서", "작업", "버그", "fix", "수정", "에러"}
    _COMPACT_KEYWORDS = {"압축", "토큰", "compact"}

    @classmethod
    def generate(
        cls,
        prompt: str,
        config: Optional[AppConfig] = None,
    ) -> List[SimulationEvent]:
        config = config or load_config()
        try:
            return cls._build_scenario(prompt, config)
        except Exception:
            return cls._direct_response(config)

    @classmethod
    def _build_scenario(cls, prompt: str, config: AppConfig) -> List[SimulationEvent]:
        if not prompt or not prompt.strip():
            return cls._direct_response(config)

        lower = prompt.lower().strip()
        need_compact = any(keyword in lower for keyword in cls._COMPACT_KEYWORDS) or len(prompt) >= 50

        if not config.orchestration_enabled:
            return cls._direct_response(config, need_compact)
        if any(keyword in lower for keyword in cls._CODE_KEYWORDS):
            return cls._case_code(need_compact, config)
        if any(keyword in lower for keyword in cls._SEARCH_KEYWORDS):
            return cls._case_search(need_compact, config)
        return cls._direct_response(config, need_compact)

    @classmethod
    def _root(cls, config: AppConfig) -> SimulationEvent:
        return SimulationEvent(
            step=0,
            tool_id=config.root_tool_id,
            label=config.root_label,
            delay_ms=500,
            parent_step=None,
            node_key="root_orchestrator",
        )

    @classmethod
    def _case_search(cls, need_compact: bool, config: AppConfig) -> List[SimulationEvent]:
        events = [cls._root(config)]
        context = 0
        events.append(cls._branch(1, config.search_agent_id, "검색 계획을 수립하고 웹 정보 수집을 위임받았습니다.", 0, "search_agent"))
        events.append(cls._branch(2, config.memory_agent_id, "관련 대화 맥락과 기억을 병렬로 조회합니다.", 0, "memory_agent"))
        context = cls._append_tool(events, 3, "web_search", "키워드 검색 결과를 수집합니다.", 1, context, 30, 45)
        context = cls._append_tool(events, 4, "fetch_url", "선별된 문서 내용을 읽고 요약합니다.", 3, context, 25, 35)
        context = cls._append_tool(events, 5, "mcp_memory", "이전 맥락과 검색 결과를 병합합니다.", 2, context, 20, 30)
        return cls._finish(events, 6, 0, (4, 5), context, "최종 검색 분석 보고서를 생성합니다.", need_compact)

    @classmethod
    def _case_code(cls, need_compact: bool, config: AppConfig) -> List[SimulationEvent]:
        events = [cls._root(config)]
        context = 0
        events.append(cls._branch(1, config.search_agent_id, "코드베이스 구조 탐색과 수정 후보 검색을 위임받았습니다.", 0, "search_agent"))
        events.append(cls._branch(2, config.memory_agent_id, "요구사항과 이전 실행 맥락을 정리합니다.", 0, "memory_agent"))
        events.append(cls._branch(3, "security_monitor", "수정 전 위험 요소와 금지된 의존성을 점검합니다.", 0, "security_monitor"))
        context = cls._append_tool(events, 4, "mcp_filesystem", "프로젝트 파일 구조를 조회합니다.", 1, context, 20, 30)
        context = cls._append_tool(events, 5, "grep_search", "관련 코드 패턴을 검색합니다.", 4, context, 25, 35)
        context = cls._append_tool(events, 6, "str_replace", "수정 패치를 적용하고 충돌을 확인합니다.", 5, context, 25, 35)
        context = cls._append_tool(events, 7, "mcp_memory", "요구사항 맥락을 재확인합니다.", 2, context, 15, 25)
        return cls._finish(events, 8, 0, (3, 6, 7), context, "최종 수정 결과와 검증 내용을 정리합니다.", need_compact)

    @classmethod
    def _direct_response(
        cls,
        config: AppConfig,
        need_compact: bool = False,
    ) -> List[SimulationEvent]:
        events = [cls._root(config)]
        return cls._finish(events, 1, 0, (0,), 100, "도구 사용 없이 바로 응답을 작성합니다.", need_compact)

    @classmethod
    def _branch(cls, step: int, tool_id: str, label: str, parent_step: int, node_key: str) -> SimulationEvent:
        return SimulationEvent(
            step=step,
            tool_id=tool_id,
            label=label,
            delay_ms=700,
            parent_step=parent_step,
            is_parallel=True,
            node_key=node_key,
        )

    @classmethod
    def _append_tool(
        cls,
        events: List[SimulationEvent],
        step: int,
        tool_id: str,
        label: str,
        parent_step: int,
        context: int,
        min_gain: int,
        max_gain: int,
    ) -> int:
        gain = random.randint(min_gain, max_gain)
        new_context = min(100, context + gain)
        events.append(SimulationEvent(
            step=step,
            tool_id=tool_id,
            label=label,
            delay_ms=random.randint(850, 1200),
            parent_step=parent_step,
            context_percent=new_context,
            context_gained=new_context - context,
            node_key=f"{tool_id}_{step}",
        ))
        return new_context

    @classmethod
    def _finish(
        cls,
        events: List[SimulationEvent],
        step: int,
        parent_step: int,
        merge_parent_steps: Sequence[int],
        context: int,
        label: str,
        need_compact: bool,
    ) -> List[SimulationEvent]:
        if need_compact:
            events.append(SimulationEvent(
                step=step,
                tool_id="context_compact",
                label="컨텍스트 압축을 수행합니다.",
                delay_ms=800,
                parent_step=parent_step,
                is_compact_trigger=True,
                context_percent=context,
                node_key="context_compact",
            ))
            parent_step = step
            merge_parent_steps = (step,)
            step += 1

        events.append(SimulationEvent(
            step=step,
            tool_id="final_response",
            label=label,
            delay_ms=900,
            parent_step=parent_step,
            context_percent=100,
            context_gained=max(0, 100 - context),
            node_key="final_response",
            merge_parent_steps=tuple(merge_parent_steps),
        ))
        return events
