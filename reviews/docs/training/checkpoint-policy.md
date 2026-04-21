# docs/training/checkpoint-policy.md 리뷰

## 축
`training`

## 검토 기준
- `AGENTS.md`
- `agents/review-agent.md`
- `docs/training/trainer-loop.md`

## 특이사항 없음
- 현재 상위 docs 기준에서 다음 핵심은 일관되게 정리되어 있다.
  - `latest training checkpoint`는 단일 세션 상태
  - `best_black`, `best_white`, `best_balanced` 트랙 분리
  - top-level 평가 메타데이터
  - `track` 식별 방향
  - `balanced_eval_score`의 평균/가중 평균 규칙

## 고려사항
- 하위 `specs/tasks`에서도 top-level 평가 메타데이터 이름과 `track` 식별 방향을 그대로 유지해야 한다.
