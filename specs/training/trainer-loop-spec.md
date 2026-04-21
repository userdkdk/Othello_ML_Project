# Trainer 학습 루프 명세

## 목적
이 문서는 향후 실제 모델 업데이트를 수행하는 trainer 학습 루프의 최소 계약을 정의한다.

## 관련 문서
- `docs/training/trainer-loop.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/self-play-data-schema.md`
- `specs/training/checkpoint-policy-spec.md`

## 구현 대상
- 실제 모델 업데이트용 trainer 계층
- 학습 step/epoch 리포트 구조
- iteration 단위 학습/평가/승격 경로

## 권장 분리 계약
- 기존 `src/training/trainer.py`의 `Trainer.train()`은 요약 리포트 경로로 유지하는 것을 기본값으로 한다.
- 실제 모델 업데이트 경로는 별도 클래스 또는 별도 메서드로 분리하는 것을 권장한다.

## 입력 계약
- 기본 입력은 `completed` episode iterable이어야 한다.
- 실패 episode는 기본 학습 배치에서 제외되어야 한다.
- 정책 타깃은 전체 액션 공간 `65` 기준과 정합해야 한다.
- 학습 샘플 단위는 turn record여야 한다.
- 각 샘플은 최소한 하나의 입력 상태와 하나의 정책 타깃, 하나의 가치 타깃으로 물질화 가능해야 한다.
- in-memory 입력 경로에서는 `TurnRecord.encoded_state`를 직접 사용할 수 있어야 한다.
- 직렬화된 episode 입력 경로에서는 `state`에서 다시 인코딩하는 경로를 허용해야 한다.
- trainer는 필요 시 `resume_from_checkpoint` 또는 동등 입력으로 이전 학습 상태를 복원할 수 있어야 한다.

## 정책 타깃 계약
- 기본 정책 타깃은 각 turn의 실제 실행 행동 `action`이다.
- 정책 타깃은 길이 `65`의 one-hot 벡터 또는 동등 인덱스 표현으로 변환 가능해야 한다.
- `MOVE` 행동은 row-major 좌표 인덱스를 사용해야 한다.
- `PASS` 행동은 인덱스 `64`를 사용해야 한다.

## 가치 타깃 계약
- 기본 가치 타깃은 각 turn의 `reward`다.
- 가치 타깃은 `BLACK` 관점 reward와 정합해야 한다.
- completed episode의 turn마다 값이 존재하거나, 학습 직전 채워질 수 있어야 한다.

## 출력 계약
- 학습 루프는 최소한 학습 리포트 객체 또는 dict를 반환할 수 있어야 한다.
- 필요 시 갱신된 모델 또는 체크포인트 경로를 함께 반환할 수 있어야 한다.
- 기본 학습 리포트는 최소한 다음 항목을 표현 가능해야 한다.
  - iteration 수
  - epoch 수
  - step 수
  - 사용 샘플 수
  - 평균 policy loss
  - 평균 value loss
- 누적 학습을 지원하는 경우 리포트는 가능하면 다음 항목도 표현 가능해야 한다.
  - `resumed_from`
  - `total_iterations`
  - `total_epochs`
  - `total_steps`
  - `latest_checkpoint_path`
  - `promoted_tracks`

## resume 계약
- `resume` 경로는 최소한 다음 상태와 연결 가능해야 한다.
  - 모델 파라미터
  - 모델 버전
  - 누적 iteration/epoch/step 메타데이터
  - 필요 시 optimizer state
- `continue` 경로는 모델 파라미터만 불러와 새 학습 세션을 시작할 수 있어야 한다.
- `resume_from_checkpoint`가 주어졌는데 trainer가 요구하는 학습 상태가 부족하면 명시적으로 실패해야 한다.

