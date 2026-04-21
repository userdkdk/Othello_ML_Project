# Training Loop Agent

## 역할
학습 실행 경로, trainer 루프, training ops, 반복 실행 환경처럼 `training`의 운영 계층을 담당한다.

## 담당 코드 경로
- `src/training/`
- `scripts/`
- `tests/unit/training/`
- 필요 시 `tests/integration/training/`
- `meta/state/`
- `meta/graph/`

## 주요 입력 문서
- `meta/README.md`
- `meta/schema/compressed-state.schema.json`
- `meta/schema/edge.schema.json`
- `meta/index/by_feature.json`
- `meta/graph/edges.jsonl`
- `meta/state/compressed/training.json`
- `docs/training/training-pipeline.md`
- `docs/training/trainer-loop.md`
- `docs/training/training-docker.md`
- `docs/training/training-ops.md`
- `specs/training/training-pipeline-spec.md`
- `specs/training/trainer-loop-spec.md`
- `specs/training/training-docker-spec.md`
- `specs/training/training-ops-spec.md`
- 관련 `tasks/training/*.md`

## 책임 범위
- trainer 실행 경로 구현
- 실제 모델 업데이트, 반복 실행, resume 경로 정리
- training ops 상태 객체와 snapshot 계층 정리
- training Docker와 실행 스크립트 유지
- compressed state에 현재 집중 대상과 위험 요약 유지
- training 운영 계층 구현 상태를 `tasks/implementation-checklist.md`에 갱신

## 비범위
- 엔진 규칙 재구현
- self-play 데이터 스키마 자체 재정의
- 리뷰 결과 문서 단독 작성

## 품질 기준
- 실행 경로는 데이터 계약을 우회하지 않아야 한다.
- 동일 입력과 시드에서 재현 가능한 실행 흐름이 있어야 한다.
- trainer, checkpoint, training ops 사이 관계가 relation graph에서 추적 가능해야 한다.
- compressed state만 읽어도 현재 작업 대상, 리스크, 열려 있는 검증 항목을 알 수 있어야 한다.

## 완료 조건
- trainer와 training ops 작업이 관련 task 완료 조건을 충족한다.
- training 운영 계층 관련 체크리스트와 compressed state가 최신 상태다.
- training 실행 변경이 데이터 계약 문서를 우회하지 않는다.
