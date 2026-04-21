# Training 구현 우선순위 명세

## 목적
이 문서는 `training` 구현 작업의 권장 순서와 선후 의존 관계를 작업 계약 수준에서 정의한다.

## 관련 문서
- `docs/training/implementation-priority.md`
- `docs/training/training-pipeline.md`
- `specs/training/training-pipeline-spec.md`
- `tasks/training/*.md`

## 우선순위 계약
- `training` 구현의 기본 권장 순서는 다음과 같아야 한다.
  1. `implement-training-pipeline`
  2. `implement-episode-storage`
  3. `implement-cnn-policy-model`
  4. `implement-checkpoint-policy`
  5. `implement-trainer-loop`
  6. `implement-training-ops`
  7. `implement-training-docker`

## 의존 계약
- `implement-episode-storage`는 `Episode`와 `Episode.to_dict()` 경계가 안정된 뒤 진행하는 것을 기본값으로 한다.
- `implement-checkpoint-policy`는 CNN 정책 모델의 버전 메타데이터와 로드 경로가 정의된 뒤 진행하는 것을 기본값으로 한다.
- `implement-trainer-loop`는 다음 작업의 핵심 계약이 먼저 고정된 뒤 진행하는 것을 기본값으로 한다.
  - `implement-training-pipeline`
  - `implement-episode-storage`
  - `implement-cnn-policy-model`
  - `implement-checkpoint-policy`
- `implement-training-ops`는 다음 작업의 핵심 계약이 먼저 고정된 뒤 진행하는 것을 기본값으로 한다.
  - `implement-checkpoint-policy`
  - `implement-trainer-loop`
- `implement-training-docker`는 trainer-loop와 training-ops를 포함한 training 실행 경로를 통합 검증할 수 있는 시점에 정리하는 것을 기본값으로 한다.

## 검증 계약
- 우선순위 문서는 단순 추천이 아니라, 왜 뒤 작업이 앞 작업의 산출물에 의존하는지 설명 가능해야 한다.
- 구현 순서를 바꿀 경우 어떤 계약이 아직 불안정한지 문서나 리뷰에 남길 수 있어야 한다.

## 비범위
- 세부 일정 추정
- 작업자 수 배분
- 병렬 개발 도구 선택
