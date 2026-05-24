"""Tkinter Canvas tree renderer and animation engine."""

from __future__ import annotations

import time
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from app.config import AppConfig, DEFAULT_CONFIG
from app.events import SimulationEvent
from app.state import Phase, SimulationState
from app.ui.node import NodeWidget


def ease_out_bounce(t: float) -> float:
    if t < 1 / 2.75:
        return 7.5625 * t * t
    if t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    if t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    t -= 2.625 / 2.75
    return 7.5625 * t * t + 0.984375


def ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3


@dataclass
class ScaleAnimation:
    node: NodeWidget
    start_time: float
    duration: float = 0.4
    done: bool = False


@dataclass
class LineAnimation:
    line_id: int
    x1: float
    y1: float
    x2: float
    y2: float
    start_time: float
    duration: float = 0.3
    done: bool = False


class AnimationManager:
    """Single 60fps animation loop."""

    TICK_MS = 16

    def __init__(self, canvas: tk.Canvas, root: tk.Tk) -> None:
        self.canvas = canvas
        self.root = root
        self._scale_anims: List[ScaleAnimation] = []
        self._line_anims: List[LineAnimation] = []
        self._running = False

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._tick()

    def stop(self) -> None:
        self._running = False

    def clear(self) -> None:
        self._scale_anims.clear()
        self._line_anims.clear()

    def add_scale(self, node: NodeWidget) -> None:
        self._scale_anims.append(ScaleAnimation(node=node, start_time=time.perf_counter()))

    def add_line(self, x1: float, y1: float, x2: float, y2: float) -> int:
        line_id = self.canvas.create_line(x1, y1, x1, y1, fill="#777777", width=2, smooth=True)
        self._line_anims.append(LineAnimation(line_id, x1, y1, x2, y2, time.perf_counter()))
        return line_id

    def _tick(self) -> None:
        if not self._running:
            return

        now = time.perf_counter()
        for anim in self._scale_anims:
            if anim.done:
                continue
            t = min((now - anim.start_time) / anim.duration, 1.0)
            anim.node.update_scale(ease_out_bounce(t))
            if t >= 1.0:
                anim.node.update_scale(1.0)
                anim.done = True

        for anim in self._line_anims:
            if anim.done:
                continue
            t = min((now - anim.start_time) / anim.duration, 1.0)
            progress = ease_out_cubic(t)
            cx = anim.x1 + (anim.x2 - anim.x1) * progress
            cy = anim.y1 + (anim.y2 - anim.y1) * progress
            self.canvas.coords(anim.line_id, anim.x1, anim.y1, cx, cy)
            if t >= 1.0:
                self.canvas.coords(anim.line_id, anim.x1, anim.y1, anim.x2, anim.y2)
                anim.done = True

        self._scale_anims = [anim for anim in self._scale_anims if not anim.done]
        self._line_anims = [anim for anim in self._line_anims if not anim.done]
        self.root.after(self.TICK_MS, self._tick)


