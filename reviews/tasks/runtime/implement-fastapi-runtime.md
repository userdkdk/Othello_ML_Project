# Review: tasks/runtime/implement-fastapi-runtime.md

## 필수 수정
- runtime task가 `model_vs_model` 관전용 진행 endpoint를 반영하지 못한다.
  - 근거: [tasks/runtime/implement-fastapi-runtime.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/runtime/implement-fastapi-runtime.md:12)~[24행]은 최소 API 엔드포인트 구현을 요구하지만 구체 완료 조건 [29행](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/runtime/implement-fastapi-runtime.md:29)에는 `/api/state`, `/api/new`, `/api/move`, `/api/pass`만 있다.
  - 비교 기준: [specs/runtime/web-runtime-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/web-runtime-spec.md:11)~[17행]은 `POST /api/step`을 최소 엔드포인트에 포함한다.
  - 비교 기준: 같은 spec [50행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/web-runtime-spec.md:50)~[52행]은 `POST /api/step`을 모델 턴 진행과 `model_vs_model` 관전의 기본 경로로 정의한다.
  - 문제: task 기준대로 구현하면 spec을 만족하지 못하는 runtime이 완료 처리될 수 있다.
  - 권장: 필수 작업과 완료 조건에 `POST /api/step`을 명시한다.
