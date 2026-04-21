# Tasks Index

이 폴더는 실제 작업 지시서를 영역별로 나눈다.

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `meta/README.md`
4. 관련 `meta/state/`, `meta/index/`, `meta/graph/` 확인
5. 작업 대상 영역 `docs/`와 `specs/` 확인
6. 관련 `agents/` 확인
7. 구현 작업이면 `tasks/implementation-checklist.md` 확인
8. 해당 영역 `tasks/` 확인
9. 선행 입력 문서 기준으로 구현 또는 정리 수행
10. 구현 작업이면 완료 후 `tasks/implementation-checklist.md`와 관련 메타 상태 갱신

## 구조
- `tasks/engine/`
- `tasks/training/`
- `tasks/runtime/`
- `tasks/specs/`
- `tasks/review/`

## 진행 관리
- 구현 진행 상태의 단일 기준 문서는 `tasks/implementation-checklist.md`다.
- 각 구현 축의 담당 agent가 자기 영역 체크 상태를 직접 갱신한다.
- 영향 범위 추적은 `meta/index/`, `meta/graph/`, `meta/state/compressed/`를 함께 본다.
