# Agents Index

이 폴더는 역할별 전문 agent 문서를 둔다.

## 역할 구분
- `engine-agent.md`
- `training-data-agent.md`
- `training-loop-agent.md`
- `runtime-agent.md`
- `governance-agent.md`

## 선택 기준
- 엔진 규칙, 테스트, 상태 전이는 `engine-agent.md`
- self-play 데이터, episode 스키마, checkpoint 메타데이터, 정책 입출력 계약은 `training-data-agent.md`
- trainer 실행 경로, training ops, 반복 실행 환경, 파이프라인 운영은 `training-loop-agent.md`
- FastAPI, Docker, 웹 UI는 `runtime-agent.md`
- 문서 정합성, 리뷰 형식, 체크리스트 구조, 메타 구조 운영은 `governance-agent.md`

## 재편 원칙
- 과잉 분리였던 `spec-agent`, `review-agent`, `checklist-agent`는 `governance-agent`로 병합한다.
- 범위가 과도하게 넓었던 `training-agent`는 `training-data-agent`와 `training-loop-agent`로 분리한다.
- agent는 문서 상속을 따라 내려가기보다 `meta/index`, `meta/graph`, `meta/state/compressed`를 먼저 사용해 직접 관련 노드만 읽는다.

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `meta/README.md`
4. 관련 `meta/state/`, `meta/index/`, `meta/graph/`
5. 관련 `docs/`
6. 관련 `specs/`
7. 해당 `agents/*.md`
8. 관련 `tasks/`
