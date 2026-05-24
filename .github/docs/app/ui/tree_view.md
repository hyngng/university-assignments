# UI Specification: `app/ui/tree_view.py`

## Role
`TreeView` renders `SimulationEvent` objects as a progressive Tkinter Canvas tree
with 60fps animation, scale-up easing, progressive line drawing, and auto-scroll.

## Tree Layout
The canvas is a managed tree, not a vertical event log.

- A single Orchestrator root sits at the top center.
- Children are grouped by `parent_step`.
- Sibling branch agents are distributed left/right under their parent with
  stable X offsets.
- Tool nodes continue beneath the branch agent that owns them.
- Events with `merge_parent_steps` are centered below the listed branch leaves.
  This is used for `final_response`, which is a synthesis node rather than a
  delegated worker.

## Object Management
Rendered node widgets and positions must be kept in dictionaries. If an event has
the same logical `node_key` as an existing node, the view reuses/updates that
node instead of creating another object at the same coordinates.

## State Handling
State transitions still use `SimulationState.transition(...)`; the view must not
assign `state.phase` directly.
