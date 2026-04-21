# specs/training/trainer-loop-spec.md 리뷰

## 축
`training`

## 검토 기준
- `AGENTS.md`
- `agents/review-agent.md`
- `docs/training/trainer-loop.md`
- `docs/training/checkpoint-policy.md`

## 특이사항 없음
- 상위 `docs`에서 정의한 3트랙 best 구조가 spec까지 일관되게 내려왔다.
  - `best_black`
  - `best_white`
  - `best_balanced`
- 평가 메타데이터도 상위 문서 기준과 정합한다.
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
- `balanced_eval_score`의 평균/가중 평균 규칙도 spec에 직접 드러난다.

## 고려사항
- 이후 구현 시 `promoted_tracks` 같은 리포트 필드 이름을 코드에서도 동일하게 유지해야 한다.
