# Training Docs

`training` 영역은 엔진 규칙 위에서 데이터 생성과 평가를 정의한다.

## 읽는 순서
1. `self-play-spec.md`
2. `predict-api.md`
3. `rl-components.md`

## 파일 역할
- `self-play-spec.md`
  - self-play 범위, 보상 기준, 시작 상태 제약
- `predict-api.md`
  - `(row, col)` / `PASS` 행동 표현과 정책 분포 규약
- `rl-components.md`
  - match runner, agent, encoder, evaluator 등 구성요소 책임
