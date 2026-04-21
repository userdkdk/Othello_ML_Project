# 학습 대시보드 명세

## 목적
이 문서는 `runtime` 계층에서 학습 제어, 상태 조회, checkpoint 비교를 노출하는 FastAPI 및 웹 UI 계약을 정의한다.

## 관련 문서
- `docs/runtime/training-dashboard.md`
- `docs/training/training-ops.md`
- `specs/training/training-ops-spec.md`
- `specs/runtime/web-runtime-spec.md`

## 구현 대상
- 학습 대시보드 HTML 또는 동등 웹 UI
- 학습 제어 API
- 세션 상태 조회 API
- checkpoint 비교 API

## 라우팅 계약
- 학습 운영 UI는 기본 게임 UI와 분리된 경로를 가져야 한다.
- 권장 기본 경로는 다음 중 하나다.
  - `GET /training`
  - `GET /ops/training`
- 학습 운영 API는 기본 게임 API와 분리된 namespace를 사용해야 한다.
- 권장 기본 prefix는 `/api/training`이다.

## 최소 엔드포인트 계약
- `GET /api/training/state`
- `POST /api/training/start`
- `POST /api/training/start-from-checkpoint`
- `POST /api/training/run-once`
- `POST /api/training/pause`
- `POST /api/training/resume-session`
- `POST /api/training/stop`
- `POST /api/training/compare`
- `GET /api/training/comparisons/latest`

## `GET /api/training/state` 계약
- 현재 세션이 없더라도 성공 응답을 반환할 수 있어야 한다.
- 최소 응답 필드는 다음을 포함해야 한다.
  - `session`
  - `latest_iteration`
  - `history`
  - `checkpoint_inventory`
  - `last_comparison`
- 세션이 없더라도 `session` 객체는 존재해야 하며, 이때 `session.status`는 `idle`이어야 한다.

## `POST /api/training/start` 계약
- 새 학습 세션을 생성하고 연속 iteration 실행을 시작하는 요청이다.
- 요청 본문은 최소한 다음 필드를 받을 수 있어야 한다.
  - `num_self_play_games`
  - `epochs`
  - `checkpoint_version`
  - `latest_checkpoint_path`
  - `best_training_checkpoint_paths`
  - `best_inference_checkpoint_paths`
  - `heuristic_games_per_side`
  - `current_best_checkpoint_paths`
  - `current_best_games_per_side`
- 성공 시 응답은 최소한 `session` 스냅샷을 반환해야 한다.

## `POST /api/training/start-from-checkpoint` 계약
- training checkpoint를 입력으로 새 학습 세션을 생성하고 연속 iteration 실행을 시작하는 요청이다.
- 요청 본문은 최소한 다음 필드를 받을 수 있어야 한다.
  - `start_from_checkpoint_path`
  - `num_self_play_games`
  - `epochs`
  - `checkpoint_version`
  - `latest_checkpoint_path`
  - `best_training_checkpoint_paths`
  - `best_inference_checkpoint_paths`
  - `heuristic_games_per_side`
  - `current_best_checkpoint_paths`
  - `current_best_games_per_side`
- 성공 시 응답은 최소한 `session` 스냅샷을 반환해야 한다.

## `POST /api/training/run-once` 계약
- 연속 루프를 돌리지 않고 정확히 한 iteration만 수행하는 요청이다.
- 요청 본문은 `start`와 동일한 설정 집합 또는 그 부분집합을 받을 수 있어야 한다.
- checkpoint 기반 단발 실행이 필요하면 `start_from_checkpoint_path`를 추가 입력으로 받을 수 있어야 한다.
- 성공 응답은 최소한 다음을 포함해야 한다.
  - `session`
  - `latest_iteration`

## `POST /api/training/pause` 계약
- 현재 iteration 종료 후 멈추도록 요청해야 한다.
- 세션이 `running`이 아니면 명시적 실패 또는 no-op 성공 중 하나를 선택하되 일관돼야 한다.
- 성공 시 현재 세션 상태를 반환해야 한다.

## `POST /api/training/resume-session` 계약
- `paused` 상태 세션을 다시 `running`으로 전환해야 한다.
- 성공 시 현재 세션 상태를 반환해야 한다.

## `POST /api/training/stop` 계약
- 현재 세션을 종료 상태로 전환해야 한다.
- 성공 시 현재 세션 상태를 반환해야 한다.

## `POST /api/training/compare` 계약
- 두 checkpoint를 비교하는 단발 실행 요청이다.
- 요청 본문은 최소한 다음 필드를 포함해야 한다.
  - `left_checkpoint_path`
  - `right_checkpoint_path`
  - `num_games_per_side`
- 선택 필드는 다음을 포함할 수 있다.
  - `seed`
  - `left_version`
  - `right_version`
  - `left_model_kwargs`
  - `right_model_kwargs`
- 기본 비교 입력은 inference checkpoint여야 한다.
- training checkpoint는 inference agent 로드와 호환될 때만 명시적으로 허용할 수 있다.
- 성공 응답은 최소한 다음을 포함해야 한다.
  - `comparison`

## `GET /api/training/comparisons/latest` 계약
- 마지막으로 성공한 비교 결과가 있으면 반환해야 한다.
- 없으면 `200` 응답과 함께 `comparison: null`을 반환해야 한다.

## UI 상태 모델 계약
- 대시보드 프론트엔드는 최소한 다음 상태 조각을 유지할 수 있어야 한다.
  - `session`
  - `latestIteration`
  - `history`
  - `checkpointInventory`
  - `comparisonForm`
  - `lastComparison`
  - `errorMessage`
- 긴 작업 중 UI는 적어도 다음 버튼 상태를 구분해야 한다.
  - enabled
  - disabled
  - pending

## UI 표시 계약
- 학습 운영 UI는 최소한 다음 정보를 표시해야 한다.
  - 세션 상태
  - 현재 단계
  - iteration 번호
  - 최근 self-play 통계
  - 최근 학습 loss
  - 최근 평가 점수
  - 최근 승격된 track
  - checkpoint inventory
  - 마지막 checkpoint 비교 결과

## 폴링 계약
- 기본 구현은 polling 기반이어도 된다.
- 폴링 간격은 구현 선택 사항이지만, 세션이 `running`일 때와 아닐 때 다르게 둘 수 있어야 한다.
- 폴링 응답은 전체 대국 raw episode를 포함하지 않는 경량 payload를 기본값으로 둔다.

## 오류 응답 계약
- 오류 응답은 최소한 다음 필드를 포함할 수 있어야 한다.
  - `error_code`
  - `message`
- 권장 오류 코드는 다음과 같다.
  - `SESSION_ALREADY_RUNNING`
  - `NO_ACTIVE_SESSION`
  - `INVALID_SESSION_STATE`
  - `CHECKPOINT_NOT_FOUND`
  - `CHECKPOINT_LOAD_FAILED`
  - `COMPARISON_FAILED`
  - `TRAINING_FAILED`

## 보드 UI와의 분리 계약
- `/api/state`, `/api/new`, `/api/move`, `/api/pass`와 학습 운영 API는 서로의 응답 스키마를 공유하지 않는다.
- 게임 보드 UI는 학습 대시보드 상태를 요구하지 않아야 한다.
- 학습 대시보드는 raw 게임 상태를 요구하지 않아야 한다.

## 비범위
- websocket 전용 설계 강제
- 인증/인가
- 다중 사용자 세션 격리
