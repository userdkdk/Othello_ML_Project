# Specs Index

이 폴더는 구현 전에 고정해야 하는 상세 명세를 영역별로 나눈다.

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. 관련 `docs/` 확인
4. 해당 영역 `specs/` 확인
5. 관련 `agents/` 확인
6. 구현 전 `tasks/` 확인

## 구조와 역할
- `specs/engine/`
  - Python 엔진 인터페이스와 직렬화 계약
- `specs/training/`
  - self-play 데이터 스키마
  - RL 구성요소 명세
- `specs/runtime/`
  - 프로젝트 구조
  - 웹/도커 런타임 명세
