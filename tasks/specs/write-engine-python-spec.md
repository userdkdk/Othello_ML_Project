# Python 엔진 명세 작성 작업 지시서

## 목적
`src/engine`에 구현할 Python 오셀로 엔진의 타입, 모듈, 공개 API를 명세한다.

## 선행 입력
- `docs/engine/othello-rules.md`
- `docs/engine/othello-module-spec.md`
- `docs/engine/othello-acceptance-tests.md`
- `agents/governance-agent.md`

## 필수 작업
- 엔진 모듈 구조 정의
- 핵심 타입 정의
- 공개 API 함수 또는 클래스 명세
- 상태 불변과 실패 규약 명세
- 테스트와 연결되는 API 사용 예시 작성

## 출력 파일
- `specs/engine/python-engine-spec.md`

## 완료 조건
- `src/engine`의 파일 구조와 책임이 명확하다.
- `Board`, `CellState`, `Player`, `Position`, `GameStatus`, `MoveErrorCode`, `GameState`, `MoveResult` 같은 핵심 타입이 정의되어 있다.
- `GameState`에는 최소한 `board`, `current_player`, `status`와 함께 필요한 부가 상태인 `move_history`, `last_move` 반영 여부가 명확히 적혀 있다.
- 유효 수 계산, 수 적용, 패스, 종료 판정 API 계약이 문서화되어 있다.
- 실패 시 상태 불변 규약이 구현 가능한 수준으로 적혀 있다.
