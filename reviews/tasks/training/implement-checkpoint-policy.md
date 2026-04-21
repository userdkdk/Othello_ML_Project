# tasks/training/implement-checkpoint-policy.md 리뷰

## 축
`training`

## 검토 기준
- `AGENTS.md`
- `agents/review-agent.md`
- `docs/training/checkpoint-policy.md`
- `specs/training/checkpoint-policy-spec.md`

## 특이사항 없음
- task가 `latest training checkpoint`와 3트랙 best checkpoint를 구분하고 있다.
- top-level 평가 메타데이터도 현재 상위 문서 기준과 정합한다.
  - `black_side_win_rate`
  - `white_side_win_rate`
  - `balanced_eval_score`
  - 필요 시 `track`
- `training_state`와 top-level metadata 책임 분리도 task에 내려와 있다.

## 고려사항
- 구현 시 실제 payload에서 `track`을 쓸지, 파일명 suffix로만 표현할지 최종 선택이 필요하다.
