# Review: specs/training/training-pipeline-spec.md

## 필수 수정
- `run_match` 계약이 `GameState.clone()` 존재를 전제하지만 engine spec에는 그 API가 없다.
  - 근거: [specs/training/training-pipeline-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-pipeline-spec.md:34)는 agent 호출 시 입력 상태가 `state.clone()`이어야 한다고 고정한다.
  - 비교 기준: [specs/engine/python-engine-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/engine/python-engine-spec.md:78)~[88행]의 `GameState` 계약에는 `clone()` 메서드가 없다.
  - 비교 기준: 같은 엔진 spec의 공개 API는 [169행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/engine/python-engine-spec.md:169) 이하에 정의돼 있지만 `GameState.clone()`는 없다.
  - 문제: training spec이 engine spec에 없는 메서드를 필수로 요구하므로, 두 spec을 동시에 만족하는 구현 계약이 성립하지 않는다.
  - 권장: `GameState.clone()`를 engine spec에 추가하거나, training spec을 "agent에 전달되는 입력 상태는 원본과 분리된 스냅샷 또는 동등 clone"처럼 더 추상적으로 바꾼다.
