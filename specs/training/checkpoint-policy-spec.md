# Checkpoint 명세

## 목적
이 문서는 `training` 계층의 체크포인트 저장/로드 경로가 따라야 할 최소 계약을 정의한다.

## 관련 문서
- `docs/training/checkpoint-policy.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/training-pipeline-spec.md`

## 구현 대상
- 체크포인트 로드 helper
- 향후 체크포인트 저장 helper
- inference checkpoint / training checkpoint 구분 계약

## checkpoint 종류 계약
- `inference checkpoint`는 self-play, evaluator, runtime에서 바로 추론 가능한 모델 복원용 산출물이어야 한다.
- `training checkpoint`는 trainer의 `resume` 경로에 사용할 수 있는 학습 상태 복원용 산출물이어야 한다.
- 두 종류는 같은 payload 형식을 강제하지 않는 것을 기본값으로 둔다.
- `latest training checkpoint`는 기본 resume 기준이어야 한다.
- `best training checkpoint`와 `best inference checkpoint`는 서로 다른 산출물로 유지할 수 있어야 한다.
- best 계열 checkpoint는 필요 시 다음 세 트랙을 표현할 수 있어야 한다.
  - `best_black`
  - `best_white`
  - `best_balanced`
- `latest training checkpoint`는 위 best 트랙과 별개인 단일 세션 상태여야 한다.

## 로드 계약
- 체크포인트 로더는 최소한 다음 두 입력 형태를 허용해야 한다.
  - 순수 `state_dict`
  - `model_state_dict`, `model_version`을 포함한 dict
- 로드 결과는 self-play에 연결 가능한 agent 또는 model이어야 한다.
- dict payload에서는 `model_state_dict`를 `state_dict`보다 우선 해석해야 한다.
- 호출자 명시 `version`이 있으면 checkpoint 내 `model_version`보다 우선해야 한다.
- 호출자 명시 `model_kwargs`가 있으면 checkpoint 내 구조 파라미터보다 우선할 수 있어야 한다.
- `model_state_dict`와 `state_dict` 키가 모두 없는 dict는 자동으로 순수 state dict로 간주하면 안 된다.
- 순수 `state_dict`로 인정하는 dict는 값이 모두 tensor-like weight 항목으로 해석 가능한 경우로 제한하는 편을 기본값으로 둔다.
- `resume`용 로더는 필요 시 `optimizer_state_dict`, `training_state` 같은 학습 메타데이터를 함께 반환할 수 있어야 한다.

## 권장 payload 계약
- 기본 checkpoint payload는 dict를 권장한다.
- 권장 최소 키는 다음과 같다.
  - `model_state_dict`
  - `model_version`
- 선택 키는 다음과 같다.
  - `model_kwargs`
  - `checkpoint_format_version`
  - `saved_at`
- `training checkpoint`의 선택 키는 다음을 포함할 수 있어야 한다.
  - `optimizer_state_dict`
  - `training_state`
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
  - `track`

## training state 계약
- `training checkpoint`의 `training_state`는 trainer가 누적 학습 상태를 복원하는 데 사용할 수 있어야 한다.
- `training_state`에는 가능하면 다음 항목이 포함된다.
  - `completed_iterations`
  - `completed_epochs`
  - `completed_steps`
  - `last_self_play_data_ref` 또는 동등 데이터 참조 메타데이터
  - `saved_at`
- 위 항목 전체를 필수로 고정하지는 않지만, `resume` 경로가 요구하는 최소 학습 상태는 문서나 구현에서 추적 가능해야 한다.
- `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`는 `training_state` 안이 아니라 checkpoint top-level 메타데이터로 두는 것을 기본값으로 한다.
- best 계열 checkpoint라면 어떤 트랙의 최고 모델인지 나타내는 `track` 식별자를 top-level 메타데이터로 기록할 수 있어야 한다.
- `balanced_eval_score`는 양방향 평가 승률의 평균값으로 기록하는 것을 기본값으로 한다.
- 양방향 평가 게임 수가 다르면 `balanced_eval_score`는 가중 평균 규칙으로 계산할 수 있어야 한다.

## 저장 계약
- 저장 경로를 추가하면 최소한 모델 파라미터와 모델 버전을 기록할 수 있어야 한다.
- 모델 구성 파라미터가 필요하면 함께 저장 가능한 확장 지점을 가져야 한다.
- writer가 dict payload를 쓴다면 최소한 `model_state_dict`를 기록해야 한다.
- writer는 기본적으로 모델 복원에 불필요한 runtime 전용 정보를 강제 포함하지 않는다.
- `training checkpoint` writer는 `resume`에 필요한 모델 상태와 학습 상태를 함께 기록할 수 있어야 한다.
- 권장 기본 저장 정책은 다음을 표현 가능해야 한다.
  - iteration 종료 후 `latest training checkpoint` 저장
  - 평가 기준 충족 시 `best_black`, `best_white`, `best_balanced` training checkpoint 갱신
  - 필요 시 대응하는 inference checkpoint 저장

## 버전 계약
- 체크포인트에서 해석된 모델 버전은 agent `version`과 연결 가능해야 한다.
- 체크포인트에 버전이 없으면 구현이 정의한 기본 모델 버전으로 해석할 수 있어야 한다.
- 버전 해석 우선순위는 다음과 같아야 한다.
  - 호출자 명시 `version`
  - checkpoint `model_version`
  - 구현 기본 모델 버전

## 오류 계약
- 구조가 맞지 않는 체크포인트는 조용히 통과하면 안 된다.
- 로드 실패는 호출자에게 예외 또는 명시적 실패로 드러나야 한다.
- `model_state_dict`, `state_dict`, 순수 state dict 중 어느 경로로도 해석할 수 없으면 실패해야 한다.
- 모델 구조와 state dict가 맞지 않으면 `load_state_dict` 실패가 그대로 드러나야 한다.
- `resume_from_checkpoint`가 주어졌는데 trainer가 요구하는 `training_state` 또는 `optimizer_state_dict`가 부족하면 명시적으로 실패할 수 있어야 한다.

## 반환 계약
- agent loader는 self-play에 바로 연결 가능한 agent를 반환해야 한다.
- model loader를 별도로 두는 경우 model과 버전 해석 결과를 함께 반환할 수 있어야 한다.
- training checkpoint loader를 별도로 두는 경우 최소한 다음 결과를 함께 반환할 수 있어야 한다.
  - model
  - resolved version
  - model kwargs
  - optional optimizer state
  - optional training state
  - optional top-level evaluation metadata

## 비범위
- optimizer 내부 포맷 표준화
- 분산 학습 체크포인트 병합
