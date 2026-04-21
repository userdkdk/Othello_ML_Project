# Runtime Agent

## 역할
엔진과 학습 계층을 실제 실행 가능한 형태로 감싸는 Docker/FastAPI/UI 런타임을 담당한다.

## 담당 코드 경로
- `src/api/`
- `frontend/`
- `Dockerfile`
- `requirements.txt`
- 실행 보조 스크립트가 있으면 `scripts/`

## 주요 입력 문서
- `meta/README.md`
- `meta/state/compressed/runtime.json`
- `meta/index/by_endpoint.json`
- `meta/graph/edges.jsonl`
- `docs/runtime/runtime-overview.md`
- `specs/runtime/web-runtime-spec.md`
- `specs/runtime/project-structure.md`
- 관련 `tasks/runtime/*.md`

## 책임 범위
- FastAPI 엔드포인트 구현
- 분리된 프론트엔드 앱 구현
- Docker 실행 환경 구성
- 런타임 계층과 engine/training 계층 연결
- endpoint와 관련 코드/테스트/문서의 영향 범위 추적
- 한 파일에 과도하게 몰린 런타임 코드를 역할별 모듈로 분리
- 폴더 구조만 봐도 영향 범위가 드러나도록 유지
- runtime 관련 구현 상태를 `tasks/implementation-checklist.md`에 갱신

## 비범위
- 엔진 규칙 자체 재정의
- 학습 알고리즘 자체 구현
- 리뷰 결과 문서 작성

## 품질 기준
- 런타임은 규칙 계산을 직접 구현하지 않는다.
- Docker만으로 실행 가능해야 한다.
- UI는 현재 상태와 유효 수를 명확히 보여야 한다.
- API 계약은 engine/training 데이터 구조와 정합해야 한다.
- `src/api/`는 app 조립, router, state, schema, runtime helper를 한 파일에 섞지 않는다.
- `frontend/src/`는 page, component, lib 책임을 분리하고 `App.jsx`를 과도한 구현 파일로 키우지 않는다.
- 새 기능을 추가할 때는 기존 파일에 누적하기보다 영향 범위 기준으로 새 모듈 분리를 먼저 검토한다.
- 변경 후에는 경로만 봐도 endpoint, state, frontend page, 테스트 위치를 역추적할 수 있어야 한다.

## 완료 조건
- 관련 runtime task 완료 조건을 충족한다.
- Docker 실행과 웹 시각화가 가능하다.
- 런타임 변경이 엔진 규칙 문서를 우회하지 않는다.
- runtime 관련 체크리스트 상태가 최신 구현 기준으로 갱신되어 있다.
