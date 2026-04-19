# 구조 문서 리뷰

## 필수 수정

### 1. 문서 진입 순서가 `README.md`와 `AGENTS.md` 사이에서 충돌함
- 기준 문서:
  - `README.md`
  - `AGENTS.md`
  - `tasks/README.md`
  - `specs/README.md`
- 문제:
  - `README.md`는 `AGENTS.md -> docs -> specs -> tasks` 순서로 읽으라고 안내한다.
  - 반면 `AGENTS.md`는 항상 `tasks/`를 먼저 읽고, 그 다음 `README.md`, `agents/`, `specs/`, `docs/`를 보라고 적고 있다.
  - `tasks/README.md`, `specs/README.md`도 각각 자기 기준의 읽는 순서를 제시하고 있어 진입 규칙이 하나로 고정되지 않는다.
- 영향:
  - 사용자가 어떤 작업을 시작할 때 `상위 기준부터 읽어야 하는지`, `작업 지시서부터 읽어야 하는지`가 문서마다 다르게 보인다.
  - 지금처럼 저장소를 `engine / training / runtime` 축으로 다시 정리한 목적이 "한눈에 들어오게" 만드는 것이라면, 첫 진입 규칙이 흔들리는 것은 바로 혼선을 만든다.
- 권장 방향:
  - 루트 기준 진입 순서를 하나로 고정하고, `README.md`, `AGENTS.md`, `docs/README.md`, `specs/README.md`, `tasks/README.md`가 같은 흐름을 가리키게 맞춰야 한다.

## 권장 수정

### 2. 루트 개요가 `engine / training / runtime` 전 영역의 실제 진입점을 동일한 해상도로 보여주지 않음
- 기준 문서:
  - `README.md`
  - `AGENTS.md`
  - `specs/runtime/project-structure.md`
- 문제:
  - `README.md`의 `현재 구조`는 `src/engine`, `src/training`, `src/api`, `tests/unit`, `tests/integration`만 요약한다.
  - 그런데 실제 문서 체계의 핵심은 코드 폴더뿐 아니라 `docs/`, `specs/`, `tasks/`, `agents/`, `reviews/`가 `engine / training / runtime` 축으로 연결되어 있다는 점이다.
  - 현재 루트 개요만 보면 코드 구조는 보이지만, 새로 정리한 문서 축과 실제 작업 진입점은 한 단계 더 내려가서 찾아야 한다.
- 영향:
  - 저장소에 처음 들어온 사람이 "세 축으로 나눴다"는 말은 이해해도, 각 축의 기준 문서와 작업 문서가 어디에 모여 있는지는 바로 파악하기 어렵다.
- 권장 방향:
  - `README.md`에 `문서 구조`를 코드 구조와 같은 수준으로 드러내거나, 각 축별 대표 파일 예시를 한 줄씩 추가하는 편이 좋다.
