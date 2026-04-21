# Review: tasks/training/prioritize-training-implementation.md

## 필수 수정
- 우선순위 정리 task가 `training-ops` 축을 입력과 완료 기준에서 반영하지 못한다.
  - 근거: [tasks/training/prioritize-training-implementation.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/training/prioritize-training-implementation.md:10)~[15행]의 선행 입력에는 `implement-training-ops.md`가 없다.
  - 비교 기준: [specs/training/implementation-priority-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/implementation-priority-spec.md:13)~[20행]은 `implement-training-ops`를 권장 순서에 포함한다.
  - 비교 기준: 같은 spec [30행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/implementation-priority-spec.md:30)~[33행]은 `implement-training-ops`의 의존 관계와 `training-docker`의 뒤 배치를 정의한다.
  - 문제: 현재 task 기준대로 우선순위를 정리하면 최신 spec보다 오래된 순서를 문서화하게 된다.
  - 권장: 선행 입력에 `tasks/training/implement-training-ops.md`를 추가하고, 완료 조건에도 `training-ops`의 상대적 순서와 이유가 드러나도록 반영한다.
