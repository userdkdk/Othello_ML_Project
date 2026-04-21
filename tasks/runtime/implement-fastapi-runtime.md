# FastAPI 런타임 구현 작업 지시서

## 목적
엔진을 Docker와 FastAPI로 실행하고, 분리된 프론트엔드 앱으로 게임 UI를 제공할 수 있게 만든다.

## 선행 입력
- `docs/runtime/runtime-overview.md`
- `specs/runtime/web-runtime-spec.md`
- `specs/runtime/project-structure.md`
- `agents/runtime-agent.md`

## 필수 작업
- FastAPI app 구현
- 최소 API 엔드포인트 구현
- 분리된 프론트엔드 앱 구현
- 게임 모드 선택 구현
  - `human_vs_human`
  - `human_vs_model`
  - `model_vs_model`
- `human_vs_model`에서 사람 색 선택과 모델 턴 자동 또는 명시 진행 구현
- `model_vs_model` 관전 진행 구현
- `POST /api/step` 기반 모델 턴 진행 경로 구현
- inference checkpoint 경로를 받아 흑/백 agent를 구성하는 경로 구현
- dependency 부족 시 checkpoint 로드 실패를 제어된 오류 또는 fallback warning으로 처리
- Dockerfile 구성
- requirements 정리

## 완료 조건
- Docker로 앱 실행이 가능하다.
- `/`에서 보드 UI를 볼 수 있다.
- `/training`에서 분리된 학습 운영 UI 진입이 가능하다.
- `/api/state`, `/api/new`, `/api/move`, `/api/pass`, `/api/step`이 동작한다.
- `/api/training/state`와 `/api/training/comparisons/latest` 기본 조회가 동작한다.
- 사람이 모델과 둘 수 있다.
- 모델끼리 두는 대국을 UI에서 관전할 수 있다.
- runtime image에서 inference checkpoint 로드 경로가 `torch` 의존성 부족으로 즉시 깨지지 않는다.
