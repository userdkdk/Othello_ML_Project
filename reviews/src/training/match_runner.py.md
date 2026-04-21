# `match_runner.py` Review

## 필수 수정

### 1. CNN 정책 버전이 self-play 메타데이터로 전달되지 않음
- 기준 문서:
  - `docs/training/cnn-policy.md`
  - `specs/training/self-play-data-schema.md`
  - `agents/training-agent.md`
- 문제:
  - `run_match()`는 `Episode` 생성 시 `black_agent.version` / `white_agent.version`만 기록한다.
  - 새로 추가된 `PolicyClient.model_version`과 `src/training/cnn_model.py`의 `MODEL_VERSION`은 episode 메타데이터로 연결되지 않는다.
  - 즉, CNN-backed policy를 `PolicyClient(model=...)`로 사용해도 self-play 결과에는 실제 모델 버전이 남지 않는다.
- 영향:
  - `policy_black_version` / `policy_white_version`가 학습 데이터 재현성 기준이 되지 못한다.
  - 문서가 요구하는 "모델 구조 변경 시 버전도 명시적으로 갱신" 조건을 코드에서 강제하지 못한다.
  - 이후 비교 평가나 데이터 재생성 시 어떤 CNN이 사용됐는지 추적할 수 없다.
- 근거 위치:
  - `src/training/match_runner.py:36-40`
  - `src/training/policy_client.py:27-37`
  - `src/training/cnn_model.py:9`
- 수정 방향:
  - `Episode` 생성 시 agent 버전 대신 policy/model 버전을 읽을 수 있는 단일 계약을 만들거나,
  - `PolicyClient`를 포함한 정책 래퍼가 self-play 메타데이터를 직접 제공하도록 연결해야 한다.

