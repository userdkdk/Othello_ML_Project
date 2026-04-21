# Specs Index

이 폴더는 구현 전에 고정해야 하는 상세 명세를 영역별로 나눈다.

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `meta/README.md`
4. 관련 `meta/index/`, `meta/graph/`, `meta/state/` 확인
5. 관련 `docs/` 확인
6. 해당 영역 `specs/` 확인
7. 관련 `agents/` 확인
8. 구현 전 `tasks/` 확인

## 구조와 역할
- `specs/engine/`
  - Python 엔진 인터페이스와 직렬화 계약
- `specs/training/`
  - self-play 데이터 스키마
  - RL 구성요소 명세
- `specs/runtime/`
  - 프로젝트 구조
  - 웹/도커 런타임 명세

## 메타와의 관계
- `specs/`는 정답 계약을 정의한다.
- `meta/`는 해당 계약이 어떤 코드, 테스트, task와 연결되는지 역으로 찾게 돕는다.
