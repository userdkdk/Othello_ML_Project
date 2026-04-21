# Review: specs/training/self-play-data-schema.md

## 필수 수정
- `valid_moves` 위치가 문서 내부에서 이중 정의되어 저장 포맷이 고정되지 않는다.
  - 근거: [specs/training/self-play-data-schema.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/self-play-data-schema.md:69)~[75행] 예시는 `state.valid_moves`를 사용한다.
  - 근거: 같은 문서 [103행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/self-play-data-schema.md:103)~[105행]은 `valid_moves`, `action_mask`를 turn record의 선택 확장 필드로 둔다.
  - 비교 기준: [specs/training/training-pipeline-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-pipeline-spec.md:49)~[62행]은 메모리상 `TurnRecord`에 `valid_moves`와 `action_mask`가 turn-level 필드로 존재해야 한다고 정의한다.
  - 문제: writer와 reader가 `valid_moves`를 `state` 안에서 읽을지, turn top-level에서 읽을지 고를 수 있게 되어 직렬화 호환성이 깨진다.
  - 권장: `valid_moves`의 canonical 위치를 하나로 고정하고, 다른 위치는 금지하거나 명시적 파생 필드로 재정의한다.
