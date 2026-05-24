"""Top control panel for prompt input and simulation state."""

import queue
import threading
import tkinter as tk

from app.config import AppConfig, DEFAULT_CONFIG
from app.scenario import ScenarioEngine
from app.state import Phase, SimulationState


class ControlPanel(tk.Frame):
    """Prompt controls, run/reset actions, and context score display."""

    HINT_TEXT = "검색, 코드 수정"

    def __init__(
        self,
        parent: tk.Widget,
        state: SimulationState,
        msg_queue: queue.Queue,
        config: AppConfig = DEFAULT_CONFIG,
    ) -> None:
        super().__init__(parent, bg=config.panel_background, padx=12, pady=10)
        self._state = state
        self._queue = msg_queue
        self._config = config
        self._panel_bg = config.panel_background
        self._current_context_percent = 0

        self._build_ui()
        self._state.subscribe(self._on_state_change)

    def _build_ui(self) -> None:
        title = tk.Label(
            self,
            text=self._config.window_title,
            bg=self._panel_bg,
            fg="#E0E0E0",
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(anchor="w", pady=(0, 8))

        input_frame = tk.Frame(self, bg=self._panel_bg)
        input_frame.pack(fill="x")

        self._prompt_var = tk.StringVar()
        self._prompt_var.trace_add("write", self._on_prompt_change)

        self._prompt_field = tk.Entry(
            input_frame,
            textvariable=self._prompt_var,
            font=("Segoe UI", 11),
            bg="#F7F9FC",
            fg="#111827",
            insertbackground="#111827",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#7B9FFF",
            highlightcolor="#7B9FFF",
        )
        self._prompt_field.pack(side="left", fill="x", expand=True, ipady=6)
        self._prompt_field.bind("<Return>", lambda _event: self._on_submit())

        self._hint_label = tk.Label(
            self._prompt_field,
            text=self.HINT_TEXT,
            fg="#7A8190",
            bg="#F7F9FC",
            font=("Segoe UI", 11),
            cursor="xterm",
        )
        self._hint_label.place(relx=0.0, rely=0.5, anchor="w", x=4)
        self._hint_label.bind("<Button-1>", lambda _event: self._prompt_field.focus_set())

        self._submit_btn = tk.Button(
            input_frame,
            text="▶ 실행",
            font=("Segoe UI", 10, "bold"),
            bg="#4A90D9",
            fg="#FFFFFF",
            activebackground="#3A7BC8",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=16,
            pady=4,
            cursor="hand2",
            command=self._on_submit,
        )
        self._submit_btn.pack(side="left", padx=(8, 4))

        self._reset_btn = tk.Button(
            input_frame,
            text="↻ 초기화",
            font=("Segoe UI", 10),
            bg="#555555",
            fg="#CCCCCC",
            activebackground="#666666",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._on_reset,
            state="disabled",
        )
        self._reset_btn.pack(side="left", padx=(4, 0))

        self._status_label = tk.Label(
            self,
            text="상태: 대기 중 (IDLE)",
            bg=self._panel_bg,
            fg="#888888",
            font=("Segoe UI", 9),
            anchor="w",
        )
        self._status_label.pack(fill="x", pady=(6, 0))

        self._context_frame = tk.Frame(self, bg=self._panel_bg)
        self._context_frame.pack(fill="x", pady=(6, 0))

        self._context_label = tk.Label(
            self._context_frame,
            text="맥락 수집도(Context Score): 0%",
            bg=self._panel_bg,
            fg="#81C784",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self._context_label.pack(side="top", anchor="w", pady=(0, 4))

        self._context_canvas = tk.Canvas(
            self._context_frame,
            height=16,
            bg=self._panel_bg,
            highlightthickness=0,
        )
        self._context_canvas.pack(fill="x", side="top")
        self._context_canvas.bind(
            "<Configure>",
            lambda _event: self.update_context_bar(self._current_context_percent, 0),
        )

    def _on_prompt_change(self, *_args) -> None:
        if self._prompt_var.get():
            self._hint_label.place_forget()
        else:
            self._hint_label.place(relx=0.0, rely=0.5, anchor="w", x=4)

    def _on_submit(self) -> None:
        prompt = self._prompt_var.get().strip()
        if not prompt or self._state.phase != Phase.IDLE:
            return

        self._state.transition(Phase.PLANNING)

        def generate() -> None:
            events = ScenarioEngine.generate(prompt, self._config)
            self._queue.put(("SCENARIO_READY", events))

        threading.Thread(target=generate, daemon=True).start()

    def _on_reset(self) -> None:
        self._prompt_var.set("")
        self._state.reset()
        self.reset_context_bar()

    def _interpolate_color(self, hex1: str, hex2: str, t: float) -> str:
        h1 = hex1.lstrip("#")
        h2 = hex2.lstrip("#")
        r1, g1, b1 = int(h1[0:2], 16), int(h1[2:4], 16), int(h1[4:6], 16)
        r2, g2, b2 = int(h2[0:2], 16), int(h2[2:4], 16), int(h2[4:6], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_context_bar(self, percent: int, gained: int) -> None:
        self._current_context_percent = percent
        suffix = f" (+{gained}%)" if gained > 0 else ""
        self._context_label.config(text=f"맥락 수집도(Context Score): {percent}%{suffix}")

        self._context_canvas.delete("all")
        width = max(self._context_canvas.winfo_width(), 400)
        self._context_canvas.create_rectangle(0, 2, width, 14, fill="#3C3C3C", outline="#555555", width=1)

        fill_width = int(width * (percent / 100.0))
        if fill_width <= 0:
            return

        color = self._interpolate_color("#4FC3F7", "#81C784", percent / 100.0)
        self._context_canvas.create_rectangle(0, 2, fill_width, 14, fill=color, outline="", width=0)
        if gained > 0:
            prev_percent = max(0, percent - gained)
            prev_width = int(width * (prev_percent / 100.0))
            self._context_canvas.create_rectangle(prev_width, 2, fill_width, 14, fill="#FFFFFF", outline="", width=0)

    def reset_context_bar(self) -> None:
        self.update_context_bar(0, 0)

    _STATUS_TEXT = {
        Phase.IDLE: "상태: 대기 중 (IDLE)",
        Phase.PLANNING: "상태: 시나리오 생성 중... (PLANNING)",
        Phase.EXECUTING: "상태: 시뮬레이션 실행 중... (EXECUTING)",
        Phase.COMPACTING: "상태: 컨텍스트 압축 중... (COMPACTING)",
        Phase.DONE: "상태: 완료 (DONE)",
    }

    _STATUS_COLOR = {
        Phase.IDLE: "#888888",
        Phase.PLANNING: "#FFB74D",
        Phase.EXECUTING: "#4FC3F7",
        Phase.COMPACTING: "#CE93D8",
        Phase.DONE: "#81C784",
    }

    def _on_state_change(self, phase: Phase) -> None:
        self._status_label.config(
            text=self._STATUS_TEXT.get(phase, ""),
            fg=self._STATUS_COLOR.get(phase, "#888888"),
        )

        if phase == Phase.IDLE:
            self._prompt_field.config(state="normal")
            self._submit_btn.config(state="normal")
            self._reset_btn.config(state="disabled")
        elif phase in (Phase.PLANNING, Phase.EXECUTING, Phase.COMPACTING):
            self._prompt_field.config(state="disabled")
            self._submit_btn.config(state="disabled")
            self._reset_btn.config(state="disabled")
        elif phase == Phase.DONE:
            self._prompt_field.config(state="disabled")
            self._submit_btn.config(state="disabled")
            self._reset_btn.config(state="normal")
