# Review: tasks/implementation-checklist.md

## 필수 수정
- `engine`을 전부 `[x]`로 표시한 것은 현재 spec 기준으로 과대평가다.
  - 근거: [tasks/implementation-checklist.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/implementation-checklist.md:32)~[36행]은 `game_engine`과 엔진 인수 시나리오를 모두 완료로 표시한다.
  - 비교 기준: [specs/engine/python-engine-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/engine/python-engine-spec.md:43)~[48행]은 `GameResult`를 `BLACK | WHITE | DRAW`로 정의한다.
  - 실제 구현: [src/engine/types.py](/home/dkdk/dkdk/03.study/06.practice/pr3/src/engine/types.py:18)~[21행]은 아직 `BLACK_WIN | WHITE_WIN | DRAW`를 사용한다.
  - 문제: 체크리스트의 `[x]` 기준이 "현재 spec과 큰 결손 없이 연결"인데, winner 표현은 engine과 training/runtime 직렬화 경계에 직접 걸리는 계약이다.
  - 권장: engine 전체를 무조건 `[x]`로 두기보다, 최소한 engine 정합성 관련 메모를 넣거나 `game_engine`/엔진 정합성 항목을 `[-]`로 낮춰 현재 spec mismatch를 드러내야 한다.

## 권장 수정
- `training ops` 항목 분해가 spec보다 거칠어서 진행 관리 문서로 쓰기에 아쉽다.
  - 근거: [tasks/implementation-checklist.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/implementation-checklist.md:67)~[74행]은 `세션 제어`, `checkpoint inventory / dashboard snapshot`, `checkpoint 비교 전용 실행기` 정도로만 나눈다.
  - 비교 기준: [specs/training/training-ops-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-ops-spec.md:47)~[59행], [103행]~[182행]은 `session metadata`, `latest_iteration`, `history`, `checkpoint_inventory`, `comparison output`를 별도 계약으로 분리한다.
  - 권장: 최소한 다음 항목은 따로 쪼개는 편이 좋다.
    - 세션 상태 객체
    - 세션 메타데이터/active_stage
    - latest_iteration/history snapshot
    - checkpoint inventory
    - comparison runner
    - comparison result serialization

- `runtime` 체크 항목도 대시보드 API 기준으로 조금 더 잘게 쪼개는 편이 관리에 유리하다.
  - 근거: [tasks/implementation-checklist.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/implementation-checklist.md:89)~[94행]은 `학습 대시보드 UI`, `/api/training/* 운영 API`, `마지막 비교 결과 조회 및 dashboard polling` 정도로 묶어 둔다.
  - 비교 기준: [specs/runtime/training-dashboard-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/training-dashboard-spec.md:26)~[35행]은 `start`, `start-from-checkpoint`, `run-once`, `pause`, `resume-session`, `stop`, `compare`, `comparisons/latest`를 각각 고정한다.
  - 권장: 구현 상태를 오판하지 않도록 `/api/training/state`, `/start`, `/start-from-checkpoint`, `/resume-session`, `/compare`, `/comparisons/latest` 정도는 별도 체크로 빼는 편이 좋다.

- `다음 우선순위`는 최신 training 우선순위 spec과 연결이 약하다.
  - 근거: [tasks/implementation-checklist.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/implementation-checklist.md:103)~[107행]은 runtime 중심 우선순위만 적고 있다.
  - 비교 기준: [specs/training/implementation-priority-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/implementation-priority-spec.md:13)~[20행]은 `implement-training-ops` 다음에 `implement-training-docker`를 두고 있다.
  - 권장: 체크리스트 하단 우선순위도 최소한 `training-ops -> training-docker` 순서를 반영하거나, runtime 우선순위와 training 우선순위를 분리해 적는 편이 낫다.
