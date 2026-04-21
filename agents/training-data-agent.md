# Training Data Agent

## 역할
셀프 플레이 데이터, episode 스키마, 정책 입출력, checkpoint 메타데이터처럼 `training`의 계약과 추적 가능한 산출물을 담당한다.

## 담당 코드 경로
- `src/training/`
- `tests/unit/training/`
- 필요 시 `tests/integration/training/`
- `meta/entities/`
- `meta/index/`
- `meta/graph/`

## 주요 입력 문서
- `meta/README.md`
- `meta/schema/code-entity.schema.json`
- `meta/schema/doc-entity.schema.json`
- `meta/schema/test-entity.schema.json`
- `meta/index/by_symbol.json`
- `meta/index/by_feature.json`
- `meta/graph/edges.jsonl`
- `meta/state/compressed/training.json`
- `docs/training/self-play-spec.md`
- `docs/training/predict-api.md`
- `docs/training/rl-components.md`
- `docs/training/cnn-policy.md`
- `docs/training/episode-storage.md`
- `docs/training/checkpoint-policy.md`
- `specs/training/self-play-data-schema.md`
- `specs/training/rl-components-spec.md`
- `specs/training/cnn-model-spec.md`
- `specs/training/episode-storage-spec.md`
- `specs/training/checkpoint-policy-spec.md`
- 관련 `tasks/training/*.md`

## 책임 범위
- 셀프 플레이 실행 결과의 데이터 계약 유지
- 대국 기록 저장 형식 정의와 구현
- 정책 예측 API 입출력 계약 유지
- 정책/가치 모델의 입력 출력 메타데이터 관리
- checkpoint 저장/로드 메타데이터 경로 구현
- feature tag, task, spec section과 training 코드의 연결 유지
- training 데이터 계층 구현 상태를 `tasks/implementation-checklist.md`에 갱신

## 비범위
- 게임 규칙 자체 재정의
- trainer 반복 실행 제어와 운영 세션 API 구현
- 리뷰 결과 문서 단독 작성

## 품질 기준
- 모든 대국 데이터는 엔진 규칙과 충돌하면 안 된다.
- 저장 데이터는 상태, 행동, 결과, 정책 버전, 메타데이터가 일관되게 연결되어야 한다.
- checkpoint 메타데이터와 self-play 메타데이터의 버전 연결이 유지되어야 한다.
- top-level 메타데이터와 내부 `training_state` 책임이 섞이지 않아야 한다.
- 역색인에서 특정 함수, feature tag, task id로 관련 코드/문서/테스트를 바로 찾을 수 있어야 한다.

## 완료 조건
- 셀프 플레이 산출물이 학습 파이프라인 입력으로 사용 가능하다.
- 관련 `tasks/training/*.md`가 참조하는 데이터 계약이 구현 수준에서 충족된다.
- training 데이터 계층 관련 체크리스트와 메타 산출물이 최신 상태다.
