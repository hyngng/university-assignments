"""Immutable event model for the simulator tree."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class SimulationEvent:
    """One visual action in the orchestration simulation."""

    step: int
    tool_id: str
    label: str
    delay_ms: int
    parent_step: Optional[int]
    is_parallel: bool = False
    is_compact_trigger: bool = False
    context_percent: int = 0
    context_gained: int = 0
    node_key: Optional[str] = None
    merge_parent_steps: Tuple[int, ...] = ()
    """Branch leaf steps that visually converge into this event."""
