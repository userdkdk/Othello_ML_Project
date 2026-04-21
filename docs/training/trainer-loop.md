# Trainer 학습 루프 기준

## 목적
이 문서는 현재 `TrainingReport` 생성기와 별개로, 향후 실제 모델 파라미터 업데이트를 수행하는 trainer 학습 루프의 상위 기준을 정의한다.

현재 구현의 `Trainer`는 episode 집합을 요약하는 계층이다. 이 문서는 이후 실제 학습 루프를 추가할 때 현재 리포트 계층과 충돌하지 않도록 경계를 먼저 고정한다.

## 적용 범위
- episode 기반 학습 배치 구성
- 정책 loss, 가치 loss 계산
- iteration 단위 학습 실행
- 평가 실행과 checkpoint 승격 판단
- 체크포인트 저장 시점
- 학습 리포트와 모델 업데이트 분리

## 경계 기준
- 현재 `Trainer.train(episodes)`의 의미를 바로 덮어쓰면 안 된다.
- 실제 학습 루프를 도입할 때는 기존 요약 리포트 계층과 명시적으로 구분해야 한다.
- 권장 기본값은 기존 `Trainer`를 그대로 두고, 실제 모델 업데이트는 별도 클래스 또는 별도 메서드로 분리하는 것이다.
- 기본 권장 예시는 다음 둘 중 하나다.
  - `TrainingReporter` 같은 요약 전용 이름으로 기존 계층을 분리
  - `ModelTrainer` 또는 `PolicyValueTrainer` 같은 새 학습 루프 계층 추가
- `누적 학습`은 단순히 이전 가중치를 다시 불러오는 동작이 아니라, 평가 기준에 따라 `latest checkpoint`와 여러 `best checkpoint`를 구분해 관리하는 반복 학습 루프를 의미한다.
- 이 문서에서는 다음 용어를 구분한다.
  - `resume`: 같은 학습 세션을 이어서 진행하는 재개 경로
  - `continue`: 이전 모델을 초기값으로만 사용하고 새 학습 세션을 시작하는 경로

## iteration 기준
- trainer 학습 루프의 기본 운영 단위는 `epoch`만이 아니라 `iteration`이다.
- 권장 기본 iteration 순서는 다음과 같다.
  1. self-play 데이터 생성
  2. 학습 입력 구성
  3. 모델 업데이트 수행
  4. `latest training checkpoint` 저장
  5. evaluator 기반 평가 실행
  6. 기준 충족 시 `best_black`, `best_white`, `best_balanced` checkpoint 승격
- `epoch`는 한 iteration 내부에서 같은 샘플 집합을 반복 학습하는 단위로 해석한다.

## 샘플 단위 기준
- 학습 루프의 기본 샘플 단위는 `episode`가 아니라 `completed episode` 안의 개별 `turn record`다.
- 학습 배치는 여러 turn record를 묶어 `(batch, 4, 8, 8)` 입력으로 구성한다.
- 실패 episode의 turn record는 기본 학습 배치에서 제외한다.

## 입력 기준
- 기본 입력은 `completed` episode 집합이다.
- 실패 episode는 기본 학습 입력에서 제외한다.
- 정책 타깃과 가치 타깃은 `self-play-data-schema` 및 `cnn-model-spec`과 정합해야 한다.
- 기본 입력에서 각 turn은 최소한 다음 정보를 제공할 수 있어야 한다.
  - 상태 표현
  - 최종 선택 행동
  - 최종 reward 또는 value target

## 입력 물질화 기준
- 가장 직접적인 학습 입력은 메모리상 `TurnRecord.encoded_state`다.
- 기본 파일 직렬화 출력에는 `encoded_state`가 없으므로, 파일에서 다시 학습할 때는 `state`를 바탕으로 재인코딩 경로가 필요하다.
- 따라서 학습 루프는 최소한 다음 둘 중 하나와 연결 가능해야 한다.
  - in-memory episode 경로
  - 저장된 state를 다시 `state_encoder`로 변환하는 경로

## 정책 타깃 기준
- 정책 타깃 기본값은 각 turn의 실제 실행 행동 `action`이다.
- 정책 타깃은 전체 액션 공간 `65` 기준 one-hot 또는 동등 인덱스 표현으로 해석할 수 있어야 한다.
- 좌표 행동은 row-major 인덱스로 변환한다.
- `PASS` 행동은 인덱스 `64`로 변환한다.
- 유효 수가 있는 상태에서 `PASS`를 정책 타깃으로 사용하면 안 된다.

## 가치 타깃 기준
- 가치 타깃 기본값은 각 turn에 연결된 최종 `reward`다.
- 가치 타깃 관점은 `BLACK` 기준을 유지해야 한다.
- 기본값은 completed episode의 모든 turn에 동일 reward를 연결하는 현재 파이프라인과 정합해야 한다.

## 출력 기준
- 학습 루프는 최소한 다음 산출물 중 일부를 제공할 수 있어야 한다.
  - loss 요약
  - step 또는 epoch 단위 리포트
  - 갱신된 모델 파라미터
  - 체크포인트 저장 트리거
