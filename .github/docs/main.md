# Entry Point Specification: `main.py`

## Role
`main.py` is the Tkinter composition root for the Agent Orchestration Visualizer.
It creates the main window, shared `SimulationState`, thread-safe `queue.Queue`,
`ControlPanel`, and `TreeView`.

## Configuration
Runtime constants must be loaded from root-level `config.yaml` through
`app/config.py`; do not hardcode window title, dimensions, background colors, or
queue pump interval in `main.py`.

Managed keys:
- `window.title`, `window.width`, `window.height`
- `window.min_width`, `window.min_height`
- `window.background`, `window.panel_background`, `window.separator_color`
- `runtime.pump_interval_ms`
- `orchestration.enabled` and root/branch agent ids

The default visual theme should stay in a neutral charcoal/soft-black range
rather than blue-tinted dark colors, so the tree remains a simulator canvas and
not a branded dashboard surface.

## Thread Safety
Background work may generate scenario events, but UI state changes must happen on
the Tk main thread through the queue pump and `root.after(...)`.
