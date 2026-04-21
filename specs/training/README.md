# Training Specs

## 파일 역할
- `self-play-data-schema.md`
  - episode/turn 저장 스키마
  - reward, action index, metadata 규약
  - 메모리상 필드와 기본 직렬화 출력의 경계
- `rl-components-spec.md`
  - `src/training` 공개 모듈과 최소 공개 API
- `training-pipeline-spec.md`
  - self-play 실행 순서와 `SelfPlayResult`/`TrainingReport`/`EvaluationReport` 생성 경로 계약
- `episode-storage-spec.md`
  - episode 저장기 입력/출력/오류 계약
- `checkpoint-policy-spec.md`
  - 체크포인트 저장/로드와 버전 해석 계약
- `trainer-loop-spec.md`
  - 실제 모델 업데이트용 trainer 학습 루프 계약
- `training-ops-spec.md`
  - 학습 세션 제어, 대시보드 상태 스냅샷, checkpoint 비교 계약
- `cnn-model-spec.md`
  - CNN 정책/가치 모델 입력, 출력, head 계약
- `training-docker-spec.md`
  - training 전용 Docker 파일과 실행 계약
- `implementation-priority-spec.md`
  - training 구현 task의 권장 순서와 의존 관계 계약
