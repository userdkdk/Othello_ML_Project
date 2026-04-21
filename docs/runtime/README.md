# Runtime Docs

`runtime` 영역은 엔진과 학습 계층을 외부에서 실행 가능한 형태로 감싼다.

## 읽는 순서
1. `runtime-overview.md`
2. `run-guide.md`
3. `training-dashboard.md`

## 파일 역할
- `runtime-overview.md`
  - Docker 실행 기준
  - FastAPI 역할
  - 분리된 프론트엔드와 백엔드 경계
  - 웹 UI가 가져야 할 책임 범위
  - runtime이 training checkpoint와 inference checkpoint를 어떻게 소비하는지에 대한 상위 방향
- `run-guide.md`
  - runtime Docker 실행 방법
  - `run-runtime.sh`, `make runtime` 사용법
  - 포트, 이미지 이름, 컨테이너 이름 변경 방법
- `training-dashboard.md`
  - 학습 운영 UI 분리 기준
  - 학습 제어/상태 조회/checkpoint 비교 화면 기준
