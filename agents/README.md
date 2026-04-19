# Agents Index

이 폴더는 역할별 전문 agent 문서를 둔다.

## 역할 구분
- `engine-agent.md`
- `training-agent.md`
- `runtime-agent.md`
- `spec-agent.md`
- `review-agent.md`

## 선택 기준
- 엔진 규칙, 테스트, 상태 전이는 `engine-agent.md`
- self-play, agent, evaluator, trainer는 `training-agent.md`
- FastAPI, Docker, 웹 UI는 `runtime-agent.md`
- 새 명세 문서 작성은 `spec-agent.md`
- 문서나 코드 검토는 `review-agent.md`

## 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. 관련 `docs/`
4. 관련 `specs/`
5. 해당 `agents/*.md`
6. 관련 `tasks/`