class TreeView(tk.Frame):
    """Render simulation events as a branching tree."""

    NODE_WIDTH = 220
    NODE_HEIGHT = 48
    Y_PADDING = 92
    X_OFFSET = 250
    CANVAS_PADDING_TOP = 58

    def __init__(
        self,
        parent: tk.Widget,
        state: SimulationState,
        root: tk.Tk,
        on_event_rendered: Optional[Callable[[int, int], None]] = None,
        config: AppConfig = DEFAULT_CONFIG,
    ) -> None:
        super().__init__(parent, bg=config.background)
        self._state = state
        self._root = root
        self._on_event_rendered = on_event_rendered
        self._config = config

        self._current_x = 450.0
        self._event_index = 0
        self._step_positions: Dict[int, Tuple[float, float]] = {}
        self._node_positions: Dict[str, Tuple[float, float]] = {}
        self._nodes: Dict[str, NodeWidget] = {}
        self._step_to_key: Dict[int, str] = {}
        self._children_by_parent: Dict[Optional[int], List[int]] = {}

        self._build_ui()
        self._anim = AnimationManager(self._canvas, self._root)
        self._state.subscribe(self._on_state_change)

    def _build_ui(self) -> None:
        self._scrollbar = tk.Scrollbar(self, orient="vertical", bg="#2D2D2D")
        self._scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(
            self,
            bg=self._config.background,
            highlightthickness=0,
            yscrollcommand=self._scrollbar.set,
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.config(command=self._canvas.yview)
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda event: self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
        )

    def _on_state_change(self, phase: Phase) -> None:
        if phase == Phase.IDLE:
            self._clear_canvas()
        elif phase == Phase.EXECUTING:
            self._start_playback()

    def _clear_canvas(self) -> None:
        self._anim.stop()
        self._anim.clear()
        self._canvas.delete("all")
        self._event_index = 0
        self._step_positions.clear()
        self._node_positions.clear()
        self._nodes.clear()
        self._step_to_key.clear()
        self._children_by_parent.clear()

    def _start_playback(self) -> None:
        canvas_width = self._canvas.winfo_width()
        self._current_x = canvas_width / 2 if canvas_width > 1 else self._config.window_width / 2
        self._event_index = 0
        self._build_child_index()
        self._anim.start()
        self._play_next()

    def _build_child_index(self) -> None:
        self._children_by_parent.clear()
        for event in self._state.events:
            self._children_by_parent.setdefault(event.parent_step, []).append(event.step)

    def _play_next(self) -> None:
        events = self._state.events
        if self._event_index >= len(events):
            self._finalize()
            return
        event = events[self._event_index]
        self._root.after(event.delay_ms, lambda e=event: self._render_event(e))

    def _render_event(self, event: SimulationEvent) -> None:
        if event.is_compact_trigger:
            if self._state.phase == Phase.EXECUTING:
                self._state.transition(Phase.COMPACTING)
            for node in self._nodes.values():
                node.dim()

        key = self._node_key(event)
        x, y = self._calculate_position(event, key)
        self._step_positions[event.step] = (x, y)
        self._step_to_key[event.step] = key

        if key in self._nodes:
            node = self._nodes[key]
            node.set_active()
            self._anim.add_scale(node)
        else:
            parent_steps = event.merge_parent_steps or (
                (event.parent_step,) if event.parent_step is not None else ()
            )
            for parent_step in parent_steps:
                if parent_step in self._step_positions:
                    px, py = self._step_positions[parent_step]
                    self._anim.add_line(px, py + self.NODE_HEIGHT // 2, x, y - self.NODE_HEIGHT // 2)

            node = NodeWidget(
                self._canvas,
                x,
                y,
                tool_id=event.tool_id,
                label=event.label,
                width=self.NODE_WIDTH,
                height=self.NODE_HEIGHT,
            )
            node.draw(scale=0.0)
            self._nodes[key] = node
            self._node_positions[key] = (x, y)
            self._anim.add_scale(node)

        self._update_scroll_region()
        self._complete_previous_event(event.step)

        if event.is_compact_trigger and self._state.phase == Phase.COMPACTING:
            self._state.transition(Phase.EXECUTING)

        self._event_index += 1
        if self._event_index >= len(self._state.events):
            self._root.after(800, self._finalize)
        else:
            self._play_next()

    def _node_key(self, event: SimulationEvent) -> str:
        return event.node_key or f"step:{event.step}"

    def _complete_previous_event(self, current_step: int) -> None:
        previous_step = current_step - 1
        previous_key = self._step_to_key.get(previous_step)
        if previous_key and previous_key in self._nodes:
            self._nodes[previous_key].set_completed()
            if self._on_event_rendered:
                previous_event = self._state.events[previous_step]
                self._on_event_rendered(previous_event.context_percent, previous_event.context_gained)

    def _finalize(self) -> None:
        events = self._state.events
        if events:
            last_event = events[-1]
            last_key = self._step_to_key.get(last_event.step, self._node_key(last_event))
            if last_key in self._nodes:
                self._nodes[last_key].set_completed()
                if self._on_event_rendered:
                    self._on_event_rendered(last_event.context_percent, last_event.context_gained)

        self._anim.stop()
        if self._state.phase in (Phase.EXECUTING, Phase.COMPACTING):
            self._state.transition(Phase.DONE)

    def _calculate_position(self, event: SimulationEvent, key: str) -> Tuple[float, float]:
        if key in self._node_positions:
            return self._node_positions[key]

        if event.merge_parent_steps:
            # Merge nodes represent branch convergence, so they are centered
            # under the completed branch leaves instead of treated as siblings.
            positions = [
                self._step_positions[step]
                for step in event.merge_parent_steps
                if step in self._step_positions
            ]
            if positions:
                x = sum(position[0] for position in positions) / len(positions)
                y = max(position[1] for position in positions) + self.Y_PADDING
                return x, y

        if event.parent_step is None or event.parent_step not in self._step_positions:
            return self._current_x, self.CANVAS_PADDING_TOP

        px, py = self._step_positions[event.parent_step]
        siblings = self._children_by_parent.get(event.parent_step, [event.step])
        count = len(siblings)
        index = siblings.index(event.step) if event.step in siblings else count - 1
        offset = (index - (count - 1) / 2) * self.X_OFFSET
        y = py + self.Y_PADDING
        return px + offset, y

    def _update_scroll_region(self) -> None:
        bbox = self._canvas.bbox("all")
        if bbox:
            padded = (bbox[0] - 40, bbox[1] - 30, bbox[2] + 60, bbox[3] + 90)
            self._canvas.configure(scrollregion=padded)
            self._canvas.yview_moveto(1.0)
