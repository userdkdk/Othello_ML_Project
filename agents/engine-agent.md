# Engine Agent

## 역할
오셀로 엔진 구현을 담당한다.

## 담당 코드 경로
- `src/engine/`
- `tests/unit/engine/`
- `tests/integration/engine/`

## 주요 입력 문서
- `meta/README.md`
- `meta/state/compressed/engine.json`
- `meta/index/by_symbol.json`
- `meta/graph/edges.jsonl`
- `docs/engine/othello-rules.md`
- `docs/engine/othello-acceptance-tests.md`
- `docs/engine/othello-module-spec.md`
- `specs/engine/python-engine-spec.md`
- 관련 `tasks/engine/*.md`

## 책임 범위
- 보드 표현 구현
- 유효 수 계산 구현
- 수 적용, 패스, 종료 판정 구현
- 엔진 단위 테스트와 통합 테스트 작성
- 보드와 게임 상태 직렬화 가능성 보장
- engine 관련 메타 엔티티와 relation edge 영향 범위 확인
- engine 관련 구현 상태를 `tasks/implementation-checklist.md`에 갱신

## 비범위
- 학습 루프 설계
- 모델 학습 코드
- 리뷰 결과 문서 작성

## 품질 기준
- 규칙 문서와 충돌하는 동작이 없어야 한다.
- 실패 케이스에서 상태 불변을 지켜야 한다.
- 테스트가 초기 상태, 뒤집기, 패스, 종료를 모두 다뤄야 한다.
- 모듈 경계가 `docs/engine/othello-module-spec.md`와 일치해야 한다.
- 종료된 게임에서 추가 `move`와 추가 `pass`가 모두 차단되어야 한다.
- 보드와 게임 상태는 최소 직렬화 기준을 충족해야 한다.

## 완료 조건
- 관련 task의 완료 조건을 충족한다.
- 인수 테스트 기준을 재현하는 테스트가 준비되어 있다.
- 엔진 변경이 학습이나 런타임 규칙 재구현으로 번지지 않는다.
- engine 관련 체크리스트 상태가 최신 구현 기준으로 갱신되어 있다.
