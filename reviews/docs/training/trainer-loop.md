# docs/training/trainer-loop.md 리뷰

## 축
`training`

## 검토 기준
- `AGENTS.md`
- `agents/review-agent.md`
- `docs/training/checkpoint-policy.md`

## 권장 수정
- 출력 기준의 `eval_score 또는 동등 평가 메타데이터` 표현은 현재 문서 전반에서 쓰는 `balanced_eval_score` 중심 용어와 다소 느슨하게 연결된다.
  - 현재 문서의 핵심 평가지표는 `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`로 정리되어 있으므로, 출력 기준도 같은 이름 체계로 좁히면 하위 `specs/tasks`가 덜 흔들린다.

## 고려사항
- 3트랙 best 구조(`best_black`, `best_white`, `best_balanced`)와 평균/가중 평균 규칙은 상위 docs 기준으로 충분히 드러난 상태다.
- 하위 `specs/tasks`가 이 구조를 단순화하지 않도록 계속 같은 이름을 유지해야 한다.
