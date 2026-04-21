# 학습 대시보드 구현 작업 지시서

## 목적
`runtime` 계층에서 학습 제어, 상태 조회, checkpoint 비교를 제공하는 별도 운영 UI와 API를 구현한다.

## 선행 입력
- `docs/runtime/training-dashboard.md`
- `docs/runtime/runtime-overview.md`
- `docs/training/training-ops.md`
- `specs/runtime/training-dashboard-spec.md`
- `specs/runtime/web-runtime-spec.md`
- `specs/training/training-ops-spec.md`
- `agents/runtime-agent.md`

## 필수 작업
- 게임 플레이 UI와 분리된 학습 대시보드 경로 구현
- `/api/training` namespace API 구현
- `GET /api/training/state` 구현
- `POST /api/training/start` 구현
- `POST /api/training/start-from-checkpoint` 구현
- `POST /api/training/run-once` 구현
- `POST /api/training/pause` 구현
- `POST /api/training/resume-session` 구현
- `POST /api/training/stop` 구현
- `POST /api/training/compare` 구현
- `GET /api/training/comparisons/latest` 구현
- 학습 세션 상태, 최근 iteration, checkpoint inventory, 마지막 비교 결과를 표시하는 UI 구현
- 긴 작업 중 버튼 상태와 오류 표시 구현
- polling 기반 상태 갱신 또는 동등한 갱신 흐름 구현
- 최소 단위 테스트 또는 API 테스트 보강

## 완료 조건
- 기본 게임 UI와 학습 대시보드 UI가 경로와 상태 모델 기준으로 분리된다.
- 빈 세션 상태에서도 `/api/training/state`가 `session.status = idle`을 포함한 일관된 응답을 반환한다.
- paused 세션 재개와 checkpoint 기반 새 세션 시작 API가 분리된다.
- 학습 대시보드에서 세션 상태, 현재 단계, iteration 번호, 최근 loss, 평가 점수, 승격 track, checkpoint inventory를 확인할 수 있다.
- checkpoint 비교 요청과 마지막 비교 결과 조회가 동작한다.
- 비교 기본 입력이 inference checkpoint라는 점이 UI와 API에서 드러난다.
- 오류 응답이 `error_code`, `message` 형태로 노출된다.
- 관련 테스트가 포함된다.
