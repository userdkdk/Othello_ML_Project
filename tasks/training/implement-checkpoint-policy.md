# Checkpoint 구현 작업 지시서

## 목적
CNN 정책 모델의 체크포인트 저장/로드 정책을 문서 기준에 맞게 정리하고 최소 구현 경로를 고정한다.

## 선행 입력
- `docs/training/checkpoint-policy.md`
- `docs/training/cnn-policy.md`
- `specs/training/checkpoint-policy-spec.md`
- `specs/training/cnn-model-spec.md`
- `agents/training-data-agent.md`

## 필수 작업
- `inference checkpoint`와 `training checkpoint` 구분 구현 또는 문서화
- `latest training checkpoint`와 3트랙 best checkpoint 구분 구현 또는 문서화
- 체크포인트 로드 입력 형태 검증
- dict payload 키 우선순위 검증
- 모델 버전 해석 규칙 정리
- 호출자 인자와 checkpoint 메타데이터의 우선순위 정리
- 필요 시 `model_kwargs` 복원 경로 정리
- `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`의 top-level 저장 경로 정리
- 필요 시 `track` 식별자의 top-level 저장 경로 정리
- `training_state`와 top-level 평가 메타데이터의 책임 분리
- 로드 결과가 self-play와 evaluator에 연결 가능한지 검증
- 권장 dict payload 저장 helper 초안 추가 또는 저장 포맷 문서화
- 체크포인트 오류 처리 검증

## 완료 조건
- 순수 `state_dict`와 `model_state_dict` dict 형식을 처리할 수 있다.
- `model_state_dict`와 `state_dict`가 함께 있으면 우선순위가 명확하다.
- 모델 버전이 agent `version`과 연결된다.
- 호출자 `version`과 checkpoint `model_version`의 우선순위가 문서와 테스트에서 드러난다.
- 필요 시 `model_kwargs` 복원 우선순위가 문서와 구현에서 드러난다.
- `latest training checkpoint`와 `best_black`, `best_white`, `best_balanced`가 구분된다.
- `black_side_win_rate`, `white_side_win_rate`, `balanced_eval_score`가 checkpoint top-level 메타데이터로 기록되는지 드러난다.
- 필요 시 `track` 식별자 저장 위치가 문서와 구현에서 일치한다.
- `training_state`와 top-level 평가 메타데이터 저장 위치가 문서와 구현에서 일치한다.
- 잘못된 체크포인트는 명시적으로 실패한다.
- 최소 단위 테스트가 포함된다.
