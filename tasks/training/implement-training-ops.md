# 학습 운영 구현 작업 지시서

## 목적
`training` 계층에서 학습 세션 제어, iteration 실행, 대시보드용 상태 스냅샷, checkpoint 비교 기능을 문서 기준에 맞게 구현 가능한 작업 단위로 고정한다.

## 선행 입력
- `docs/training/training-ops.md`
- `docs/training/trainer-loop.md`
- `docs/training/checkpoint-policy.md`
- `specs/training/training-ops-spec.md`
- `specs/training/trainer-loop-spec.md`
- `specs/training/checkpoint-policy-spec.md`
- `agents/training-loop-agent.md`

## 필수 작업
- 학습 세션 상태 객체 구현
- 세션 상태 전이 규칙 구현 또는 검증
- `start`, `pause`, `resume_session`, `stop` 제어 경로 구현
- `start_from_checkpoint` 경로 구현 또는 정리
- iteration 실행기 구현
- iteration 단계별 진행 상태와 오류 상태 추적 구현
- 대시보드용 경량 상태 스냅샷 직렬화 구현
- checkpoint inventory 구성 로직 구현
- checkpoint 비교 실행기 구현
- 비교 결과를 left checkpoint 관점 리포트로 직렬화
- 실패 시 명시적 오류 경로와 상태 보존 검증
- 최소 단위 테스트 보강

## 완료 조건
- 학습 세션이 `idle`, `running`, `pause_requested`, `paused`, `completed`, `failed`, `stopped` 상태를 일관되게 표현한다.
- paused 세션 재개와 checkpoint 기반 새 세션 시작이 다른 경로로 구분된다.
- iteration 실행 결과에 self-play 통계, training report, 평가 결과, 승격 track이 연결된다.
- 대시보드 조회용 payload가 raw episode 전체를 다시 내보내지 않는다.
- checkpoint inventory가 training/inference 슬롯을 구분해 표현한다.
- checkpoint 비교가 양방향 평가를 수행하고 left checkpoint 관점 결과를 반환한다.
- 존재하지 않는 checkpoint와 로드 실패가 명시적으로 드러난다.
- 관련 단위 테스트가 포함된다.
