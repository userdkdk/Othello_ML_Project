# 학습 운영 명세

## 목적
이 문서는 `training` 계층에서 학습 세션 제어, iteration 실행, 대시보드용 상태 스냅샷, checkpoint 비교가 따라야 할 상세 계약을 정의한다.

## 관련 문서
- `docs/training/training-ops.md`
- `docs/training/trainer-loop.md`
- `docs/training/checkpoint-policy.md`
- `specs/training/trainer-loop-spec.md`
- `specs/training/checkpoint-policy-spec.md`

## 구현 대상
- 학습 세션 상태 객체
- iteration 실행기
- 대시보드용 상태 스냅샷 직렬화
- checkpoint 비교 실행기

## 용어 계약
- `training session`
  - 동일한 모델, optimizer, checkpoint 경로 집합, iteration 누적 상태를 공유하는 학습 실행 컨텍스트
- `iteration`
  - self-play, training, checkpoint 저장, 평가, 승격 판단을 한 번 수행하는 단위
- `comparison`
  - 두 checkpoint를 agent로 로드해 양방향 평가를 수행하는 단발 실행

## 세션 상태 계약
- 세션은 최소한 다음 상태 문자열을 사용해야 한다.
  - `idle`
  - `running`
  - `pause_requested`
  - `paused`
  - `completed`
  - `failed`
  - `stopped`
- 상태 전이 기본 규칙은 다음과 같다.
  - `idle -> running`
  - `running -> pause_requested`
  - `pause_requested -> paused`
  - `paused -> running`
  - `running -> completed`
  - `running -> failed`
  - `running -> stopped`
  - `paused -> stopped`
- `pause_requested`는 iteration 중간 강제 중단이 아니라 "현재 iteration 종료 후 멈춤" 의미여야 한다.

## 세션 메타데이터 계약
- 세션 스냅샷은 최소한 다음 필드를 노출할 수 있어야 한다.
  - `session_id`
  - `status`
  - `current_iteration`
  - `active_stage`
  - `created_at`
  - `updated_at`
  - `start_from_checkpoint_path`
  - `latest_checkpoint_path`
  - `best_training_checkpoint_paths`
  - `best_inference_checkpoint_paths`
  - `last_error`
- `active_stage`는 최소한 다음 중 하나를 표현 가능해야 한다.
  - `idle`
  - `self_play`
  - `train`
  - `evaluate_heuristic`
  - `evaluate_current_best`
  - `save_checkpoint`
  - `promote_checkpoint`
  - `completed`

## iteration 실행 입력 계약
- iteration 실행 요청은 최소한 다음 설정을 받을 수 있어야 한다.
  - `num_self_play_games`
  - `self_play_seed`
  - `epochs`
  - `latest_checkpoint_path`
  - `checkpoint_version`
  - `checkpoint_model_kwargs`
  - `heuristic_games_per_side`
  - `heuristic_seed`
  - `current_best_checkpoint_paths`
  - `current_best_games_per_side`
  - `current_best_seed`
  - `best_training_checkpoint_paths`
  - `best_inference_checkpoint_paths`
- 지정되지 않은 필드는 구현 기본값을 사용할 수 있어야 한다.

## iteration 실행 출력 계약
- iteration 결과는 최소한 다음 정보를 포함해야 한다.
  - `iteration`
  - `self_play_statistics`
  - `self_play_failures`
  - `written_episode_count`
  - `training_report`
  - `heuristic_report`
  - `current_best_reports`
  - `promoted_tracks`
  - `latest_checkpoint_path`
  - `best_training_checkpoint_paths`
  - `best_inference_checkpoint_paths`
- `training_report`는 `ModelTrainingReport`와 정합해야 한다.
- `promoted_tracks`는 `best_black`, `best_white`, `best_balanced`의 부분집합이어야 한다.

