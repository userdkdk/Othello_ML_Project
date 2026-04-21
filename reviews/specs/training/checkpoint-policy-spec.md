# specs/training/checkpoint-policy-spec.md 리뷰

## 축
`training`

## 검토 기준
- `AGENTS.md`
- `agents/review-agent.md`
- `docs/training/checkpoint-policy.md`
- `docs/training/trainer-loop.md`

## 특이사항 없음
- 상위 `docs` 기준의 3트랙 best checkpoint 구조가 spec에 반영되어 있다.
- `latest training checkpoint`가 단일 세션 상태라는 점도 명시돼 있다.
- top-level 평가 메타데이터와 `training_state` 책임 분리가 유지된다.
  - top-level:
    - `black_side_win_rate`
    - `white_side_win_rate`
    - `balanced_eval_score`
    - `track`
  - `training_state`:
    - resume용 누적 상태

## 고려사항
- 구현 시 `track` 식별자를 생략하는 경우에도 파일명 또는 디렉터리 구조 중 하나로 동일한 정보를 추적할 수 있어야 한다.
