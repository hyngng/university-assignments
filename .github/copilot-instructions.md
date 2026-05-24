# GitHub Copilot Instructions — Agent Orchestration Visualizer

이 파일은 GitHub Copilot(및 호환 AI 코드 보조 도구)이 이 저장소에서 코드를 생성할 때
따라야 할 규칙과 맥락을 담고 있다.
코드를 제안하기 전에 반드시 `.github/docs/` 폴더 내의 각 분할된 명세서(main.md, state.md 등)를 먼저 참고해라.

---

## 이 프로젝트가 하는 일

사용자가 입력한 프롬프트 텍스트를 분석해, 에이전트가 도구를 선택·실행하는 과정을
Tkinter Canvas로 실시간 트리 형태로 시각화하는 **로컬 전용 시뮬레이터**이다.
외부 API, 네트워크 요청, 데이터베이스는 일절 없다.

---

## 프로젝트 개발 목표 및 마일스톤 (Phased Goals)

본 프로젝트는 다음과 같은 단계적 개발 목표를 가진다. 코드를 작성할 때 이 마일스톤과 확장성을 반드시 염두에 둬라.

1. **1단계 목표 (현재 최우선 과제)**:
   - 사용자가 프롬프트를 입력하면, 에이전트가 도구를 사용하고 맥락을 수집하는 과정을 순차적으로 화면에 시각화한다.
   - 예: `(입력 받음)` ➔ `(웹 검색 도구 실행)` ➔ `(답변 작성)`
   - 각 작업 노드는 **진행 상태**를 갖습니다. 화면에 처음 등장할 때는 `[실행 중...]` 상태로 활성화되며, 해당 작업 딜레이가 끝나고 다음 작업으로 넘어가기 전에 `[완료]` 상태로 시각적 전환이 일어나야 한다.
   
2. **2단계 목표 (확장 과제)**:
   - 1단계가 성공적으로 완수되면, 본격적이고 복잡한 **'에이전트 오케스트레이션'** 시스템으로 발전시킵니다.
   - 따라서, 현재 작성하는 아키텍처(상태 관리, 트리 뷰, 이벤트 데이터 클래스)는 추후 복잡한 오케스트레이션 로직이 붙더라도 쉽게 호환될 수 있도록 **강력한 확장성과 모듈화**를 유지해야 한다.

---

## 코드 생성 원칙

### 1. 상태는 반드시 `SimulationState.transition()`을 통해 변경
```python
# ✅
state.transition(Phase.EXECUTING)

# ❌ 직접 대입 금지
state.phase = Phase.EXECUTING
```

### 2. 도구 색상·아이콘은 `ToolRegistry`에서만 조회
```python
# ✅
tool = ToolRegistry.get("web_search")
color = tool.color

# ❌ UI 레이어 하드코딩 금지
color = ft.colors.RED_ACCENT_400
```

### 3. 시나리오 생성은 `ScenarioEngine`이 전담
```python
# ✅
events = ScenarioEngine.build(prompt)

# ❌ 외부에서 SimulationEvent 리스트 직접 조립 금지
events = [SimulationEvent(step=0, tool_id="orchestrator", ...)]
```

### 4. 비동기 처리 및 스레드 분리
Tkinter 메인 스레드가 얼지(Freeze) 않도록, 별도 스레드에서 시나리오를 만들고 UI 업데이트는 큐(Queue)와 `root.after()` 타이머 루프를 통해 처리한다.
```python
# ✅
def check_queue():
    if not queue.empty():
        # UI 처리 로직
    root.after(100, check_queue)
```

### 5. 외부 HTTP 요청 금지
어떤 모듈에서도 `requests`, `httpx`, `aiohttp`, `urllib` 등을 import하지 마세요.

---

## 모듈별 역할 요약

| 모듈 | 역할 | 주의 |
|------|------|------|
| `app/state.py` | 상태 보유 + 전이 검증 + 리스너 패턴 | phase 직접 대입 금지 |
| `app/tools.py` | ToolDef 정의 + ToolRegistry | 색상은 여기서만 |
| `app/events.py` | SimulationEvent 데이터클래스 | 순수 데이터, 로직 없음 |
| `app/scenario.py` | 키워드 추출 → 이벤트 리스트 생성 | API 호출 없음 |
| `app/ui/control_panel.py` | 입력 UI + 버튼 상태 제어 | state 구독으로 버튼 활성 제어 |
| `app/ui/tree_view.py` | 이벤트 순차 재생 + 노드 배치 | asyncio.sleep으로 딜레이 |
| `app/ui/node.py` | 노드 단일 컴포넌트 + 등장 애니메이션 | 굵은 외곽선(Outline) 사용 |
| `main.py` | ft.app() 진입점만 | 비즈니스 로직 없음 |

---

## ScenarioEngine 키워드 규칙 (추가 시 참고)

새 키워드나 도구를 추가할 때는 아래 순서로만 작업한다.

1. `tools.py`의 `ToolRegistry`에 `ToolDef` 추가
2. `scenario.py`의 `KEYWORD_TAG_MAP`에 키워드 → 태그 항목 추가
3. `scenario.py`의 `TAG_RULE_MAP`에 태그 → step 생성 규칙 추가
4. UI 코드는 건드리지 않음 — 자동으로 반영됨

---
Tkinter 사용 시 주의사항

- 레이아웃 로직: `ft.Column` 등의 Flex 레이아웃 대신 `tkinter.Canvas`를 크게 띄우고, 최상단부터 Y 좌표를 증가시키며 사각형(노드)과 선(연결선)을 직접 드로잉(Drawing)한다.
- 애니메이션: `.after()` 루프를 사용하여 도형의 좌표나 컬러를 점진적으로 업데이트한다. 
- Flet Material 상수 사용 금지: `ft.colors` 등은 전부 걷어내고, Python 내장 Tkinter 문법과 Hex Color 코드로 규격화한다. 배경 `ft.colors.GREY_900`
- 스크롤 가능 트리: `Scrollbar` 위젯과 캔버스 `yview` 및 `scrollregion`을 연결하여 제어한다.

---

## 제안하지 말아야 할 패턴

- `import anthropic` / `import openai` / 기타 LLM SDK
- `import requests` / `import httpx` / 네트워크 관련 라이브러리
- `threading.Thread` — 비동기는 `asyncio`로만
- `global` 변수로 상태 관리 — 반드시 `SimulationState` 인스턴스 사용
- `time.sleep()` — 반드시 `await asyncio.sleep()` 사용