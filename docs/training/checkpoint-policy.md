# Checkpoint 기준

## 목적
이 문서는 `training` 계층에서 모델 체크포인트를 저장하고 다시 로드할 때 따를 상위 기준을 정의한다.

현재 저장소에는 체크포인트 로드 helper가 일부 존재한다. 이 문서는 향후 저장과 로드를 함께 다루는 정책을 고정한다.

## 적용 범위
- CNN 정책/가치 모델 체크포인트
- 정책 버전 메타데이터
- 저장 경로와 로드 진입점

## 기본 원칙
- 체크포인트는 모델 상태와 버전 정보를 함께 다룰 수 있어야 한다.
- 로드 후 생성된 agent는 self-play와 evaluator에 바로 연결 가능해야 한다.
- 체크포인트 정책은 `runtime` 배포 포맷과 분리해서 해석한다.
- 기본 정책은 "모델 복원 가능성"을 우선하고, 부가 메타데이터는 확장 가능 필드로 본다.
- 학습 재개용 checkpoint와 추론용 checkpoint는 목적이 다르므로 같은 포맷으로 강제하지 않는 것을 기본값으로 둔다.

## checkpoint 종류
- `inference checkpoint`
  - 목적: self-play, evaluator, runtime에서 정책을 로드해 바로 추론
  - 최소 포함 정보: `model_state_dict`, `model_version`
  - 필요 시 `model_kwargs`를 포함할 수 있다.
- `training checkpoint`
  - 목적: trainer가 같은 학습 세션을 이어서 진행하는 `resume` 경로
  - 최소 포함 정보: `model_state_dict`, `model_version`
  - 권장 확장 정보: `model_kwargs`, `optimizer_state_dict`, `training_state`
- `best inference checkpoint`와 `best training checkpoint`는 서로 다른 산출물로 유지할 수 있다.
- best 계열 checkpoint는 필요 시 다음 세 트랙으로 분리할 수 있어야 한다.
  - `best_black`
  - `best_white`
  - `best_balanced`
- 위 트랙 이름은 checkpoint 파일명, checkpoint 식별자, 메타데이터에서 일관되게 추적 가능해야 한다.
- 권장 기본 방향은 다음 셋 중 하나로 명시적 표현을 유지하는 것이다.
  - 파일명 suffix
  - checkpoint metadata `track`
  - 디렉터리 구분
- `latest training checkpoint`는 트랙별 best와 별개인 단일 학습 세션 상태를 뜻하며, 기본 resume 기준이다.

## 권장 경로 규칙
- 기본 checkpoint 루트 디렉터리는 호출자가 명시적으로 주지 않으면 `checkpoints/`를 사용한다.
- `latest training checkpoint`의 권장 기본 경로는 다음과 같다.
  - `checkpoints/latest-training.pt`
- best 계열 `training checkpoint`의 권장 기본 경로는 다음과 같다.
  - `checkpoints/best-black-training.pt`
  - `checkpoints/best-white-training.pt`
  - `checkpoints/best-balanced-training.pt`
- best 계열 `inference checkpoint`의 권장 기본 경로는 다음과 같다.
  - `checkpoints/best-black-inference.pt`
  - `checkpoints/best-white-inference.pt`
  - `checkpoints/best-balanced-inference.pt`
- 위 파일명은 기본 운영 규칙이며, 다른 경로를 쓰더라도 역할이 추적 가능해야 한다.
- `latest training checkpoint`는 항상 단일 파일을 기본값으로 유지하고, `latest_black` 같은 트랙별 latest 개념은 두지 않는 것을 기본값으로 한다.
- best 계열 checkpoint는 파일명만으로도 트랙과 용도를 알 수 있어야 한다.
  - 예: `best-black-training.pt`
  - 예: `best-balanced-inference.pt`
- 경로 해석 구현은 가능하면 다음 우선순위를 따른다.
  - 호출자 명시 경로
  - 프로젝트 기본 checkpoint 루트 기준 권장 파일명
- 파일 경로와 별개로 best 계열 checkpoint에는 가능하면 top-level metadata `track`를 함께 기록한다.

## current-best 로드 기준
- trainer-loop가 현재 최고 모델을 비교 대상으로 사용할 때는 기본적으로 best 계열 `inference checkpoint`를 읽는 것을 권장한다.
- 기본 current-best 로드 경로는 다음과 같이 해석한다.
  - `best_black` 비교 대상: `checkpoints/best-black-inference.pt`
  - `best_white` 비교 대상: `checkpoints/best-white-inference.pt`
  - `best_balanced` 비교 대상: `checkpoints/best-balanced-inference.pt`
- 위 파일이 없으면 현재 iteration의 승격 비교는 해당 트랙에 대해 생략하거나, 호출자가 명시한 대체 agent를 사용하도록 구현에서 선택할 수 있어야 한다.
- 기본 resume 경로는 `latest training checkpoint`이며, best 계열 checkpoint를 기본 resume 대상으로 삼지 않는 것을 권장한다.

## 용어 기준
- `resume`은 같은 학습 세션을 이어서 진행하는 재개를 의미한다.
- `continue`는 이전 모델을 초기값으로 사용하되, 새로운 학습 세션으로 시작하는 경로를 의미한다.
- `resume`은 기본적으로 `training checkpoint`를 입력으로 사용한다.
- `continue`는 `inference checkpoint` 또는 `training checkpoint` 어느 쪽에서도 시작할 수 있다.

