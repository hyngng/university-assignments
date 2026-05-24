"""Agent Orchestration Visualizer entry point."""

import queue
import tkinter as tk

from app.config import load_config
from app.state import Phase, SimulationState
from app.ui.control_panel import ControlPanel
from app.ui.tree_view import TreeView


def main() -> None:
    """Start the Tkinter application."""
    config = load_config()

    root = tk.Tk()
    root.title(config.window_title)
    root.geometry(f"{config.window_width}x{config.window_height}")
    root.minsize(config.min_width, config.min_height)
    root.configure(bg=config.background)

    try:
        import ctypes

        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            20,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        pass

    state = SimulationState()
    msg_queue: queue.Queue = queue.Queue()

    control_panel = ControlPanel(root, state, msg_queue, config=config)
    control_panel.pack(fill="x", side="top")

    separator = tk.Frame(root, height=1, bg=config.separator_color)
    separator.pack(fill="x")

    tree_view = TreeView(
        root,
        state,
        root,
        on_event_rendered=control_panel.update_context_bar,
        config=config,
    )
    tree_view.pack(fill="both", expand=True, side="top")

    def pump_queue() -> None:
        try:
            while not msg_queue.empty():
                msg = msg_queue.get_nowait()
                if isinstance(msg, tuple) and len(msg) >= 2:
                    msg_type, payload = msg[0], msg[1]
                    if msg_type == "SCENARIO_READY":
                        state.set_events(payload)
                        if state.phase == Phase.PLANNING:
                            state.transition(Phase.EXECUTING)
        except Exception:
            pass

        root.after(config.pump_interval_ms, pump_queue)

    root.after(config.pump_interval_ms, pump_queue)
    root.mainloop()


if __name__ == "__main__":
    main()
