# FastAPI 런타임 구현 작업 지시서

## 목적
엔진을 Docker와 FastAPI로 실행하고 웹 UI로 시각화할 수 있게 만든다.

## 선행 입력
- `docs/runtime/runtime-overview.md`
- `specs/runtime/web-runtime-spec.md`
- `specs/runtime/project-structure.md`
- `agents/runtime-agent.md`

## 필수 작업
- FastAPI app 구현
- 최소 API 엔드포인트 구현
- 웹 UI 구현
- Dockerfile 구성
- requirements 정리

## 완료 조건
- Docker로 앱 실행이 가능하다.
- `/`에서 보드 UI를 볼 수 있다.
- `/api/new`, `/api/move`, `/api/pass`가 동작한다.
