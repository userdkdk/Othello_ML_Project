# Meta Index

`meta/`는 agent가 필요한 코드, 문서, 테스트만 빠르게 읽고 영향 범위를 계산하기 위한 운영 계층이다.

정답 기준은 여전히 `AGENTS.md`, `docs/`, `specs/`, `tasks/`다. `meta/`는 이를 대체하지 않는다.

## 목적
- 문서 상속형 탐색 대신 역색인 기반 탐색으로 전환
- 특정 함수, 클래스, task, spec section, endpoint의 영향 범위 즉시 확인
- 현재 작업 상태를 compressed state로 짧게 유지

## 구조
- `meta/schema/`
  - 코드, 문서, 테스트, relation edge, compressed state 스키마
- `meta/entities/`
  - 코드, 문서, 테스트 엔티티 저장 위치
- `meta/graph/`
  - 관계 그래프 노드와 edge 저장 위치
- `meta/index/`
  - symbol, feature tag, task id, endpoint 기준 역색인
- `meta/state/`
  - 축별 compressed state

## 생성 스크립트
- `scripts/build_meta_index.py`
  - `src/`, `tests/`, `docs/`, `specs/`, `tasks/`, `agents/`를 스캔해 `meta/` 산출물을 다시 만든다.
- `scripts/check_meta_index.py`
  - 현재 저장소 기준으로 `meta/`를 다시 생성해 비교하고, 결과가 다르면 실패한다.

## 권장 실행 순서
1. 변경 전 영향 범위 확인
2. 작업 수행
3. `python3 scripts/build_meta_index.py`
4. `python3 scripts/check_meta_index.py`

검증 책임은 별도 agent가 아니라 `agents/governance-agent.md`가 가진다.

## 자동화
- `make meta`
  - 메타 산출물 재생성
- `make meta-check`
  - 메타 최신 여부 검증
- `scripts/install_git_hooks.sh`
  - 저장소의 `pre-commit` 훅을 설치한다.
- `.githooks/pre-commit`
  - `src/`, `tests/`, `docs/`, `specs/`, `tasks/`, `agents/`, `meta/`, `scripts/build_meta_index.py` 변경 시 `make meta-check`를 실행한다.

## 읽는 순서
1. `meta/state/compressed/<axis>.json`
2. 관련 `meta/index/*.json`
3. 관련 `meta/graph/edges.jsonl`
4. 필요한 경우 `meta/entities/*.jsonl`
5. 그 다음 원본 기준 문서 `docs/`, `specs/`, `tasks/`

## 핵심 엔티티 타입
- `code.module`
- `code.class`
- `code.function`
- `doc.file`
- `doc.section`
- `test.unit`
- `test.integration`
- `test.e2e`

## 핵심 relation 타입
- `defines`
- `implements`
- `satisfies`
- `verifies`
- `calls`
- `raises`
- `uses`
- `references`
- `exposes`
- `owned_by`

## 폴더별 사용 기준
- `meta/entities/`는 사실 저장소 상태를 기술한다.
- `meta/graph/`는 엔티티 간 연결을 기술한다.
- `meta/index/`는 조회 속도를 위해 파생 생성된다.
- `meta/state/compressed/`는 현재 집중 중인 작업 컨텍스트를 유지한다.
