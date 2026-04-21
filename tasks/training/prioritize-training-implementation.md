# Training 구현 우선순위 정리 작업 지시서

## 목적
`training` 영역의 구현 작업들을 선후관계와 리스크 기준으로 정렬하고, 실제 구현 착수 순서를 문서로 고정한다.

## 선행 입력
- `docs/training/implementation-priority.md`
- `docs/training/training-pipeline.md`
- `specs/training/implementation-priority-spec.md`
- `tasks/training/implement-training-pipeline.md`
- `tasks/training/implement-episode-storage.md`
- `tasks/training/implement-cnn-policy-model.md`
- `tasks/training/implement-checkpoint-policy.md`
- `tasks/training/implement-trainer-loop.md`
- `tasks/training/implement-training-ops.md`
- `tasks/training/implement-training-docker.md`
- `agents/training-loop-agent.md`

## 필수 작업
- 구현 작업들의 기본 순서 정의
- 각 단계의 선행 이유와 의존 관계 정리
- 병렬 가능 범위와 비권장 순서 정리
- 가장 먼저 착수할 작업과 후속 작업 기준 정리

## 완료 조건
- 구현자가 어떤 task부터 시작해야 할지 해석 없이 판단할 수 있다.
- `trainer-loop`가 가장 뒤인 이유가 문서화되어 있다.
- `training-ops`가 어떤 선행 작업 뒤에 오는지 설명 가능하다.
- 저장기, CNN 모델, checkpoint, trainer-loop, training-ops, Docker의 상대적 순서가 설명 가능하다.
- 현재 `training` 범위와 향후 학습 루프 범위가 혼동되지 않는다.
