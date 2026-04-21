# CNN 정책 모델 명세

## 목적
이 문서는 오셀로 학습 파이프라인에 추가할 CNN 기반 정책/가치 모델의 최소 코드 계약을 정의한다.

## 관련 문서
- `docs/training/cnn-policy.md`
- `docs/training/predict-api.md`
- `specs/training/training-pipeline-spec.md`
- `specs/training/self-play-data-schema.md`

## 구현 대상
- `src/training/` 아래 CNN 모델 모듈
- 정책 추론 래퍼 또는 `policy_client` 확장
- `CNNPolicyAgent` 래퍼
- 체크포인트 로드 helper
- 향후 `trainer`의 모델 학습 루프

## 입력 계약
- 입력 텐서 shape 기본값은 `(batch, 4, 8, 8)`이다.
- 단건 추론은 `(4, 8, 8)` 또는 `(1, 4, 8, 8)`를 허용할 수 있으나, 내부 표준 shape는 batch-first다.
- 입력 channel 의미는 `state_encoder`와 동일해야 한다.
  - channel 0: 현재 플레이어 돌
  - channel 1: 상대 플레이어 돌
  - channel 2: 빈 칸
  - channel 3: 현재 플레이어가 `BLACK`인지 나타내는 plane
- 입력 dtype은 실수형이어야 한다.

## 출력 계약
- 모델 출력은 정책 head와 가치 head 두 개를 포함해야 한다.

### 정책 head
- 출력 shape는 `(batch, 65)`다.
- 값은 softmax 이전 logit을 기본값으로 한다.
- 인덱스 규약은 다음과 같다.
  - `0..63`: row-major 좌표
  - `64`: `PASS`

### 가치 head
- 출력 shape는 `(batch, 1)` 또는 `(batch,)`를 허용한다.
- 값 범위 기본값은 `[-1, 1]`이다.
- value는 `BLACK` 관점 reward와 정합해야 한다.

## 아키텍처 요구사항
- 입력 stem은 `4` 채널을 받는 convolution block이어야 한다.
- convolution trunk는 보드 공간 구조를 유지해야 한다.
- trunk 출력은 정책 head와 가치 head로 분기해야 한다.
- 정책 head는 최종적으로 `65`개 출력을 제공해야 한다.
- 가치 head는 최종적으로 스칼라 하나를 제공해야 한다.

## 최소 공개 인터페이스
- 모델 객체는 batch 입력을 받아 정책 logits와 value를 반환해야 한다.
- 예시:

```python
policy_logits, value = model(x)
```

- `policy_logits.shape[-1] == 65`여야 한다.
- `value`는 batch별 스칼라여야 한다.

### agent 래퍼
- CNN 모델은 `Agent` 프로토콜에 맞는 래퍼를 통해 self-play에 연결 가능해야 한다.
- 예시:

```python
agent = CNNPolicyAgent(model=model, version="cnn-v1", device="cpu")
action = agent.select_action(state, valid_moves)
```

- agent는 내부적으로 `PolicyClient` 또는 동등 계층을 사용해 행동을 선택해야 한다.
- agent의 `version`은 self-play episode 메타데이터와 연결되어야 한다.

## 추론 계약
- 추론 계층은 정책 logits에 action mask를 적용할 수 있어야 한다.
- 마스킹 후 행동 확률은 정규화 가능해야 한다.
- 최종 선택 행동은 항상 유효 수 집합 또는 `PASS` 규약을 따라야 한다.
- 유효 수가 있을 때 `PASS`를 선택하면 계약 위반이다.

## 학습 계약
- 정책 loss는 전체 액션 공간 `65` 기준으로 계산한다.
- 가치 loss는 최종 reward 또는 value target과 비교할 수 있어야 한다.
- 완료 episode만 기본 학습 입력으로 사용한다.
- 실패 episode는 기본 학습 배치에서 제외한다.

## 직렬화와 메타데이터
- 모델 버전 문자열은 self-play episode 메타데이터에 기록 가능해야 한다.
- 모델 구조 변경 시 버전 문자열도 함께 변경해야 한다.
- `policy_black_version`, `policy_white_version`에는 실제 정책 공급자의 모델 버전이 기록되어야 한다.

## 체크포인트 로드 계약
- 체크포인트에서 CNN 모델과 agent를 다시 만들 수 있어야 한다.
- 최소한 다음 두 형태 중 하나를 허용해야 한다.
  - 순수 `state_dict`
  - `model_state_dict`와 `model_version`을 포함한 dict
- 체크포인트 로드 후 생성된 agent는 self-play와 evaluator에 바로 연결 가능해야 한다.

## 현재 구현과의 연결 포인트
- `state_encoder.encode_state()` 출력은 이 모델의 기본 입력과 호환되어야 한다.
- `action_mask.build_action_mask()` 출력은 정책 head 출력과 직접 대응되어야 한다.
- `policy_client`는 향후 이 모델의 추론 결과를 `PolicyOutput` 형식으로 변환할 수 있어야 한다.

## 비범위
- convolution layer 수, kernel 크기, hidden width의 최종 수치
- optimizer 종류
- checkpoint 파일 포맷
- 배포용 추론 서버 프로토콜
