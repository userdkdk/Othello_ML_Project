# 학습 파이프라인 구현 작업 지시서

## 목적
현재 `training` 계층의 self-play 실행, episode 수집, 리포트 생성 흐름을 문서와 코드 기준에 맞게 정리하고 확장 가능한 학습 파이프라인 단위로 고정한다.

## 선행 입력
- `docs/training/training-pipeline.md`
- `docs/training/self-play-spec.md`
- `docs/training/rl-components.md`
- `docs/training/predict-api.md`
- `specs/training/training-pipeline-spec.md`
- `specs/training/self-play-data-schema.md`
- `specs/training/rl-components-spec.md`
- `agents/training-loop-agent.md`

## 필수 작업
- `run_self_play()`와 `run_match()`의 호출 경로를 현재 문서와 일치시키기
- `Episode`, `TurnRecord`, `SelfPlayResult`의 공개 산출물 정리
- `Trainer`가 episode 집합 기반 `TrainingReport`를 생성하도록 유지 또는 정리
- `Evaluator`가 agent 대 agent 평가 실행 결과를 리포트로 반환하도록 유지 또는 정리
- self-play 결과와 trainer/evaluator 출력의 관계를 코드와 테스트에서 분명히 하기
- 실패 episode와 완료 episode의 집계 규칙 검증
- 직렬화 기본 경로와 메모리상 필드의 차이 검증
- 최소 단위 테스트 또는 통합 테스트 보강

## 완료 조건
- `run_self_play()`의 직접 반환값이 `SelfPlayResult`로 명확하다.
- `Trainer.train()`은 episode iterable을 받아 `TrainingReport`를 반환한다.
- `Trainer`가 현재 범위에서 모델 파라미터 업데이트 루프가 아니라는 점이 문서와 코드에 일관되게 드러난다.
- `Evaluator.evaluate()`는 agent와 게임 수를 받아 `EvaluationReport`를 반환한다.
- 실패 episode는 `failures`에 집계되지만 승패 통계에는 포함되지 않는다.
- `TurnRecord.encoded_state`가 메모리상 필드이고 기본 직렬화 출력에는 포함되지 않는다는 점이 코드와 테스트에서 드러난다.
- `policy_black_version`, `policy_white_version`, 최종 reward, failure 정보가 파이프라인 산출물에 일관되게 연결된다.
- 현재 범위가 모델 파라미터 업데이트 학습 루프를 포함하지 않는다는 점이 유지된다.
