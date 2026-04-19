# Othello ML Project

오셀로 엔진, 학습 파이프라인, 실행 환경을 한 저장소에서 관리하는 Python 프로젝트다.

## 현재 구조
- `src/engine/`
  - 오셀로 규칙, 보드, 수 검증, 게임 진행
- `src/training/`
  - 랜덤/휴리스틱 agent, match runner, self-play, encoder, trainer, evaluator
- `src/api/`
  - FastAPI 런타임과 웹 UI
- `tests/unit/`
  - engine, training 단위 테스트
- `tests/integration/`
  - engine 인수 시나리오 테스트

## 문서 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `docs/README.md`
4. 작업 영역 문서
   - 엔진: `docs/engine/`
   - 학습: `docs/training/`
   - 실행부: `docs/runtime/`
5. 상세 명세: `specs/`
6. 역할 문서: `agents/`
7. 작업 지시서: `tasks/`

## 문서 체계
- `docs/`
  - 프로젝트 기준과 상위 규칙
- `specs/`
  - 구현 직전의 코드 레벨 계약
- `tasks/`
  - 구현 또는 정리 작업 지시
- `agents/`
  - 역할별 책임과 품질 기준
- `reviews/`
  - 검토 결과 기록

## 영역별 빠른 진입
- `engine`
  - 기준 문서: `docs/engine/othello-rules.md`
  - 상세 명세: `specs/engine/python-engine-spec.md`
  - 작업 지시: `tasks/engine/`
  - 담당 코드: `src/engine/`, `tests/unit/engine/`, `tests/integration/engine/`
- `training`
  - 기준 문서: `docs/training/self-play-spec.md`, `docs/training/rl-components.md`
  - 상세 명세: `specs/training/self-play-data-schema.md`, `specs/training/rl-components-spec.md`
  - 작업 지시: `tasks/training/`
  - 담당 코드: `src/training/`, `tests/unit/training/`
- `runtime`
  - 기준 문서: `docs/runtime/runtime-overview.md`
  - 상세 명세: `specs/runtime/project-structure.md`, `specs/runtime/web-runtime-spec.md`
  - 작업 지시: `tasks/runtime/`
  - 담당 코드: `src/api/`, `Dockerfile`, `requirements.txt`

## 실행 메모
- 엔진 코어는 `src/engine/`에 있고 웹 프레임워크와 분리되어 있다.
- 런타임은 현재 `FastAPI + Docker` 기준으로 정리되어 있다.
- 로컬 Python 버전과 무관한 실행은 Docker 기준으로 맞춘다.
