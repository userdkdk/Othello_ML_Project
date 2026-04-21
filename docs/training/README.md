# Training Docs

`training` 영역은 엔진 규칙 위에서 데이터 생성과 평가를 정의한다.

현재 문서 기준에서 `training`의 중심 범위는 다음과 같다.
- self-play 실행
- episode 수집과 직렬화 경계
- 정책 추론 연계
- episode 집합 기반 리포트
- agent 대 agent 평가

주의:
- 현재 `trainer`는 모델 파라미터를 업데이트하는 학습 루프가 아니다.
- 현재 `trainer`는 수집된 episode 집합으로 `TrainingReport`를 만드는 요약 계층이다.
- 실제 파라미터 업데이트 학습 루프는 아직 비범위다.

## 읽는 순서
1. `self-play-spec.md`
2. `predict-api.md`
3. `rl-components.md`
4. `cnn-policy.md`
5. `training-pipeline.md`
6. `episode-storage.md`
7. `checkpoint-policy.md`
8. `trainer-loop.md`
9. `training-ops.md`
10. `training-docker.md`
11. `training-run-guide.md`
12. `implementation-priority.md`

## 파일 역할
- `self-play-spec.md`
  - self-play 범위, 보상 기준, 시작 상태 제약
- `predict-api.md`
  - `(row, col)` / `PASS` 행동 표현과 정책 분포 규약
- `rl-components.md`
  - match runner, agent, encoder, evaluator 등 구성요소 책임
- `cnn-policy.md`
  - CNN 기반 정책/가치 모델 상위 기준
- `training-pipeline.md`
  - 현재 구현 기준 학습 파이프라인 흐름
- `episode-storage.md`
  - episode 파일 저장 기준과 직렬화 경계
- `checkpoint-policy.md`
  - 모델 체크포인트 저장/로드 기준
- `trainer-loop.md`
  - 향후 실제 trainer 학습 루프 기준
- `training-ops.md`
  - 학습 제어, 대시보드 노출 상태, checkpoint 비교 기준
- `training-docker.md`
  - training 전용 Docker 분리 기준
- `training-run-guide.md`
  - training Docker 실행 방법
  - 누적 학습 resume 사용법
  - `run-training.sh`, `train-resume.sh` 사용법
- `implementation-priority.md`
  - training 구현 작업 우선순위와 선후관계 기준

## 현재 범위 요약
- `run_self_play()`
  - self-play 실행과 `SelfPlayResult` 반환
- `Trainer.train(episodes)`
  - episode 집합 기반 `TrainingReport` 생성
- `Evaluator.evaluate(...)`
  - 별도 평가 실행 기반 `EvaluationReport` 생성

## 저장 경계
- 메모리상 `TurnRecord`는 `valid_moves`, `action_mask`, `encoded_state`를 포함할 수 있다.
- 기본 직렬화 출력은 `specs/training/self-play-data-schema.md`를 따른다.
- 현재 기본 직렬화 출력에는 `encoded_state`가 포함되지 않는다.
