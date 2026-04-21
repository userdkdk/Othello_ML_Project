# 학습 파이프라인 개요

## 목적
이 문서는 현재 저장소 구현 기준으로 오셀로 학습 파이프라인이 어떤 단계로 동작하는지 설명한다.

이 문서의 범위는 `src/training/`의 실제 코드 흐름이다. 이상적인 강화학습 전체 구조보다 현재 구현되어 있는 self-play, episode 수집, 집계, 평가 흐름을 우선 설명한다.
즉 이 문서는 trainer-loop와 checkpoint의 최종 설계 문서가 아니라, 현재 구현 상태를 설명하는 문서다.

## 관련 경로
- 엔진 규칙: `docs/engine/othello-rules.md`
- self-play 기준: `docs/training/self-play-spec.md`
- 예측 계약: `docs/training/predict-api.md`
- 구성요소 기준: `docs/training/rl-components.md`
- 구현 코드: `src/training/`

## 현재 파이프라인 한눈에 보기
1. 표준 초기 상태에서 새 대국을 시작한다.
2. 현재 플레이어의 유효 수를 계산한다.
3. agent 또는 정책 계층이 행동을 선택한다.
4. 행동 직전 상태를 학습 입력 형태로 인코딩한다.
5. action mask와 함께 turn record를 `Episode`에 저장한다.
6. 선택한 행동을 엔진에 적용한다.
7. 종료 시 최종 승패와 보상을 episode 전체에 연결한다.
8. 여러 판을 반복 실행해 self-play 결과와 통계를 만든다.
9. 필요하면 수집된 episode 집합으로 `TrainingReport`를 만든다.
10. 필요하면 별도 agent 대 agent 평가 실행으로 `EvaluationReport`를 만든다.

## 단계별 흐름

### 1. 대국 시작
- 진입점은 `src/training/self_play_runner.py`의 `run_self_play()`다.
- 각 게임은 `src/training/match_runner.py`의 `run_match()`로 실행된다.
- `run_match()`는 `engine.game_engine.create_new_game()`를 호출해 표준 초기 상태를 만든다.
- 현재 구현은 기본적으로 표준 시작 상태만 사용한다.

### 2. 턴 루프와 행동 선택
- 매 턴마다 `get_valid_moves_for_current_player()`로 유효 수를 계산한다.
- 현재 플레이어가 `BLACK`이면 black agent, `WHITE`면 white agent가 행동을 선택한다.
- agent 호출 형태는 `select_action(state.clone(), valid_moves, rng)`다.
- CNN 모델을 쓰는 경우 `CNNPolicyAgent`가 `PolicyClient`를 통해 모델 추론을 수행한다.
- agent는 유효 수가 있을 때는 그중 하나를 반환해야 한다.
- `PASS`는 유효 수가 없을 때만 허용된다.

### 3. 상태 인코딩
- 행동을 엔진에 적용하기 전에 현재 상태를 학습 입력으로 변환한다.
- `src/training/state_encoder.py`의 `encode_state()`는 기본적으로 `4 x 8 x 8` 입력을 만든다.
- plane 구성은 다음과 같다.
  - 현재 플레이어 돌
  - 상대 플레이어 돌
  - 빈 칸
  - 현재 플레이어가 `BLACK`인지 나타내는 plane

### 4. 액션 마스크 생성
- `src/training/action_mask.py`의 `build_action_mask()`가 길이 `65`의 마스크를 만든다.
- 인덱스 `0..63`은 보드 좌표를 row-major로 표현한다.
- 인덱스 `64`는 `PASS`다.
- 유효 수가 있으면 해당 좌표만 `1`이고, 유효 수가 없으면 `PASS`만 `1`이다.

### 5. 턴 기록 수집
- 각 턴은 `src/training/episode.py`의 `TurnRecord`로 저장된다.
- 현재 구현의 turn record에는 다음 정보가 들어간다.
  - 턴 인덱스
  - 행동 주체 플레이어
  - 상태 스냅샷
  - 선택 행동
  - 유효 수 목록
  - action mask
  - encoded state
  - policy output
  - reward 슬롯
- 이 turn record들은 한 판 단위의 `Episode`에 누적된다.
- 다만 현재 `Episode.to_dict()` 직렬화 결과에는 `encoded_state`가 포함되지 않는다.
- 따라서 encoded tensor는 현재 메모리상 turn record에는 존재하지만, 기본 dict 출력이나 저장 스키마에는 직접 남지 않는다.
- 반면 `policy_output`은 기본 직렬화 결과에 포함된다.

### 6. 엔진 적용과 실패 처리
- 선택 행동이 `PASS`면 `pass_turn()`을 호출한다.
- 좌표 행동이면 `apply_move()`를 호출한다.
- agent가 유효하지 않은 행동을 반환하면 엔진 결과는 실패가 된다.
- 이 경우 episode는 `failed` 상태로 마감되고, 실패 원인과 실패 턴 인덱스를 기록한다.

### 7. 종료 후 보상 부여
- 게임 종료 시 `Episode.finalize()`가 승패를 기록한다.
- 현재 보상 기준은 `BLACK` 관점으로 고정되어 있다.
  - `BLACK` 승리: `+1.0`
  - 무승부: `0.0`
  - `WHITE` 승리: `-1.0`
- 현재 구현은 최종 보상을 모든 turn record의 `reward`에 동일하게 채운다.

