# Checkpoint 명세 작성 작업 지시서

## 목적
`training` 계층의 체크포인트 저장/로드와 버전 해석 계약을 구현 직전 수준으로 명세한다.

## 선행 입력
- `docs/training/checkpoint-policy.md`
- `docs/training/cnn-policy.md`
- `specs/training/cnn-model-spec.md`
- `agents/governance-agent.md`

## 필수 작업
- 체크포인트 payload 기본 키 정의
- `model_state_dict`/`state_dict`/순수 state dict 해석 우선순위 정의
- 호출자 인자와 checkpoint 메타데이터 우선순위 정의
- 버전 해석 규칙 정의
- 오류 및 실패 규약 정의

## 출력 파일
- `specs/training/checkpoint-policy-spec.md`

## 완료 조건
- 구현자가 loader의 우선순위와 실패 조건을 해석 없이 구현할 수 있다.
- 버전 해석 경로가 명확하다.
- 순수 state dict 판별 규칙이 문서화되어 있다.
- 저장 payload 최소 키와 선택 키가 정의되어 있다.
