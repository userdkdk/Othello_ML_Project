# Review: specs/engine/python-engine-spec.md

## 필수 수정
- `GameResult` 값 표현이 training/runtime 계층의 winner 표현과 충돌한다.
  - 근거: [specs/engine/python-engine-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/engine/python-engine-spec.md:43)~[48행]은 `GameResult`를 `BLACK_WIN`, `WHITE_WIN`, `DRAW`로 정의한다.
  - 비교 기준: [specs/training/self-play-data-schema.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/self-play-data-schema.md:58)~[60행]은 episode `winner`를 `BLACK | WHITE | DRAW | null`로 정의한다.
  - 비교 기준: 같은 스키마의 state record도 [118행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/self-play-data-schema.md:118)~[119행]에서 `winner: str | null`만 두고 `*_WIN` 표현은 언급하지 않는다.
  - 문제: engine의 종료 결과를 training/runtime으로 직렬화할 때 `BLACK_WIN`을 그대로 내보낼지 `BLACK`로 변환할지 계층별로 달라질 수 있다.
  - 권장: engine enum 값을 상위 계층과 같은 `BLACK | WHITE | DRAW`로 맞추거나, 변환 규칙을 직렬화 계약에 명시한다.