## 대시보드 스냅샷 계약
- 대시보드 조회용 스냅샷은 세션 전체를 다시 계산하지 않고 직렬화 가능한 경량 요약이어야 한다.
- 최소 직렬화 필드는 다음을 포함해야 한다.
  - `session`
  - `latest_iteration`
  - `history`
  - `checkpoint_inventory`
- `latest_iteration`이 존재할 때 최소 다음 필드를 포함해야 한다.
  - `iteration`
  - `samples`
  - `policy_loss`
  - `value_loss`
  - `self_play_games`
  - `self_play_failures`
  - `heuristic_report`
  - `current_best_reports`
  - `promoted_tracks`
- `history`는 최근 iteration 결과를 제한된 개수로 보존할 수 있어야 한다.

## checkpoint inventory 계약
- checkpoint inventory는 존재하는 경로만 나열해도 되지만, 기본 슬롯 이름은 유지해야 한다.
- 최소 슬롯은 다음을 표현 가능해야 한다.
  - `latest_training`
  - `best_black_training`
  - `best_white_training`
  - `best_balanced_training`
  - `best_black_inference`
  - `best_white_inference`
  - `best_balanced_inference`
- training checkpoint 슬롯은 운영 상태 표시와 `start_from_checkpoint` 입력 후보를 위한 것이다.
- 비교 실행과 추론 agent 기본 입력은 inference checkpoint 슬롯을 우선 사용해야 한다.
- 각 inventory 항목은 가능하면 다음 메타데이터를 포함해야 한다.
  - `path`
  - `exists`
  - `model_version`
  - `track`
  - `saved_at`
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`

## checkpoint 비교 입력 계약
- 비교 요청은 최소한 다음 필드를 받을 수 있어야 한다.
  - `left_checkpoint_path`
  - `right_checkpoint_path`
  - `num_games_per_side`
  - `seed`
  - `left_version`
  - `right_version`
  - `left_model_kwargs`
  - `right_model_kwargs`
- 기본 비교 대상은 inference checkpoint여야 한다.
- training checkpoint를 비교 입력으로 허용하려면 inference agent 로드와 호환되는 payload임이 보장되어야 한다.

## checkpoint 비교 실행 계약
- 비교는 다음 두 평가를 수행해야 한다.
  - left agent as black vs right agent as white
  - right agent as black vs left agent as white
- 리포트는 "left checkpoint 관점"으로 정규화하는 것을 기본값으로 둔다.
- left 관점 리포트는 최소한 다음을 포함해야 한다.
  - `games`
  - `failures`
  - `left_black_side_win_rate`
  - `left_white_side_win_rate`
  - `left_balanced_eval_score`
  - `draw_rate`
- 비교 리포트에는 양쪽 식별 정보도 포함할 수 있어야 한다.
  - `left`
  - `right`

## checkpoint 비교 출력 계약
- 비교 결과는 최소한 다음 직렬화 구조를 제공할 수 있어야 한다.
  - `comparison_id`
  - `left_checkpoint`
  - `right_checkpoint`
  - `num_games_per_side`
  - `seed`
  - `report`
  - `created_at`
- `left_checkpoint`, `right_checkpoint`는 최소한 `path`, `model_version`, `track`를 표현할 수 있어야 한다.

## 오류 계약
- 존재하지 않는 checkpoint는 명시적으로 실패해야 한다.
- 지원하지 않는 checkpoint payload는 명시적으로 실패해야 한다.
- 세션이 `running` 상태일 때 중복 `start` 또는 `start_from_checkpoint`는 실패해야 한다.
- 세션이 없는데 `pause`, `resume_session`, `stop`이 호출되면 실패해야 한다.
- `pause_requested` 상태에서 다시 `pause` 요청이 와도 무해하게 같은 상태를 반환할 수 있다.
- 비교 실행 중 한쪽 agent 로드 실패가 나면 부분 성공으로 숨기지 말고 전체 실패로 반환해야 한다.

## 비범위
- 복수 동시 세션 스케줄링
- 분산 self-play 워커 관리
- 실험 결과 영구 검색 인덱스