### 8. 다수 대국 실행
- `run_self_play()`는 `num_games`만큼 `run_match()`를 반복 호출한다.
- 각 게임의 시드는 `seed + game_index` 방식으로 만든다.
- 반환 결과는 `SelfPlayResult`이며 다음 정보를 포함한다.
  - `episodes`
  - `statistics`
  - `failures`

### 9. 집계와 평가
- `src/training/statistics.py`는 승, 패, 무, 평균 수순 같은 집계값을 관리한다.
- `src/training/trainer.py`의 `Trainer`는 현재 모델 파라미터를 업데이트하지 않고, 이미 수집된 episode 집합을 입력으로 받아 학습 리포트를 만든다.
- `src/training/evaluator.py`의 `Evaluator`는 episode 집합을 직접 받지 않고, agent와 게임 수를 입력으로 받아 내부에서 `run_self_play()`를 다시 실행한 뒤 승률, 무승부율, 실패 수를 계산한다.

## 구성요소별 책임

### `agents`
- `RandomAgent`
  - 유효 수 중 무작위 선택
- `HeuristicAgent`
  - 코너, 엣지, 뒤집기 수를 기준으로 점수화해 행동 선택

### `policy_client`
- 정책 추론 계층을 맡는다.
- agent 기반 균등 분포 출력과 CNN 모델 기반 분포 출력을 모두 지원한다.
- 모델 기반 추론 시 action mask를 적용해 최종 행동과 상태 가치를 만든다.

### `cnn_policy_agent`
- CNN 모델을 `Agent` 프로토콜에 맞게 감싸는 래퍼다.
- `run_match()`와 `run_self_play()`에 직접 연결할 수 있다.
- 체크포인트 로드 경로를 통해 생성될 수 있다.

### `episode`
- 한 판 대국의 학습용 기록 단위다.
- 완료 대국과 실패 대국을 구분한다.
- 메타데이터, 턴 기록, 최종 보상, 실패 정보를 함께 가진다.

### `data_schema`
- `Episode`를 dict로 바꾸는 직렬화 보조 계층이다.
- 현재는 in-memory 구조를 dict로 변환하는 수준이다.

## 현재 구현의 입력과 출력

### 입력
- black agent
- white agent
- 게임 수
- 시드

### 중간 산출물
- encoded state
- action mask
- turn record
- episode

### 출력
- `run_self_play()`의 직접 출력: `SelfPlayResult`
- `Trainer.train(episodes)`의 출력: `TrainingReport`
- `Evaluator.evaluate(...)`의 출력: `EvaluationReport`

## 저장 경계
- 메모리상 `TurnRecord`는 학습 보조 필드를 더 가질 수 있다.
- 기본 저장 산출물은 `Episode.to_dict()`를 통해 `self-play-data-schema.md` 형식으로 해석한다.
- 따라서 메모리 최적화나 학습 편의를 위한 필드와 파일 저장 필드는 분리해서 읽어야 한다.
- 현재 `encoded_state`는 메모리상 필드이지만 기본 파일 출력에는 포함되지 않는다.

## 현재 구현에서 아직 없는 것
- 신경망 모델 학습 루프
- optimizer, loss, checkpoint 저장
- JSONL 또는 Parquet 파일 저장기
- custom initial state 합법성 검증
- self-play 결과를 다시 정책 업데이트로 연결하는 반복 학습 루프

## 상위 설계와 현재 구현의 관계
- `docs/training/trainer-loop.md`와 `docs/training/checkpoint-policy.md`는 향후 누적 학습 루프의 상위 설계를 정의한다.
- 이 문서는 현재 구현 상태를 설명하는 문서이므로, 상위 설계 문서에 있는 trainer-loop와 checkpoint 운영 규칙이 아직 코드에 모두 반영되었다는 뜻은 아니다.
- 따라서 현재 구현 설명과 향후 설계 기준을 혼동하면 안 된다.
- 현재 구현은 상위 설계가 정의한 누적 학습 루프 이전 단계에 머물러 있다고 해석하는 것이 기본값이다.
- 구현 전 문서 우선순위는 다음과 같이 해석한다.
  - 누적 학습 설계 기준: `trainer-loop.md`, `checkpoint-policy.md`
  - 현재 코드 동작 설명: 이 문서 `training-pipeline.md`

## 향후 학습 루프와의 경계
- 현재 구현은 self-play 데이터 수집, 집계, 평가 보조 계층까지를 포함한다.
- 실제 모델 파라미터를 업데이트하는 학습 루프는 아직 구현 범위 밖이다.
- 따라서 `TrainingReport`는 현재 학습 결과가 아니라 수집된 episode 집합의 요약 리포트다.
- `EvaluationReport`도 기존 episode 재사용이 아니라 별도 평가 실행 결과로 해석해야 한다.

## 현재 파이프라인의 해석
현재 저장소의 학습 파이프라인은 완성형 RL trainer라기보다, 엔진 위에서 안전하게 대국 데이터를 만들고 이를 episode 형태로 모아 분석하거나 평가할 수 있게 하는 기반 구현에 가깝다.

즉 현재 중심축은 다음과 같다.
- 엔진 규칙을 따르는 대국 생성
- 학습 입력 표현 생성
- action mask와 reward 연결
- 완료/실패 episode 구분
- 리포트와 평가 산출

이후 실제 모델 학습을 붙이려면 `policy_client`, `trainer`, `data_schema`를 중심으로 확장하면 된다.
