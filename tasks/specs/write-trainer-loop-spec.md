# Trainer 학습 루프 명세 작성 작업 지시서

## 목적
현재 요약용 `Trainer`와 분리된 실제 모델 업데이트용 trainer 학습 루프 계약을 구현 직전 수준으로 명세한다.

## 선행 입력
- `docs/training/trainer-loop.md`
- `docs/training/cnn-policy.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/self-play-data-schema.md`
- `agents/governance-agent.md`

## 필수 작업
- 현재 `Trainer.train()`과 실제 학습 루프 경계 정의
- turn 단위 학습 샘플 계약 정의
- policy/value target 생성 규칙 정의
- in-memory 입력과 재인코딩 입력 경계 정의
- step/epoch 리포트 최소 필드 정의

## 출력 파일
- `specs/training/trainer-loop-spec.md`

## 완료 조건
- 구현자가 새 학습 루프 API와 현재 요약 리포트 계층을 혼동하지 않도록 경계가 고정되어 있다.
- turn 단위 샘플과 65-action 정책 타깃 규칙이 명확하다.
- 가치 타깃이 `BLACK` 기준 reward와 연결되는 방식이 문서화되어 있다.
- 학습 리포트 최소 필드가 정의되어 있다.
