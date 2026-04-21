# Trainer 학습 루프 구현 작업 지시서

## 목적
현재 episode 요약 계층과 분리된 실제 모델 업데이트용 trainer 학습 루프를 설계하고 구현한다.

## 선행 입력
- `docs/training/trainer-loop.md`
- `docs/training/cnn-policy.md`
- `docs/training/checkpoint-policy.md`
- `specs/training/trainer-loop-spec.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/checkpoint-policy-spec.md`
- `agents/training-loop-agent.md`

## 필수 작업
- 실제 학습 루프와 현재 `TrainingReport` 요약 계층의 경계 정리
- 실제 학습 루프의 클래스 또는 메서드 이름을 기존 `Trainer`와 충돌하지 않게 정리
- iteration 단위 학습 실행 경로 정리
- `completed` episode 기반 학습 입력 경로 구현
- episode에서 turn 단위 학습 샘플을 만드는 경로 구현
- `action`을 전체 액션 공간 `65` 기준 정책 타깃으로 변환하는 경로 구현
- `reward`를 가치 타깃으로 연결하는 경로 구현
- in-memory `encoded_state` 사용 경로 또는 `state` 재인코딩 경로 구현
- 정책/value loss 계산 경로 구현
- step 또는 epoch 리포트 정의
- `resume_from_checkpoint` 또는 동등 재개 경로 구현
- `latest training checkpoint` 저장 연결
- evaluator 연동 평가 경로 구현
- 평가 기준에 따른 `best_black`, `best_white`, `best_balanced` 승격 경로 구현
- 색을 반반 바꾼 양방향 평가와 `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score` 계산 경로 구현
- `balanced_eval_score`의 평균/가중 평균 계산 규칙 구현
- 최소 단위 테스트 또는 shape 검증 테스트 작성

## 완료 조건
- 실제 모델 업데이트용 trainer 경로가 현재 요약 리포트 계층과 구분된다.
- 실제 학습 루프 이름과 현재 `Trainer.train()` 의미가 충돌하지 않는다.
- iteration, epoch, step의 역할이 구분된다.
- 실패 episode는 기본 학습 입력에서 제외된다.
- completed episode의 turn이 학습 샘플로 변환된다.
- `MOVE`와 `PASS`가 모두 65-공간 정책 타깃으로 변환 가능하다.
- 가치 타깃이 `BLACK` 기준 reward와 정합한다.
- 직렬화된 episode만 있을 때 필요한 재인코딩 경계가 구현 또는 문서로 드러난다.
- 정책/value 출력과 타깃 shape가 정합한다.
- trainer가 이전 checkpoint에서 학습 상태를 재개할 수 있다.
- `latest checkpoint` 저장과 `best_black`, `best_white`, `best_balanced` 승격이 구분된다.
- 평가가 최소한 `HeuristicAgent` 또는 현재 `best_black`, `best_white`, `best_balanced`와의 비교 기준을 가진다.
- 평가가 흑/백 배치를 바꾼 양방향 비교 기준을 가진다.
- `balanced_eval_score`가 양방향 승률 평균으로 계산되고, 필요 시 가중 평균 규칙을 따른다.
- `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`가 각각 검증 가능하다.
- 평가 실패가 있을 때 best 승격이 막히는지 검증 가능하다.
- 최소 테스트가 포함된다.