## 최소 포함 정보
- 모델 파라미터 또는 `state_dict`
- 모델 버전 문자열
- 필요 시 모델 구성 파라미터

## 기본 payload 방향
- 저장 payload 기본값은 dict 기반 포맷을 권장한다.
- 권장 최소 키는 다음과 같다.
  - `model_state_dict`
  - `model_version`
- 필요하면 다음 확장 키를 추가할 수 있다.
  - `model_kwargs`
  - `checkpoint_format_version`
  - `saved_at`
- `training checkpoint`에는 필요 시 다음 확장 키를 둘 수 있다.
  - `optimizer_state_dict`
  - `training_state`

## 호환성 기준
- 최소한 순수 `state_dict` 로드를 허용한다.
- `model_state_dict`와 `model_version`을 가진 dict 로드를 허용할 수 있어야 한다.
- 구조가 바뀌면 버전 문자열도 함께 갱신해야 한다.
- dict 입력에서 `model_state_dict`가 있으면 이를 우선한다.
- `model_state_dict`가 없고 `state_dict`가 있으면 그 값을 대체 경로로 허용할 수 있다.
- 둘 다 없으면 payload 전체를 곧바로 model state로 해석하는 것은 제한적으로만 허용해야 하며, 문서화된 경우에만 사용한다.

## 버전 해석 우선순위
- 호출자가 명시적으로 `version`을 넘기면 이 값을 최우선으로 사용한다.
- 체크포인트 payload에 `model_version`이 있으면 그 다음 우선순위로 사용한다.
- 둘 다 없으면 구현이 가진 기본 모델 버전을 사용한다.
- 어떤 경로로 버전이 정해졌는지 호출자나 문서에서 추적 가능해야 한다.

## 모델 구성 파라미터 기준
- 모델 구조를 복원하는 데 추가 파라미터가 필요하면 `model_kwargs` 같은 명시적 키로 저장하는 것을 권장한다.
- 로더는 호출자 제공 `model_kwargs`와 체크포인트 내 구조 파라미터의 우선순위를 문서화해야 한다.
- 기본 권장 우선순위는 호출자 명시값 > 체크포인트 저장값 > 모델 기본값이다.

## 메타데이터 기준
- self-play episode의 정책 버전과 체크포인트 버전은 연결 가능해야 한다.
- 저장 시점의 버전 문자열이 불명확하면 기본 모델 버전을 사용하더라도 문서화되어야 한다.
- 체크포인트에서 복원한 agent `version`은 episode의 `policy_black_version` 또는 `policy_white_version`으로 그대로 연결 가능해야 한다.
- `training checkpoint`의 `training_state`는 trainer가 누적 iteration/epoch/step을 복원하는 데 사용할 수 있어야 한다.
- 평가 기반 승격을 쓰는 경우 `best checkpoint` 선정에 사용된 기준 또는 점수는 추적 가능해야 한다.
- `balanced_eval_score`는 `training_state` 안이 아니라 checkpoint top-level 메타데이터로 두는 것을 기본값으로 한다.
- 색을 반반 바꿔 평가하는 경우 다음 메타데이터를 top-level에서 추적 가능해야 한다.
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- best 계열 checkpoint라면 가능하면 어떤 트랙의 최고 모델인지 나타내는 식별자도 top-level에서 추적 가능해야 한다.
  - 예: `track=best_black|best_white|best_balanced`
- `balanced_eval_score`는 양방향 평가 승률의 평균값으로 기록하는 것을 기본값으로 한다.
- 양방향 평가 게임 수가 다르면 `balanced_eval_score`는 가중 평균 규칙으로 계산할 수 있어야 한다.

## training state 기준
- `training checkpoint`의 `training_state`에는 가능하면 다음 정보를 포함한다.
  - `completed_iterations`
  - `completed_epochs`
  - `completed_steps`
  - `last_self_play_data_ref` 또는 동등 데이터 참조 메타데이터
  - `saved_at`
- 위 항목 전체를 필수로 강제하지는 않지만, 기본 resume 경로에서 누적 학습 상태를 해석할 수 있어야 한다.
- `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`는 top-level checkpoint 메타데이터에 두는 것을 권장한다.

## 저장 시점 기준
- 기본 저장 단위는 "모델이 복원 가능한 시점"이다.
- epoch 종료, 평가 종료, 최고 성능 갱신 같은 저장 트리거는 학습 루프 정책에서 별도로 결정한다.
- checkpoint writer는 언제 저장할지보다 무엇을 저장할지에 집중한다.
- 권장 기본 운영은 다음과 같다.
  - 매 iteration 종료 후 `latest training checkpoint` 저장
  - 평가 기준 충족 시 `best_black`, `best_white`, `best_balanced` training checkpoint 갱신
  - 필요 시 같은 모델 상태에서 대응하는 inference checkpoint를 별도 갱신

## 오류 기준
- 체크포인트 파일이 존재하지 않거나 읽을 수 없으면 로드는 명시적으로 실패해야 한다.
- payload 구조가 기대한 형태와 다르면 조용히 기본값으로 넘어가면 안 된다.
- state dict load 실패는 호출자에게 예외로 드러나야 한다.
- `resume`에 필요한 학습 상태가 부족하면 호출자가 명시적으로 실패를 선택할 수 있어야 한다.

## 비범위
- 모델 아티팩트 레지스트리
- 원격 체크포인트 동기화
- optimizer 내부 포맷 표준화
