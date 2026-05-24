# 코어 명세: `app/state.py`

## 1. 개요
시뮬레이션 생명주기를 5개의 고유 상태(Phase)로 분리하고, 부적절한 타이밍에 이벤트가 끼어들거나 전이되는 것을 방어하는 상태 패턴 매니저이다.

## 2. 상태(Phase) 열거형 규격
- `IDLE`: 사용자 입력을 기다리는 기본 대기 상태.
- `PLANNING`: 시나리오 엔진이 키워드를 분석하여 이벤트 큐를 생성 중인 상태.
- `EXECUTING`: 생성된 시나리오 이벤트를 순차적으로 화면에 출력하는 상태.
- `COMPACTING`: 시뮬레이션 도중 컨텍스트 압축 이벤트가 발생하여 화면을 페이드아웃하는 가상 상태.
- `DONE`: 모든 이벤트 재생이 안전하게 끝나고 최종 답변까지 도달한 상태.

## 3. 인터페이스 구현 계약 (Interface Contract)
- `subscribe(self, fn: Callable)`: UI 컴포넌트들이 상태 변화를 관찰할 수 있도록 콜백 리스너를 등록한다.
- `transition(self, next_phase: Phase)`: 전이 경로가 유효한지 검증한 후 내부 상태를 변경하고, 구독된 모든 리스너 함수들을 트리거한다.
- `append_event(self, event: SimulationEvent)`: 현재 페이즈가 `EXECUTING` 또는 `COMPACTING` 일 때만 이벤트 큐에 데이터 삽입을 허용한다.
- `reset(self)`: 현재 상태를 강제로 `IDLE`로 돌리고 내부 이벤트 리스트를 완전히 비웁니다.