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
- 메모리상으로는 상태, 행동, valid moves, action mask, encoded state, reward, 메타데이터를 포함할 수 있다
- 기본 직렬화 출력은 `specs/training/self-play-data-schema.md`를 따른다

### `trainer`
- episode 집합을 입력으로 받아 `TrainingReport` 생성
- 현재 범위에서는 모델 파라미터 업데이트를 수행하지 않는다

### `evaluator`
- agent 대 agent 평가
- win rate, draw rate, failure rate 산출

## 저장 경계 원칙
- 메모리상 `TurnRecord`와 기본 저장 스키마를 같은 것으로 가정하면 안 된다.
- `encoded_state`는 현재 메모리상 필드이지만 기본 직렬화 출력에는 포함되지 않는다.
- 저장 산출물은 `specs/training/self-play-data-schema.md`를 우선 기준으로 해석한다.

## 공통 원칙
- 엔진 규칙은 `docs/engine/othello-rules.md`를 따른다.
- 데이터 구조는 `specs/training/self-play-data-schema.md`와 충돌하면 안 된다.
- 행동 표현은 `docs/training/predict-api.md` 규약을 따른다.
