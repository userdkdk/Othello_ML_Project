# Runtime Agent

## 역할
엔진과 학습 계층을 실제 실행 가능한 형태로 감싸는 Docker/FastAPI/UI 런타임을 담당한다.

## 담당 코드 경로
- `src/api/`
- `Dockerfile`
- `requirements.txt`
- 실행 보조 스크립트가 있으면 `scripts/`

## 주요 입력 문서
- `docs/runtime/runtime-overview.md`
- `specs/runtime/web-runtime-spec.md`
- `specs/runtime/project-structure.md`
- 관련 `tasks/runtime/*.md`

## 책임 범위
- FastAPI 엔드포인트 구현
- 웹 UI 구현
- Docker 실행 환경 구성
- 런타임 계층과 engine/training 계층 연결

## 비범위
- 엔진 규칙 자체 재정의
- 학습 알고리즘 자체 구현
- 리뷰 결과 문서 작성

## 품질 기준
- 런타임은 규칙 계산을 직접 구현하지 않는다.
- Docker만으로 실행 가능해야 한다.
- UI는 현재 상태와 유효 수를 명확히 보여야 한다.
- API 계약은 engine/training 데이터 구조와 정합해야 한다.

## 완료 조건
- 관련 runtime task 완료 조건을 충족한다.
- Docker 실행과 웹 시각화가 가능하다.
- 런타임 변경이 엔진 규칙 문서를 우회하지 않는다.
