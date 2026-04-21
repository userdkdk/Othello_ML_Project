# CNN 정책 모델 구현 작업 지시서

## 목적
오셀로 학습 파이프라인에 연결할 CNN 기반 정책/가치 모델과 최소 추론 계층을 구현한다.

## 선행 입력
- `docs/training/cnn-policy.md`
- `docs/training/predict-api.md`
- `docs/training/training-pipeline.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/training-pipeline-spec.md`
- `specs/training/self-play-data-schema.md`
- `agents/training-data-agent.md`

## 필수 작업
- CNN 정책/가치 모델 모듈 구현
- `4 x 8 x 8` 입력과 `65` 액션 출력 규약 구현
- 정책 head와 가치 head 분기 구현
- action mask를 반영한 추론 계층 구현
- `policy_client` 또는 동등 계층과 모델 추론 연결
- `CNNPolicyAgent` 또는 동등 agent 래퍼 구현
- 체크포인트 로드 경로 구현
- self-play `policy_output` 기록 연결
- 모델 버전 문자열 정의
- 단건 추론과 배치 추론 입력 처리
- 최소 단위 테스트 작성

## 완료 조건
- 모델이 batch 입력을 받아 정책 logits와 상태 가치를 반환한다.
- 정책 head 출력 차원은 전체 액션 공간 `65`와 일치한다.
- 가치 head는 batch별 스칼라를 반환한다.
- 유효 수가 있을 때 `PASS`를 최종 선택하지 않는다.
- action mask 적용 후 선택 행동이 `predict-api.md` 계약과 일치한다.
- `state_encoder` 출력과 모델 입력 shape가 호환된다.
- 모델 버전이 self-play 메타데이터에 연결 가능한 형태로 정의되어 있다.
- 체크포인트에서 CNN agent를 다시 만들 수 있다.
- CNN agent를 `run_self_play()`에 직접 연결할 수 있다.
- self-play 결과의 `policy_output`과 정책 버전 메타데이터가 실제 모델 경로와 정합한다.
- 최소한 shape 검증, 마스킹 검증, `PASS` 규약 검증, 체크포인트 로드 검증 테스트가 포함된다.