- 기본 학습 리포트에는 가능하면 다음 필드를 포함한다.
  - `iteration`
  - `epochs`
  - `steps`
  - `samples`
  - `policy_loss`
  - `value_loss`
  - `eval_score` 또는 동등 평가 메타데이터
  - `checkpoint_path` 또는 동등 메타데이터
  - `resumed_from` 또는 동등 resume 메타데이터

## resume 기준
- `resume` 경로는 최소한 이전 학습 상태를 다시 이어서 진행할 수 있어야 한다.
- `resume` 시 trainer는 최소한 다음 정보와 연결 가능해야 한다.
  - 모델 파라미터
  - 모델 버전
  - 누적 iteration/epoch/step 메타데이터
  - 필요 시 optimizer state
- `continue` 경로는 모델 파라미터만 불러와 새 학습 세션을 시작할 수 있으며, 이전 optimizer state 복원은 필수가 아니다.

## 평가 기준
- 누적 학습에서는 학습 loss와 별개로 "이전보다 강해졌는지"를 판정하는 평가 기준이 필요하다.
- checkpoint 승격 여부는 `policy_loss`, `value_loss` 같은 내부 학습 지표만으로 결정하면 안 된다.
- 기본 평가 상대는 다음 세 축 중 일부를 사용한다.
  - `RandomAgent`
  - `HeuristicAgent`
  - 현재 `best_black`, `best_white`, `best_balanced` checkpoint에서 로드한 agent
- 기본 운영 기준에서는 `HeuristicAgent`와 현재 best 계열 agent를 주요 평가 상대로 사용한다.
- `RandomAgent` 평가는 smoke check 성격으로만 두고, 기본 best 승격의 주 기준으로 사용하지 않는다.
- 기본 평가 리포트에는 최소한 다음 항목이 표현 가능해야 한다.
  - `games`
  - `black_win_rate`
  - `white_win_rate`
  - `draw_rate`
  - `failures`
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- 여기서 `black_win_rate`, `white_win_rate`는 전체 평가 대국 결과 기준 승률이고, `black_side_win_rate`, `white_side_win_rate`는 후보 모델이 각각 흑/백으로 배치되었을 때의 승률을 뜻한다.
- trainer는 평가 리포트에서 최소한 다음 파생 판단이 가능해야 한다.
  - 기준선 상대 대비 승률
  - 현재 best 계열 상대 대비 승률
  - 색을 바꿔가며 측정한 양방향 평균 승률
  - 후보 모델이 흑으로 플레이했을 때의 승률
  - 후보 모델이 백으로 플레이했을 때의 승률
  - 실패율
  - 무승부율
- 후보 모델과 비교 대상 모델의 평가는 색을 반반으로 나누어 수행하는 것을 기본값으로 둔다.
- 기본 평가 점수는 다음 세 가지로 나눈다.
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- `balanced_eval_score`는 양방향 평가 승률의 평균값이다.
- 기본 운영에서는 다음 세 분야의 최고 모델을 각각 유지할 수 있어야 한다.
  - `best_black`
  - `best_white`
  - `best_balanced`
- `balanced_eval_score`는 기본적으로 흑 평가 게임 수와 백 평가 게임 수를 동일하게 맞춘 상태에서 계산한다.
- 만약 양방향 평가 게임 수가 다르면 `balanced_eval_score`는 가중 평균 규칙으로 계산해야 한다.

## checkpoint 승격 기준
- 각 iteration 종료 후 현재 학습 상태는 `latest training checkpoint`로 저장할 수 있어야 한다.
- `best_black`, `best_white`, `best_balanced` 승격은 각 평가 기준을 만족할 때만 수행해야 한다.
- 권장 기본 승격 규칙은 다음과 같다.
  - 평가 실행 중 실패 대국이 없어야 한다.
  - `HeuristicAgent` 대비 최소 기준을 만족해야 한다.
  - 현재 best 계열 agent 대비 최소 기준을 만족해야 한다.
- 각 best 트랙 비교 기준은 다음과 같이 해석한다.
  - `best_black`: 현재 흑 성능 최고 모델과 비교
  - `best_white`: 현재 백 성능 최고 모델과 비교
  - `best_balanced`: 현재 흑/백 균형 성능 최고 모델과 비교
- 기본 예시 기준은 다음과 같다.
  - `failure_rate == 0`
  - `vs HeuristicAgent black_side_win_rate >= 0.70`
  - `vs HeuristicAgent white_side_win_rate >= 0.70`
  - `vs HeuristicAgent balanced_eval_score >= 0.70`
  - `vs current best_black black_side_win_rate >= 0.55`
  - `vs current best_white white_side_win_rate >= 0.55`
  - `vs current best_balanced balanced_eval_score >= 0.55`
- 평가 게임 수와 승격 임계값은 설정으로 조정할 수 있어야 하지만, 기본값은 문서나 설정에서 추적 가능해야 한다.

## 품질 기준
- 행동 공간은 전체 액션 공간 `65` 기준을 따른다.
- reward 관점은 `BLACK` 기준을 유지한다.
- 학습 루프는 self-play 스키마와 정책 버전 체계를 깨면 안 된다.
- 현재 요약용 `TrainingReport`와 실제 학습 리포트는 같은 의미로 섞어 쓰면 안 된다.
- `latest checkpoint`와 여러 `best checkpoint`의 목적이 섞이면 안 된다.

## 비범위
- optimizer 최종 선택
- scheduler 최종 선택
- 분산 학습
