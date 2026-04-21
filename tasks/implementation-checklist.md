# 구현 체크리스트

## 목적
이 문서는 현재 저장소의 구현 상태를 매번 코드 전체를 다시 읽지 않고 추적하기 위한 작업 체크리스트다.

기준 문서는 여전히 `docs/`, `specs/`, `tasks/`이지만, 실제 진행 관리는 이 문서를 우선 갱신하는 방식으로 사용한다.

## 사용 규칙
- 상태 갱신 책임:
  - `engine` 항목: `agents/engine-agent.md`
  - `training` 데이터/메타데이터 항목: `agents/training-data-agent.md`
  - `training` 실행/운영 항목: `agents/training-loop-agent.md`
  - `runtime` 항목: `agents/runtime-agent.md`
- 체크리스트 구조 정리와 메타 연결 보조: `agents/governance-agent.md`
- 새 구현 작업을 시작하기 전에 관련 항목 상태를 먼저 갱신한다.
- 구현 후에는 코드 자체 설명 대신 이 문서의 체크 상태, 메모, 필요한 메타 상태를 갱신한다.
- 상태 의미는 다음과 같다.
  - `[x]`
    - 문서 기준으로 구현이 존재하고, 현재 저장소 기준으로 큰 틀에서 연결돼 있음
  - `[-]`
    - 일부 구현은 존재하지만 범위가 불완전하거나 추가 검증/정리가 필요함
  - `[ ]`
    - 아직 없거나 사실상 착수 전 상태
- 세부 근거가 필요하면 관련 task/spec 경로만 적고, 여기서 장황하게 설명하지 않는다.

## Engine
- [x] `Board` 구현
  - 기준: `tasks/engine/implement-board.md`
  - 경로: `src/engine/board.py`, `tests/unit/engine/test_board.py`
- [x] `move_validator` 구현
  - 기준: `tasks/engine/implement-move-validator.md`
  - 경로: `src/engine/move_validator.py`, `tests/unit/engine/test_move_validator.py`
- [x] `game_engine` 구현
  - 기준: `tasks/engine/implement-game-engine.md`
  - 경로: `src/engine/game_engine.py`, `tests/unit/engine/test_game_engine.py`
- [x] 엔진 인수 시나리오 테스트
  - 경로: `tests/integration/engine/test_acceptance_scenarios.py`
  - 메모: `GameResult` winner 표현을 최신 spec 기준으로 정리 후 재검증 완료

## Training

### 기반 파이프라인
- [x] self-play 실행 경로
  - 기준: `tasks/training/implement-self-play.md`
  - 경로: `src/training/match_runner.py`, `src/training/self_play_runner.py`
  - 담당: `agents/training-data-agent.md`
- [x] RL 보조 구성요소
  - 기준: `tasks/training/implement-rl-components.md`
  - 경로: `src/training/action_mask.py`, `state_encoder.py`, `episode.py`, `statistics.py`, `evaluator.py`
  - 담당: `agents/training-data-agent.md`
- [x] training pipeline 정리
  - 기준: `tasks/training/implement-training-pipeline.md`
  - 메모: `Trainer.train()`은 현재 요약 리포트 계층으로 유지. 모델 업데이트 실행 진입점은 `scripts/train_policy.py`
  - 담당: `agents/training-loop-agent.md`

### 저장/모델/체크포인트
- [x] episode JSONL 저장
  - 기준: `tasks/training/implement-episode-storage.md`
  - 경로: `src/training/episode_storage.py`
  - 담당: `agents/training-data-agent.md`
- [x] CNN 정책/가치 모델
  - 기준: `tasks/training/implement-cnn-policy-model.md`
  - 경로: `src/training/cnn_model.py`, `src/training/cnn_policy_agent.py`, `src/training/policy_client.py`
  - 담당: `agents/training-data-agent.md`
- [x] checkpoint 저장/로드
  - 기준: `tasks/training/implement-checkpoint-policy.md`
  - 경로: `src/training/cnn_policy_agent.py`
  - 담당: `agents/training-data-agent.md`

### 학습 루프/운영
- [x] trainer-loop 기본 경로
  - 기준: `tasks/training/implement-trainer-loop.md`
  - 경로: `src/training/trainer.py`, `src/training/training_pipeline.py`
  - 메모: 실제 모델 업데이트, resume, best track 저장까지 기본 골격 존재
  - 담당: `agents/training-loop-agent.md`
- [ ] training ops 세션 상태 객체
  - 기준: `tasks/training/implement-training-ops.md`
  - 담당: `agents/training-loop-agent.md`
