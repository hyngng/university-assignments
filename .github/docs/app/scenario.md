# Core Specification: `app/scenario.py`

## Role
`ScenarioEngine` builds fake simulation events from the user prompt. It must not
call external APIs, network clients, or LLM SDKs.

## Prompt Rules
When multiple categories match, code prompts take priority over search prompts
because they imply a more specific local-workflow scenario.

- Direct prompts: if no tool-oriented keyword is detected, create only
  `orchestrator -> final_response`. Greetings such as `안녕` should not create
  Search Agent, Memory Agent, or tool nodes.
- Search prompts: if the prompt contains `검색`, `찾아`, `search`, `web`, or
  `url`, create Search Agent and Memory Agent branches. Search tools handle
  lookup and fetch work; memory tools collect prior context.
- Code prompts: if the prompt contains `코드`, `파일`, `문서`, `작업`, `버그`,
  `fix`, `수정`, or `에러`, create Search Agent, Memory Agent, and Security
  Monitor branches. Filesystem/search/replace tools sit under the relevant
  branch.
- Compacting: if the prompt contains `압축`, `토큰`, `compact`, or is long
  enough to need context pressure simulation, insert `context_compact` before
  final output.

## Orchestration Model
When `config.yaml` enables orchestration, every scenario starts with exactly one
root Orchestrator node. The engine must not insert another Orchestrator event
after each tool action.

Delegation branches are conditional. The Orchestrator may decide that no
sub-agent or tool is needed, in which case the visualization should flow
directly to `final_response`.

## Merge Nodes
`final_response` is not a parallel worker branch. It represents the final
synthesis after branch work completes. The engine sets `merge_parent_steps` to
the leaf steps that should visually converge into the final node.

## Reuse
Events may provide a logical `node_key`. The view layer uses that key to reuse an
existing node object instead of drawing a duplicate at the same position.
