# Docs Index

이 폴더는 프로젝트 상위 기준 문서를 영역별로 나눈다.

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `meta/README.md`
4. 관련 `meta/state/`, `meta/index/`, `meta/graph/`
5. `docs/engine/`
6. `docs/training/`
7. `docs/runtime/`

엔진 규칙을 먼저 고정한 뒤, 그 위에 학습과 실행부를 얹는 구조로 읽는다.

## 구조와 역할
- `docs/engine/`
  - 오셀로 규칙
  - 엔진 모듈 경계
  - 인수 테스트 기준
- `docs/training/`
  - self-play 기준
  - 예측 API 계약
  - 강화학습 구성요소 기준
- `docs/runtime/`
  - Docker 실행
  - FastAPI/UI 런타임 기준

## 우선순위
- `docs/`는 상위 기준 문서다.
- 실제 코드 레벨 계약은 `specs/`에서 더 구체화한다.
- 구현 순서와 완료 조건은 `tasks/`에서 다룬다.
- `meta/`는 관련 대상을 빠르게 찾는 보조 계층이지만 기준 문서는 아니다.
