# 강화학습 구성요소 기준

## 목적
이 문서는 오셀로 학습 파이프라인에서 필요한 핵심 구성요소의 책임 범위를 정의한다.

## 구성요소

### `match-runner`
- 두 agent 간 한 판 대국 실행
- 엔진 규칙 준수
- 턴 수, 패스 수, 승패 집계

### `random-agent`
- 유효 수 중 무작위 선택
- 유효 수가 없으면 `PASS`

### `heuristic-agent`
- 코너, 엣지, 뒤집기 수 같은 규칙 기반 점수로 행동 선택

### `state-encoder`
- `GameState`를 학습 입력 표현으로 변환
- 기본 출력은 4-plane 8x8

### `action-mask`
- 전체 액션 공간 65개에 대해 합법 행동 마스크 생성
- 유효 수가 없으면 `PASS`만 허용

### `self-play-runner`
- 여러 판 셀프 플레이 실행
- episode 수집
- 실패 대국 구분

### `episode`
- 한 판 대국 기록
- 상태, 행동, action mask, encoded state, reward, 메타데이터 포함

### `trainer`
- episode 집합을 입력으로 받아 학습 또는 학습 리포트 생성

### `evaluator`
- agent 대 agent 평가
- win rate, draw rate, failure rate 산출

## 공통 원칙
- 엔진 규칙은 `docs/engine/othello-rules.md`를 따른다.
- 데이터 구조는 `specs/training/self-play-data-schema.md`와 충돌하면 안 된다.
- 행동 표현은 `docs/training/predict-api.md` 규약을 따른다.
