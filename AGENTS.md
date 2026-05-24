# 🧠 자율 에이전트 지침서 — `AGENTS.md`

이 문서는 **Antigravity** 및 기타 자율형 AI 에이전트 프레임워크가 본 저장소에서 작업을 수행할 때 반드시 준수해야 하는 **뇌(Brain)**이자 **진입점**입니다. 본 가이드라인은 에이전트의 페르소나, 상세 명세 문서의 지연 로딩 맵, 환경 실행 및 자율 검증 지침, 그리고 코드 작성 제약 조건을 다룹니다.

> [!IMPORTANT]
> VS Code Copilot과의 호환성을 위해 `.github/copilot-instructions.md` 및 `.github/docs/` 폴더 내의 기존 문서들은 **절대로 지우지 말고 그대로 유지**해야 합니다.

---

## 1. 에이전트 페르소나 및 정체성 (Agent Persona)

* **역할**: AI 에이전트 오케스트레이션 시각화 시뮬레이터(Agent Orchestration Visualizer) 구축 에이전트.
* **현 마일스톤 (Phase 1)**: 
  * 사용자의 프롬프트 입력에 따라 에이전트의 도구 실행 과정을 Tkinter Canvas를 통해 점진적으로 시각화하는 로컬 시뮬레이터의 프론트엔드/뷰 엔진 구축.
  * 60fps 애니메이션(이징 함수 기반 Bouncy scale-up, Progressive line drawing)과 스레드 안전한 대기열(Queue) 구조 검증.
  * 외부 API 연동이나 네트워크 호출이 없는 가짜(Fake) 시나리오 엔진 작동 보장.

---

## 2. 사양 문서 지연 로딩 맵 (Lazy Loading Map)

자율 에이전트는 컨텍스트(Context) 창을 효율적으로 관리해야 합니다. 본 저장소의 모든 상세 설계 사양은 모듈별로 쪼개져 있으므로, 작업을 진행하기 전에 아래 매핑 테이블을 참조하여 **필요한 명세서만 `view_file` 도구로 지연 로딩(Lazy loading)** 하십시오.

```xml
<lazy_loading_specs>
  <!-- 메인 진입점 및 이벤트 펌프 루프 설계 -->
  <spec module="main.py" file=".github/docs/main.md" />
  
  <!-- 상태 패턴 관리자 (SimulationState) -->
  <spec module="app/state.py" file=".github/docs/app/state.md" />
  
  <!-- 도구 메타데이터 정의 및 컬러 레지스트리 (ToolRegistry) -->
  <spec module="app/tools.py" file=".github/docs/app/tools.md" />
  
  <!-- 키워드 기반 가상 시나리오 생성 엔진 (ScenarioEngine) -->
  <spec module="app/scenario.py" file=".github/docs/app/scenario.md" />
  
  <!-- 이벤트 불변 데이터 클래스 (SimulationEvent) -->
  <spec module="app/events.py" file=".github/docs/app/events.md" />
  
  <!-- 상단 컨트롤 패널 GUI 컴포넌트 -->
  <spec module="app/ui/control_panel.py" file=".github/docs/app/ui/control_panel.md" />
  
  <!-- Tkinter Canvas 트리 구조 시각화 및 애니메이션 엔진 -->
  <spec module="app/ui/tree_view.py" file=".github/docs/app/ui/tree_view.md" />
  
  <!-- Canvas 노드 그래픽 오브젝트 렌더러 -->
  <spec module="app/ui/node.py" file=".github/docs/app/ui/node.md" />
</lazy_loading_specs>
```

---

## 3. 자율 실행 및 자가 치유(Self-healing) 검증 지침

에이전트는 코드를 변경하거나 새로 작성한 후, 아래 파이프라인을 따라 독립적으로 검증을 시도하고 발생하는 오류를 스스로 수정(Self-healing)해야 합니다.

### A. Headless 구문 및 가져오기(Import) 오류 검사
에이전트 구동 터미널 환경에서는 GUI 표시 장치가 연결되어 있지 않거나, GUI 프로세스가 떠서 터미널이 블로킹될 수 있습니다. 따라서 전체 애플리케이션을 구동하기 전, 아래 명령어로 구문 분석 및 바인딩 오류를 먼저 확인합니다:
```powershell
# 모든 소스 파일에 대해 개별 컴파일 검증 실행
python -m py_compile main.py app/**/*.py
```
> [!TIP]
> 위 명령어를 실행했을 때 아무런 출력이 없고 반환 코드가 0이면 구문 및 정적 Import 상의 문제가 없음을 의미합니다.

### B. GUI 블로킹 방지 및 테스트 코드 검증
* Tkinter 애플리케이션을 직접 실행하는 `python main.py`는 유저 인터랙션이 발생하기 전까지 터미널을 중단(Hang)시킵니다.
* 에이전트의 자체 검증을 위해, 목킹(Mocking) 기반의 단위 테스트가 마련되어 있다면 `unittest` 또는 `pytest`를 통해 비즈니스 로직(예: `SimulationState` 전이 규칙, `ScenarioEngine` 파싱 로직)을 검증하십시오.

---

## 4. 에이전트 개발 수칙 & 금지 사항 (Constraints)

1. **외부 라이브러리 및 SDK 의존성 금지**
   * `import anthropic`, `import openai` 등 어떠한 LLM API 라이브러리도 임포트할 수 없습니다.
   * `import requests`, `import httpx` 등 네트워크/HTTP 관련 라이브러리도 사용할 수 없습니다.
   * 오직 **Tkinter**, **threading**, **queue**, **asyncio** 등 파이썬 기본 내장 모듈만으로 구성합니다.
2. **캡슐화된 상태 전이 규칙 준수**
   * `SimulationState`의 내부 값을 직접 대입해 변경하지 마십시오 (`state.phase = ...` 금지).
   * 상태의 변경은 오직 `state.transition(next_phase)` 메서드를 통해서만 일어나야 하며, 이를 통해 UI 상태 리스너들이 정상 동작하도록 보장해야 합니다.
3. **색상 및 UI 리소스 중앙 통제**
   * 특정 도구 노드의 색상을 UI 그리기 레이어(`tree_view.py`, `node.py`)에 하드코딩하지 마십시오.
   * 모든 도구의 파스텔 톤 헥스(Hex) 컬러는 `ToolRegistry.get(tool_id)`를 통해서만 동적으로 가져옵니다.
4. **스레드 안전성 보장**
   * Tkinter 메인 루프가 얼지 않도록 백그라운드 스레드에서 연산을 처리하되, UI 갱신은 반드시 메인 스레드에 등록된 `queue.Queue` 및 `root.after()` 주기 함수를 거쳐 스레드 간 충돌(Thread-safety 위반)을 방지하십시오.
