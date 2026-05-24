# UI 명세: `app/ui/control_panel.py`

## 1. 개요
사용자의 프롬프트 텍스트 입력을 캡처하고 시뮬레이션 제어 상태 머신의 트리거 역할을 수행하는 최상단 제어 바 영역이다.

## 2. 포함 컴포넌트 규격
- `prompt_field` (`tk.Entry` 또는 `tk.Text`): 힌트 텍스트(디폴트 값)를 설정하고, 엔터 키(`<Return>`) 바인딩 시 실행 버튼과 동일한 액션을 보장한다.
- `submit_button` (`tk.Button`): 시뮬레이션을 시작하는 버튼이다.
- `reset_button` (`tk.Button`): '초기화' 라벨을 사용하며 시뮬레이션을 초기 청정 상태로 되돌린다.

## 3. 상태 머신 결합 제어 규칙 (State Binding)
- 이 컴포넌트는 초기화 시 주입받은 `SimulationState` 인스턴스를 구독(`subscribe`)한다.
- **상태별 대응 액션 사양:**
    - `IDLE`: 입력창 활성화, 실행 버튼 활성화, 리셋 버튼 비활성화.
    - `PLANNING` / `EXECUTING` / `COMPACTING`: 입력창 비활성화, 실행 버튼 비활성화, 리셋 버튼 비활성화.
    - `DONE`: 입력창 비활성화, 실행 버튼 비활성화, 리셋 버튼 **활성화**.
- **실행 버튼 클릭 핸들러 내부 로직:**
    1. `state.transition(Phase.PLANNING)` 호출
    2. 메인 스레드 멈춤 방지를 위해 `threading.Thread` 백그라운드 스레드에서 [`ScenarioEngine.generate(prompt)`](../scenario.md)를 호출.
    3. 완료 시, 백그라운드 스레드는 결과를 전역 큐(`queue.Queue`)에 튜플이나 메시지 형태로(예: `("SCENARIO_READY", events)`) 밀어 넣고 즉시 안락하게 종료(Thread-safe)한다. 절대로 백그라운드 스레드에서 UI나 상태 전이(`state.transition`)를 직접 호출하지 않는다.