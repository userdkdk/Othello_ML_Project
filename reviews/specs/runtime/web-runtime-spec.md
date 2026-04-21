# Review: specs/runtime/web-runtime-spec.md

## 필수 수정
- `model_vs_model` 관전 진행을 요구하면서도 이를 트리거할 API 계약이 없다.
  - 근거: [specs/runtime/web-runtime-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/web-runtime-spec.md:41)는 `model_vs_model`일 때 관전 진행 버튼 또는 자동 진행 제어를 요구한다.
  - 근거: 같은 문서 [46행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/web-runtime-spec.md:46)~[49행]은 runtime이 모델 턴을 계산해 진행해야 하며, 사람 턴이 아닌데 `POST /api/move`가 호출되면 실패해야 한다고 적는다.
  - 근거: 그런데 최소 엔드포인트는 [11행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/web-runtime-spec.md:11)~[16행]의 `/api/state`, `/api/new`, `/api/move`, `/api/pass`뿐이다.
  - 문제: 사람이 아닌 턴에는 `/api/move`를 쓸 수 없는데, 모델 턴을 한 수 진행시키는 별도 endpoint가 없어 `model_vs_model` 수동 관전 경로가 계약상 성립하지 않는다.
  - 권장: `POST /api/step`, `POST /api/advance`, `POST /api/auto-play` 같은 모델 진행 endpoint를 추가하거나, `/api/move`의 허용 의미를 모드별로 재정의해야 한다.
