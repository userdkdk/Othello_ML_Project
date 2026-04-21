# CNN 정책 모델 기준

## 목적
이 문서는 오셀로 self-play와 추론에 사용할 CNN 기반 정책/가치 모델의 상위 기준을 정의한다.

이 문서는 왜 CNN을 쓰는지, 어떤 입력과 출력을 가지는지, 학습 파이프라인과 어떤 방식으로 연결되는지를 설명한다. 세부 tensor shape와 모듈 계약은 `specs/training/cnn-model-spec.md`에서 다룬다.

## 적용 범위
- `src/training/`의 정책 모델
- `src/training/`의 CNN policy agent
- `policy_client`와 연결되는 예측 계층
- 향후 `trainer`의 모델 학습 루프
- self-play와 evaluator에서 사용하는 정책 추론

## 모델 선택 원칙
- 보드 크기가 고정된 `8 x 8`이므로 CNN을 기본 모델로 사용한다.
- 모델은 현재 상태에서의 행동 분포와 상태 가치를 함께 예측해야 한다.
- 입력 표현은 기존 `state_encoder`의 `4-plane 8 x 8` 규약을 기본값으로 유지한다.
- 출력 행동 공간은 `predict-api.md`의 전체 액션 공간 `65` 규약을 그대로 따른다.

## 모델 역할

### 정책 head
- 현재 상태에서 각 행동의 상대적 선호도를 출력한다.
- 출력 정의역은 `64`개 좌표와 `PASS`를 포함한 총 `65`개다.
- 유효하지 않은 행동은 후처리 또는 loss 계산 단계에서 마스킹해야 한다.
- 최종 선택 행동은 항상 유효 수 집합과 정합해야 한다.

### 가치 head
- 현재 상태가 `BLACK` 기준으로 얼마나 유리한지 스칼라 값으로 출력한다.
- 값 범위 기본값은 `[-1, 1]`이다.
- 의미는 self-play reward 관점과 일치해야 한다.
  - `BLACK` 승리 쪽이면 양수
  - `WHITE` 승리 쪽이면 음수
  - 균형 상태면 0 근처

## 입력 기준
- 기본 입력은 `state_encoder.encode_state()`가 만든 `4 x 8 x 8` 텐서다.
- plane 의미는 다음과 같다.
  - 현재 플레이어 돌
  - 상대 플레이어 돌
  - 빈 칸
  - 현재 플레이어가 `BLACK`인지 나타내는 plane
- 모델은 입력 보드 상태를 수정하면 안 된다.

## 출력 기준
- 정책 출력: 길이 `65`의 logit 또는 확률 분포
- 가치 출력: 스칼라 `state value`
- 정책 출력은 내부적으로 전체 액션 공간 기준으로 계산한다.
- 실제 행동 선택 시에는 action mask를 적용해 유효 행동만 남겨야 한다.
- `PASS`는 유효 수가 없을 때만 선택 가능해야 한다.

## self-play 연결 기준
- self-play에서는 정책 모델이 각 턴마다 행동 후보 점수를 제공한다.
- CNN 모델은 `CNNPolicyAgent` 같은 agent 래퍼를 통해 `run_match()`와 `run_self_play()`에 직접 연결될 수 있어야 한다.
- 선택 단계는 최소한 다음 순서를 따라야 한다.
  1. 상태 인코딩
  2. 모델 추론
  3. action mask 적용
  4. 행동 선택
  5. turn record 기록
- `policy_output`에는 가능하면 정책 분포와 선택 행동, 상태 가치가 함께 연결되어야 한다.
- self-play 결과의 `policy_black_version`, `policy_white_version`에는 실제 모델 버전이 기록되어야 한다.

## 체크포인트 기준
- CNN 모델은 체크포인트 파일에서 다시 로드 가능해야 한다.
- 체크포인트에는 가능하면 모델 파라미터와 모델 버전이 함께 포함되어야 한다.
- 체크포인트 로드 후 생성된 agent는 self-play에 바로 사용할 수 있어야 한다.

## 학습 기준
- 학습 데이터 단위는 `Episode`다.
- 정책 head는 행동 타깃을 학습한다.
- 가치 head는 최종 reward 또는 그에 준하는 value target을 학습한다.
- reward 관점은 기존 문서와 동일하게 `BLACK` 기준으로 고정한다.
- 완료 episode와 실패 episode를 구분해야 하며, 기본 학습 입력은 `completed` episode만 사용한다.

## 버전 관리 기준
- 정책 모델은 버전 문자열을 가져야 한다.
- self-play 메타데이터에는 black/white 정책 버전이 함께 기록되어야 한다.
- 모델 구조가 바뀌면 버전도 명시적으로 갱신해야 한다.

## 현재 구현과의 관계
- 현재 저장소에는 CNN 정책/가치 모델, `PolicyClient`, `CNNPolicyAgent`, 체크포인트 로드 경로가 있다.
- 기존 `RandomAgent`, `HeuristicAgent`는 기준선 agent로 유지할 수 있다.
- CNN 모델은 이 기준선 agent를 대체하거나 self-play 상대 정책으로 함께 사용할 수 있다.

## 비범위
- 구체 프레임워크 선택
- optimizer, scheduler, checkpoint 형식
- 분산 학습 또는 멀티 GPU 전략
- MCTS 결합 여부
