# 셀프 플레이 데이터 스키마

## 목적
이 문서는 학습용 대국 기록과 상태/행동/보상 데이터를 어떤 구조로 저장할지 정의한다.

## 기본 저장 단위
- 기본 저장 단위는 `episode`다.
- 각 `episode`는 여러 `turn record`를 가진다.
- 저장 포맷 기본값은 `JSON Lines (.jsonl)`이다.
  - 각 줄은 하나의 `episode`
- 대용량 학습 단계에서는 `Parquet` 변환을 허용한다.

## 보상 기준
- 기본 보상 기준은 `BLACK` 기준이다.
- `BLACK 승리 = +1`
- `무승부 = 0`
- `WHITE 승리 = -1`

이 값은 `episode` 메타데이터에 기준과 함께 기록해야 한다.

## 에피소드 스키마

```json
{
  "episode_id": "uuid-or-stable-id",
  "status": "completed",
  "seed": 12345,
  "policy_black_version": "v1",
  "policy_white_version": "v1",
  "started_at": "2026-04-19T00:00:00Z",
  "finished_at": "2026-04-19T00:00:10Z",
  "initial_state_type": "standard",
  "reward_perspective": "BLACK",
  "final_reward": 1,
  "winner": "BLACK",
  "turns": []
}
```

## 에피소드 필드 정의
- `episode_id: str`
  - 저장 파일 내 유일 식별자
- `status: str`
  - `completed` | `failed`
- `seed: int`
- `policy_black_version: str`
- `policy_white_version: str`
- `started_at: str`
  - ISO 8601 UTC
- `finished_at: str`
  - ISO 8601 UTC
- `initial_state_type: str`
  - `standard` | `reachable_custom`
- `initial_state: InitialStateRecord | None`
- `reward_perspective: str`
  - 기본값 `BLACK`
- `final_reward: int | float | None`
- `winner: str | None`
  - `BLACK` | `WHITE` | `DRAW` | `null`
- `turns: list[TurnRecord]`
- `failure: FailureRecord | None`

## 턴 레코드 스키마

```json
{
  "turn_index": 0,
  "player": "BLACK",
  "state": {
    "board": [["EMPTY"]],
    "current_player": "BLACK",
    "valid_moves": [[2, 3], [3, 2], [4, 5], [5, 4]],
    "is_finished": false,
    "winner": null
  },
  "action": {
    "kind": "MOVE",
    "position": [2, 3]
  },
  "policy_output": {
    "distribution_type": "full_action_space",
    "action_probabilities": {},
    "selected_action": {
      "kind": "MOVE",
      "position": [2, 3]
    },
    "state_value": null
  },
  "reward": null
}
```

## 턴 레코드 필드 정의
- `turn_index: int`
- `player: str`
  - 행동 주체
- `state: StateRecord`
- `action: ActionRecord`
- `policy_output: PolicyOutputRecord | None`
- `reward: int | float | None`
  - 기본 저장은 `null`, 종료 후 후처리로 채워도 됨

## 상태 레코드
- `board: list[list[str]]`
  - 8x8, 각 원소는 `EMPTY`, `BLACK`, `WHITE`
- `current_player: str`
- `valid_moves: list[list[int]]`
  - 예: `[[2, 3], [3, 2]]`
- `is_finished: bool`
- `winner: str | null`

## 액션 레코드
- `kind: str`
  - `MOVE` | `PASS`
- `position: list[int] | null`
  - `PASS`면 `null`

## 정책 출력 레코드
- `distribution_type: str`
  - `full_action_space` | `valid_moves_only`
- `action_probabilities: dict[str, float]`
  - 키 규약:
    - 좌표: `"r,c"` 예: `"2,3"`
    - 패스: `"PASS"`
- `selected_action: ActionRecord`
- `state_value: float | null`

규약:
- `full_action_space`이면 최대 65개 액션을 표현한다.
- `valid_moves_only`이면 `state.valid_moves` 순서와 일치해야 한다.

## 전체 액션 공간 인덱스 규약
- `full_action_space` 분포를 벡터로 다룰 때 고정 길이는 `65`다.
- 인덱스 `0..63`은 보드 좌표를 row-major 순서로 매핑한다.
  - 인덱스 계산식: `index = row * 8 + col`
  - 예: `(0,0) -> 0`, `(0,1) -> 1`, `(7,7) -> 63`
- 인덱스 `64`는 `PASS`다.
- `action_probabilities`를 dict로 저장하더라도, 벡터 변환 시 위 인덱스 규약을 반드시 사용한다.

## 초기 상태 레코드
- `initial_state`는 `reachable_custom`일 때 실제 시작 상태를 저장한다.
- `standard` 시작이면 `null`을 허용한다.

```json
{
  "board": [["EMPTY"]],
  "current_player": "BLACK"
}
```

필드:
- `board: list[list[str]]`
- `current_player: str`

## 실패 레코드

```json
{
  "error_code": "INVALID_INITIAL_STATE",
  "message": "custom initial state is not reachable",
  "failed_turn_index": null
}
```

필드:
- `error_code: str`
- `message: str`
- `failed_turn_index: int | null`

## 초기 상태 규약
- `initial_state_type = standard`이면 표준 시작 배치를 사용한다.
- `initial_state_type = reachable_custom`이면 별도 검증을 통과한 합법 상태여야 한다.
- `initial_state_type = reachable_custom`이면 `initial_state` 필드에 실제 시작 보드와 현재 플레이어를 함께 저장해야 한다.
- 합법성 검증 실패 시 `status = failed`로 저장하고 학습 입력에는 포함하지 않는다.

## 저장 규약
- `completed` 에피소드만 학습 기본 입력으로 사용한다.
- `failed` 에피소드는 디버깅/운영 로그로만 사용한다.
- 시간 필드는 모두 UTC ISO 8601 문자열로 저장한다.
- 동일 파일 안에서 필드 이름과 타입은 고정한다.

## JSONL 예시

```json
{
  "episode_id": "ep-000001",
  "status": "completed",
  "seed": 7,
  "policy_black_version": "random-v1",
  "policy_white_version": "random-v1",
  "started_at": "2026-04-19T09:00:00Z",
  "finished_at": "2026-04-19T09:00:02Z",
  "initial_state_type": "standard",
  "reward_perspective": "BLACK",
  "final_reward": 1,
  "winner": "BLACK",
  "turns": []
}
```
