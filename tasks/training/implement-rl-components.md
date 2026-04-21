# 강화학습 구성요소 구현 작업 지시서

## 목적
강화학습과 랜덤 시뮬레이션에 필요한 보조 구성요소를 구현한다.

## 선행 입력
- `docs/training/rl-components.md`
- `docs/training/self-play-spec.md`
- `docs/training/predict-api.md`
- `specs/training/rl-components-spec.md`
- `specs/training/self-play-data-schema.md`
- `agents/training-data-agent.md`

## 필수 작업
- `match_runner`
- `random_agent`
- `heuristic_agent`
- `statistics`
- `state_encoder`
- `action_mask`
- `episode`
- `self_play_runner`
- `trainer`
- `evaluator`

## 완료 조건
- 랜덤 agent와 heuristic agent로 한 판 대국이 끝까지 실행된다.
- self-play 결과가 episode 구조로 수집된다.
- action mask 길이와 인덱스 규약이 문서와 일치한다.
- state encoder 출력 구조가 문서와 일치한다.
