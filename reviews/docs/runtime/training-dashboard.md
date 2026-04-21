# Review: docs/runtime/training-dashboard.md

## 필수 수정
- `resume` 버튼 의미가 checkpoint 기반 새 세션 시작과 paused 세션 재개 사이에서 충돌한다.
  - 근거: [docs/runtime/training-dashboard.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/runtime/training-dashboard.md:32)에서는 "기존 checkpoint 기반 resume 시작"을 세션 제어 패널에 포함한다.
  - 근거: 같은 패널에서 [34행](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/runtime/training-dashboard.md:34)에 별도로 `resume 요청`도 존재한다.
  - 문제: UI 수준에서 `resume` 하나가 두 행동을 뜻하면 API와 버튼 라벨을 설계할 때 충돌한다. 하나는 "checkpoint로 새 세션 시작", 다른 하나는 "paused 세션 재개"다.
  - 권장: 버튼/행동 명칭을 분리한다.
    - 예: `resume from checkpoint`
    - 예: `resume session`

## 권장 수정
- checkpoint 비교 패널이 training checkpoint와 inference checkpoint 중 무엇을 기본 대상으로 삼는지 상위 문서와 맞춰서 명시하는 편이 좋다.
  - 근거: [docs/runtime/training-dashboard.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/runtime/training-dashboard.md:56)~[62행]은 비교 UI 요소만 정의하고 입력 기본값은 정의하지 않는다.
  - 비교 기준: [docs/runtime/runtime-overview.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/runtime/runtime-overview.md:17)~[26행]은 runtime이 inference checkpoint를 기본 소비 대상으로 본다.
  - 문제: 비교 패널 구현 시 training checkpoint까지 기본 선택지에 넣을지, inference checkpoint를 우선할지 결정 근거가 부족하다.
  - 권장: 기본 비교 대상은 inference checkpoint로 두고, training checkpoint는 호환 가능한 경우에만 명시적으로 선택 가능하다고 적는다.