## evaluation 계약
- iteration 종료 후 trainer는 evaluator 또는 동등 계층과 연결되어 평가를 실행할 수 있어야 한다.
- 기본 평가 상대는 최소한 다음 중 일부를 지원할 수 있어야 한다.
  - `HeuristicAgent`
  - 현재 `best_black`, `best_white`, `best_balanced` checkpoint에서 로드한 agent
  - 필요 시 `RandomAgent`
- 기본 평가 산출물은 다음 항목과 정합해야 한다.
  - `games`
  - `black_win_rate`
  - `white_win_rate`
  - `draw_rate`
  - `failures`
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- 후보 모델과 비교 대상 모델의 평가는 색을 반반으로 나누어 양방향으로 수행하는 것을 기본값으로 한다.
- trainer는 최소한 다음 파생 값을 계산 또는 기록할 수 있어야 한다.
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- `balanced_eval_score`는 흑 배치 평가와 백 배치 평가의 평균 승률로 해석할 수 있어야 한다.
- 양방향 평가 게임 수가 같으면 단순 평균을 사용해야 한다.
- 양방향 평가 게임 수가 다르면 가중 평균 규칙을 사용할 수 있어야 한다.
- 학습 loss는 checkpoint 승격의 단독 기준으로 사용하면 안 된다.

## promotion 계약
- 각 iteration 종료 후 현재 상태를 `latest training checkpoint`로 저장할 수 있어야 한다.
- `best_black`, `best_white`, `best_balanced` 승격은 각 평가 기준을 만족할 때만 수행해야 한다.
- 권장 기본 승격 규칙은 다음 판단을 표현 가능해야 한다.
  - 평가 실패 대국이 없는지
  - `HeuristicAgent` 대비 최소 기준을 만족하는지
  - 현재 best 계열 agent 대비 최소 기준을 만족하는지
- 각 best 트랙 비교 기준은 다음과 같이 해석할 수 있어야 한다.
  - `best_black`: 현재 흑 성능 최고 모델과 비교
  - `best_white`: 현재 백 성능 최고 모델과 비교
  - `best_balanced`: 현재 흑/백 균형 성능 최고 모델과 비교
- 기본 예시 임계값은 다음과 같다.
  - `failure_rate == 0`
  - `vs HeuristicAgent black_side_win_rate >= 0.70`
  - `vs HeuristicAgent white_side_win_rate >= 0.70`
  - `vs HeuristicAgent balanced_eval_score >= 0.70`
  - `vs current best_black black_side_win_rate >= 0.55`
  - `vs current best_white white_side_win_rate >= 0.55`
  - `vs current best_balanced balanced_eval_score >= 0.55`
- 평가 게임 수와 임계값은 설정으로 조정 가능해야 하며, 기본값은 추적 가능해야 한다.

## 분리 계약
- 현재 `TrainingReport` 요약 계층과 실제 모델 업데이트 계층은 명시적으로 구분되어야 한다.
- 기존 `Trainer.train()`의 의미를 변경한다면 문서/테스트/호출부를 함께 갱신해야 한다.

## 검증 계약
- 완료 episode만 사용되는지 검증 가능해야 한다.
- 정책 출력 shape와 가치 타깃 shape가 모델 계약과 호환되어야 한다.
- 체크포인트 저장 시 버전 메타데이터가 연결 가능해야 한다.
- action을 65-공간 정책 타깃으로 변환하는 규칙이 검증 가능해야 한다.
- 직렬화된 episode 입력에서 재인코딩 경로가 필요하다면 그 경계가 테스트 또는 문서로 드러나야 한다.
- `resume` 시 누적 iteration/epoch/step이 복원되는지 검증 가능해야 한다.
- 평가 결과에 따라 `latest` 저장과 3트랙 `best` 승격이 분리되는지 검증 가능해야 한다.
- 양방향 색 평가와 평균/가중 평균 기반 `balanced_eval_score` 계산 규칙이 검증 가능해야 한다.

## 비범위
- optimizer 하이퍼파라미터 기본값 고정
- GPU 전략
