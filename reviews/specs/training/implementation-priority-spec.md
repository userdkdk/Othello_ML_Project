# Review: specs/training/implementation-priority-spec.md

## 권장 수정
- 우선순위 명세가 새로 추가된 학습 운영 축을 반영하지 못해 현재 문서 체계와 어긋난다.
  - 근거: [specs/training/implementation-priority-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/implementation-priority-spec.md:13)~[19행]의 권장 순서는 `implement-training-pipeline`부터 `implement-trainer-loop`까지 6개 작업만 포함한다.
  - 비교 기준: 현재 저장소에는 [specs/training/training-ops-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-ops-spec.md:1)과 [tasks/training/implement-training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/tasks/training/implement-training-ops.md:1)가 추가돼 있다.
  - 비교 기준: [docs/training/training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:21)~[41행]은 세션 제어와 checkpoint 비교를 별도 구현 축으로 고정했다.
  - 문제: 현재 우선순위 spec만 따르면 training-ops는 비계획 작업처럼 보이고, trainer-loop와의 선후 의존 관계도 추적할 수 없다.
  - 권장: `implement-training-ops`를 우선순위와 의존 관계에 포함하고, trainer-loop와 checkpoint-policy 이후인지 병행 가능한지 명시한다.