- [ ] training ops 세션 메타데이터 / `active_stage`
  - 기준: `tasks/training/implement-training-ops.md`
  - 담당: `agents/training-loop-agent.md`
- [ ] training ops latest iteration snapshot
  - 기준: `tasks/training/implement-training-ops.md`
  - 담당: `agents/training-loop-agent.md`
- [-] training ops history snapshot
  - 기준: `tasks/training/implement-training-ops.md`
  - 메모: `runs/latest/training_state.json`에 latest iteration과 제한된 history를 남기도록 기본 경로를 추가함. pause/resume/session API는 아직 미완
  - 담당: `agents/training-loop-agent.md`
- [ ] training ops checkpoint inventory
  - 기준: `tasks/training/implement-training-ops.md`
  - 담당: `agents/training-loop-agent.md`
- [ ] checkpoint 비교 전용 실행기
  - 기준: `tasks/training/implement-training-ops.md`
  - 메모: evaluator 기반 비교 재료는 있으나 운영 기능으로 분리된 API-ready 계층은 아직 없음
  - 담당: `agents/training-loop-agent.md`
- [ ] checkpoint 비교 결과 직렬화
  - 기준: `tasks/training/implement-training-ops.md`
  - 담당: `agents/training-loop-agent.md`
- [x] training 전용 Docker
  - 기준: `tasks/training/implement-training-docker.md`
  - 경로: `Dockerfile.training`, `requirements-training.txt`, `scripts/train_policy.py`
  - 메모: training Docker 이미지에서 `pytest tests/unit/training -q` 39 passed, `python scripts/train_policy.py` end-to-end 실행 확인
  - 담당: `agents/training-loop-agent.md`

## Runtime
- [-] 기본 FastAPI 게임 UI
  - 기준: `tasks/runtime/implement-fastapi-runtime.md`
  - 경로: `src/api/fastapi_app.py`, `src/api/game_router.py`, `src/api/training_router.py`, `src/api/runtime.py`, `frontend/`
  - 메모: FastAPI app 조립, 라우터, 런타임 helper, SPA 서빙을 분리했고 `/training` 대시보드 진입도 분리했다. Docker/venv 기준 최종 검증만 남음
- [-] `human_vs_human` / `human_vs_model` / `model_vs_model` 모드 완성
  - 기준: `tasks/runtime/implement-fastapi-runtime.md`
- [x] `/api/step` 기반 모델 턴 진행
  - 기준: `tasks/runtime/implement-fastapi-runtime.md`
- [-] inference checkpoint 경로 기반 흑/백 agent 구성
  - 기준: `tasks/runtime/implement-fastapi-runtime.md`
  - 메모: checkpoint 경로 로드를 우선 시도하고 파일이 없으면 heuristic fallback을 사용
- [ ] 학습 대시보드 UI
  - 기준: `tasks/runtime/implement-training-dashboard.md`
  - 메모: 분리된 프론트엔드와 `GET /api/training/state` 기본 조회는 추가됐지만 training ops 제어 API와 실제 동작 연결은 아직 미완
- [ ] `GET /api/training/state`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
  - 메모: idle snapshot과 checkpoint inventory 기본 응답만 구현됨
- [ ] `POST /api/training/start`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/start-from-checkpoint`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/run-once`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/pause`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/resume-session`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/stop`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `POST /api/training/compare`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] `GET /api/training/comparisons/latest`
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [ ] dashboard polling
  - 기준: `tasks/runtime/implement-training-dashboard.md`
- [-] runtime 테스트
  - 경로: `tests/unit/runtime/test_fastapi_app.py`
  - 메모: 로컬 Python 환경에서는 `fastapi`가 없어 pytest 실행은 미완. 대신 Docker runtime 이미지에서 함수 직접 호출 smoke test는 통과

## 문서/명세 정합성
- [x] `docs` 정리
- [x] `specs` 정리
- [x] `tasks` 정리
- [-] 구현과 문서의 최종 정합성 재검증
  - 메모: 이후 실제 구현 단계마다 이 문서 기준으로만 갱신

## 다음 우선순위
- [ ] runtime 기본 게임 모드 최종 정합화
- [ ] inference checkpoint 실경로 검증과 모델 agent 연결 보강
- [ ] runtime pytest 경로를 Docker 기준으로 재정리
- [ ] training ops 프론트 docs 정리
- [ ] training ops 상태 객체 / snapshot 계층 추가
- [ ] runtime training dashboard API 연결
- [ ] training 전용 Docker 정리
