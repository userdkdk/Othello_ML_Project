# AGENTS.md

## 목적
이 저장소의 에이전트는 오셀로 프로젝트를 `engine`, `training`, `runtime` 세 축으로 나눠 일관되게 설계, 구현, 검토하기 위한 작업 단위로 동작한다.

이 문서는 역할별 agent보다 우선하는 전역 공통 규칙을 정의한다.

## 프로젝트 구분 원칙
- `engine`: 오셀로 규칙, 상태, 수 적용, 검증, 테스트를 담당한다.
- `training`: 랜덤 대국, 휴리스틱 대국, self-play, 상태 인코딩, action mask, trainer, evaluator를 담당한다.
- `runtime`: Docker 실행, FastAPI, 웹 UI, 실행 엔트리포인트, 배포 가능한 실행 환경을 담당한다.

## 디렉터리 역할
- `README.md`: 저장소 전체 구조와 문서 진입점.
- `meta/`: agent용 역색인, relation graph, compressed state, 메타 스키마.
  - `meta/schema/`
  - `meta/entities/`
  - `meta/graph/`
  - `meta/index/`
  - `meta/state/`
- `docs/`: 프로젝트 기준 문서.
  - `docs/engine/`
  - `docs/training/`
  - `docs/runtime/`
- `specs/`: 구현 전 상세 명세 문서.
  - `specs/engine/`
  - `specs/training/`
  - `specs/runtime/`
- `agents/`: 역할별 전문 agent 설명서.
- `tasks/`: 구체 작업 지시서.
  - `tasks/engine/`
  - `tasks/training/`
  - `tasks/runtime/`
  - `tasks/specs/`
  - `tasks/review/`
- `reviews/`: 리뷰 결과물. 가능하면 원본 상대 경로를 그대로 따른다.
- `prompts/`: 반복 사용 템플릿.

## 코드 구조 대응
- `src/engine/`: 엔진 구현 코드
- `src/training/`: 학습 및 self-play 구현 코드
- `src/api/`: 실행부 구현 코드
- `frontend/`: 분리된 런타임 프론트엔드 코드
- `tests/unit/`: 단위 테스트
- `tests/integration/`: 통합/인수 테스트

## 작업 기본 순서
1. 루트 `README.md`를 읽어 저장소 구조와 작업 축을 확인한다.
2. 루트 `AGENTS.md`를 읽어 전역 규칙과 문서 우선순위를 확인한다.
3. `meta/README.md`와 관련 `meta/state/`, `meta/index/`, `meta/graph/`를 읽어 작업 진입점과 영향 범위를 좁힌다.
4. 관련 `docs/`를 읽어 상위 기준을 확인한다.
5. 관련 `specs/`와 `agents/`를 읽어 상세 계약과 역할 기준을 확인한다.
6. 관련 `tasks/`를 읽어 작업 목표와 완료 조건을 확인한다.
7. 구현 작업이면 `tasks/implementation-checklist.md`에서 해당 축 상태를 먼저 확인한다.
8. 구현, 명세 작성, 리뷰 중 현재 작업을 수행한다.
9. 구현 작업이면 완료 후 `tasks/implementation-checklist.md`와 필요한 `meta/` 산출물을 함께 갱신한다.
10. 리뷰 작업이면 결과를 `reviews/` 아래에 기록한다.
11. 사용자가 요청하지 않은 범위는 수정하지 않는다.

## 메타 계층 원칙
- `meta/`는 읽기 최적화와 영향 범위 추적을 위한 운영 계층이다.
- `meta/`는 기준 문서를 대체하지 않는다.
- 상충 시 `docs/`, `specs/`, `tasks/`, `AGENTS.md`가 우선한다.
- `meta/`의 역색인과 relation graph는 관련 코드, 문서, 테스트를 빠르게 찾기 위한 보조 자료다.
- `meta/state/compressed/`는 현재 집중 대상과 리스크, 검증 포인트를 짧게 유지하기 위한 상태 계층이다.

## 문서 우선순위
1. 사용자의 현재 요청
2. 루트 `AGENTS.md`
3. 관련 `tasks/`
4. 관련 `agents/`
5. 관련 `specs/`
6. 관련 `docs/`
7. 관련 `meta/`

동일 수준 문서가 충돌하면 더 작업에 가까운 문서를 우선하고, 해결되지 않으면 충돌 사실을 문서나 리뷰에 남긴다.

## 리뷰 경로 규칙
- 리뷰 결과는 가능하면 검토 대상의 상대 경로를 `reviews/` 아래에 그대로 미러링한다.
- 예시
  - `docs/engine/othello-rules.md` -> `reviews/docs/engine/othello-rules.md`
  - `specs/training/self-play-data-schema.md` -> `reviews/specs/training/self-play-data-schema.md`
  - `tasks/runtime/implement-fastapi-runtime.md` -> `reviews/tasks/runtime/implement-fastapi-runtime.md`

## 수정 허용 범위
- 사용자가 요청한 범위 안에서만 수정한다.
- 기준 문서 수정은 사용자가 문서 정비 또는 수정 자체를 요청했을 때 허용한다.
- 리뷰 전용 작업에서는 구현 코드를 수정하지 않는다.
- 새 규칙을 추가할 때는 기존 `docs/`와 `specs/`와의 충돌 여부를 먼저 확인한다.

## 체크리스트 운영 규칙
- 구현 상태 관리는 `tasks/implementation-checklist.md`를 기준으로 한다.
- `engine` 구현 상태 갱신 책임은 `agents/engine-agent.md`에 있다.
- `training` 데이터/메타데이터 계층 갱신 책임은 `agents/training-data-agent.md`에 있다.
- `training` 실행/학습 루프 계층 갱신 책임은 `agents/training-loop-agent.md`에 있다.
- `runtime` 구현 상태 갱신 책임은 `agents/runtime-agent.md`에 있다.
- `agents/governance-agent.md`는 체크리스트, 명세 정합성, 리뷰 출력 형식, 메타 구조, 메타 최신 여부 검증 역할을 맡는다.
- 구현 작업에서는 관련 코드를 수정한 뒤 해당 축 체크리스트와 필요한 메타 상태를 함께 갱신하는 것을 기본값으로 한다.

## 리뷰 원칙
- 감상이 아니라 기준 문서 대비 차이를 지적한다.
- 재현 가능한 근거를 우선한다.
- 사소한 스타일보다 정답성, 안정성, 설명 가능성을 우선한다.
- 가능하면 우선순위를 구분한다.
  - 필수 수정
  - 권장 수정
  - 있으면 좋은 개선

## 완료 기준
- 작업 대상이 `engine`, `training`, `runtime` 중 어디에 속하는지 명확하다.
- 관련 코드 경로가 `src/` 또는 `tests/`에서 어디인지 드러난다.
- 관련 `docs/`, `specs/`, `tasks/`, `agents/`가 연결되어 있다.
- 리뷰 작업이면 결과가 `reviews/` 아래 올바른 경로에 정리되어 있다.
- 구현 작업이면 관련 기준 문서와 완료 조건을 충족한다.
