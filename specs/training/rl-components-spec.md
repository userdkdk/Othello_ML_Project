# 강화학습 구성요소 명세

## 목적
이 문서는 `src/training` 아래 강화학습 보조 구성요소의 파일 구조와 공개 계약을 정의한다.

## 구현 대상 경로
- `src/training/match_runner.py`
- `src/training/random_agent.py`
- `src/training/heuristic_agent.py`
- `src/training/statistics.py`
- `src/training/state_encoder.py`
- `src/training/action_mask.py`
- `src/training/episode.py`
- `src/training/self_play_runner.py`
- `src/training/trainer.py`
- `src/training/evaluator.py`

## 공개 계약

### `match_runner`
- `run_match(black_agent, white_agent, seed, episode_id) -> MatchResult`
- 유효 수가 있으면 agent는 그중 하나를 반환해야 한다.
- `PASS`는 유효 수가 없을 때만 허용한다.
- 잘못된 행동은 실패 episode로 전환해야 한다.

### `random_agent`
- 유효 수 중 무작위 선택

### `heuristic_agent`
- 코너 > 엣지 > 뒤집기 수 우선

### `state_encoder`
- `encode_state(GameState) -> 4 x 8 x 8`

### `action_mask`
- 전체 길이 `65`
- 좌표 64개 + `PASS` 1개

### `self_play_runner`
- `run_self_play(black_agent, white_agent, num_games, seed)`
- 내부적으로 각 게임 시드는 `seed + game_index`를 사용한다.
- 실패 episode는 반환하되 승패 통계에서는 제외한다.

### `episode`
- `Episode`
- `TurnRecord`
- `EpisodeFailure`
- `TurnRecord`는 메모리상 `encoded_state`를 포함할 수 있다.
- 기본 직렬화 출력은 `self-play-data-schema.md`를 따르며, 현재 `encoded_state`는 기본 출력에 포함되지 않는다.

### `trainer`
- episode 집합을 입력으로 받아 training report 생성

### `evaluator`
- 다수 대국의 승률 리포트 생성

## 품질 기준
- 모든 agent는 유효하지 않은 수를 최종 반환하면 안 된다.
- episode는 완료/실패를 구분해야 한다.
- action mask와 state encoder는 예측 계약과 self-play 스키마와 일치해야 한다.
