# 학습 파이프라인 명세

## 목적
이 문서는 현재 `src/training/` 구현이 따르는 학습 파이프라인의 실행 순서와 공개 산출물을 코드 계약 수준에서 정의한다.

이 문서는 trainer-loop와 checkpoint의 최종 설계 문서가 아니라, 현재 구현 상태를 설명하는 spec이다.

## 관련 경로
- `src/training/match_runner.py`
- `src/training/self_play_runner.py`
- `src/training/episode.py`
- `src/training/state_encoder.py`
- `src/training/action_mask.py`
- `src/training/trainer.py`
- `src/training/evaluator.py`

## 파이프라인 단계
1. `run_self_play()`가 게임 수만큼 `run_match()`를 호출한다.
2. `run_match()`는 항상 표준 초기 상태로 대국을 시작한다.
3. 각 턴에서 현재 상태 기준 유효 수를 계산한다.
4. 현재 플레이어에 해당하는 agent가 행동을 선택한다.
5. 행동 적용 전 `encoded_state`와 `action_mask`를 계산한다.
6. 현재 턴 정보를 `TurnRecord`로 `Episode`에 추가한다.
7. 엔진에 행동을 적용한다.
8. 실패 시 episode를 `failed`로 종료한다.
9. 정상 종료 시 winner와 final reward를 채우고 모든 턴에 동일 보상을 연결한다.
10. `run_self_play()`는 전체 대국 집합을 `SelfPlayResult`로 반환한다.
11. `Trainer.train()`은 episode iterable을 입력으로 받아 `TrainingReport`를 만든다.
12. `Evaluator.evaluate()`는 agent와 게임 수를 입력으로 받아 별도 평가 실행 뒤 `EvaluationReport`를 만든다.

## `run_match` 계약
- 시그니처: `run_match(black_agent, white_agent, seed, episode_id) -> MatchResult`
- 시작 상태는 `create_new_game()` 결과여야 한다.
- agent 호출 시 입력 상태는 원본과 분리된 clone 또는 동등 스냅샷이어야 한다.
- engine 계층이 `GameState.clone()`을 제공한다면 그 경로를 우선 사용할 수 있다.
- CNN policy agent를 포함한 모든 agent는 `Agent` 프로토콜로 연결 가능해야 한다.
- agent는 유효 수가 있으면 반드시 그중 하나를 반환해야 한다.
- `PASS`는 유효 수가 없을 때만 유효하다.
- 유효하지 않은 좌표 또는 잘못된 `PASS`를 반환하면:
  - 엔진 적용 결과는 실패여야 한다.
  - episode는 `failed`가 되어야 한다.
  - 실패 원인과 실패 턴 인덱스를 기록해야 한다.
- 성공 종료 시 `MatchResult`는 다음 값을 포함해야 한다.
  - 최종 `GameState`
  - 최종 `Episode`
  - 실제 move 개수
  - 실제 pass 개수
- `Episode.policy_black_version`, `Episode.policy_white_version`은 실제 정책 공급자의 버전을 반영해야 한다.

## `TurnRecord` 수집 계약
- 각 턴에는 최소한 다음 정보가 메모리상 `TurnRecord`에 있어야 한다.
  - `turn_index`
  - `player`
  - `state`
  - `action`
  - `valid_moves`
  - `action_mask`
  - `encoded_state`
  - `policy_output`
  - `reward`
- `encoded_state`는 행동 적용 전 상태 기준으로 계산해야 한다.
- `action_mask`는 같은 턴의 `valid_moves`와 정합해야 한다.
- `policy_output`은 사용된 정책 계층의 분포, 선택 행동, 상태 가치와 정합해야 한다.

## 직렬화 계약
- `Episode.to_dict()`는 직렬화 기본 경로다.
- 직렬화 출력에는 최소한 `self-play-data-schema.md`에 정의된 필드가 포함되어야 한다.
- 현재 구현 기준으로 `TurnRecord.encoded_state`는 메모리상 필드이지만 기본 직렬화 출력에는 포함되지 않는다.
- 따라서 학습 입력 텐서를 저장 산출물에 남기려면 별도 저장 확장이 필요하다.

## `run_self_play` 계약
- 시그니처: `run_self_play(black_agent, white_agent, num_games, seed=0) -> SelfPlayResult`
- 각 게임의 실제 시드는 `seed + game_index`를 사용한다.
- 모든 게임의 `Episode`는 결과 리스트에 포함되어야 한다.
- 실패 episode는 `failures`에 집계되지만 승패 통계에는 포함되지 않아야 한다.
- `run_self_play()`의 직접 반환값에는 `TrainingReport`, `EvaluationReport`가 포함되지 않는다.

## `Trainer` 계약
- 시그니처: `Trainer.train(episodes) -> TrainingReport`
- 입력은 episode iterable이어야 한다.
- `TrainingReport`는 episode 집합의 요약 리포트여야 하며, 현재 범위에서 모델 파라미터 업데이트를 의미하지 않는다.

## `Evaluator` 계약
- 시그니처: `Evaluator.evaluate(black_agent, white_agent, num_games, seed=0) -> EvaluationReport`
- 입력은 기존 episode 집합이 아니라 평가에 사용할 agent와 게임 수다.
- `EvaluationReport`는 내부 평가 실행 결과를 요약해야 한다.

## 리포트 계약

### `TrainingReport`
- 완료 episode 수
- 실패 episode 수
- 완료 episode 기준 평균 턴 수
- 완료 episode 기준 보상 분포

### `EvaluationReport`
- 통계에 반영된 게임 수
- black win rate
- white win rate
- draw rate
- failures

주의:
- `TrainingReport`와 `EvaluationReport`는 같은 `run_self_play()` 호출의 직접 산출물이 아니다.
- 둘은 각각 `Trainer`, `Evaluator`의 별도 진입점에서 생성된다.

## 비범위
- optimizer, loss, checkpoint 저장
- 모델 파라미터 업데이트
- custom initial state 합법성 검증
- `encoded_state`의 기본 파일 저장

## 상위 설계와의 관계
- 누적 학습 설계 기준은 `docs/training/trainer-loop.md`, `docs/training/checkpoint-policy.md`를 우선한다.
- 이 spec은 현재 구현 기준의 파이프라인 계약을 설명하므로, 상위 설계 문서에 정의된 trainer-loop와 checkpoint 운영 규칙이 모두 현재 코드에 반영되었다고 해석하면 안 된다.
