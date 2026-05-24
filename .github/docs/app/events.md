# Core Specification: `app/events.py`

## Role
`SimulationEvent` is an immutable dataclass describing one visual action in the
tree.

## Fields
- `step`: unique sequence id for event playback
- `tool_id`: id registered in `ToolRegistry`
- `label`: action text for the node
- `delay_ms`: delay before rendering
- `parent_step`: parent event step for ordinary tree connection
- `is_parallel`: hint for branch-style placement
- `is_compact_trigger`: toggles the compacting state effect
- `context_percent`: accumulated context score
- `context_gained`: context gained by this event
- `node_key`: optional logical object key for node reuse
- `merge_parent_steps`: branch leaves that converge into this event

When `node_key` is omitted, the view may use `step` as the unique object key.
