"""State machine for the simulation lifecycle."""

from enum import Enum, auto
from typing import Callable, List

from app.events import SimulationEvent


class Phase(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    COMPACTING = auto()
    DONE = auto()


_VALID_TRANSITIONS = {
    Phase.IDLE: {Phase.PLANNING},
    Phase.PLANNING: {Phase.EXECUTING},
    Phase.EXECUTING: {Phase.COMPACTING, Phase.DONE},
    Phase.COMPACTING: {Phase.EXECUTING},
    Phase.DONE: {Phase.IDLE},
}


class SimulationState:
    """Encapsulated state transitions and event storage."""

    def __init__(self) -> None:
        self._phase: Phase = Phase.IDLE
        self._listeners: List[Callable[[Phase], None]] = []
        self._events: List[SimulationEvent] = []

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def events(self) -> List[SimulationEvent]:
        return list(self._events)

    def subscribe(self, fn: Callable[[Phase], None]) -> None:
        if fn not in self._listeners:
            self._listeners.append(fn)

    def transition(self, next_phase: Phase) -> None:
        allowed = _VALID_TRANSITIONS.get(self._phase, set())
        if next_phase not in allowed:
            raise ValueError(f"Invalid transition: {self._phase.name} -> {next_phase.name}")
        self._phase = next_phase
        self._notify()

    def append_event(self, event: SimulationEvent) -> None:
        if self._phase in (Phase.EXECUTING, Phase.COMPACTING):
            self._events.append(event)

    def set_events(self, events: List[SimulationEvent]) -> None:
        self._events = list(events)

    def reset(self) -> None:
        self._phase = Phase.IDLE
        self._events.clear()
        self._notify()

    def _notify(self) -> None:
        for fn in self._listeners:
            try:
                fn(self._phase)
            except Exception:
                pass
