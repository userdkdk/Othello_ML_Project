# Episode 저장 명세 작성 작업 지시서

## 목적
`training` 계층의 episode 저장기 입력/출력/오류 계약을 구현 직전 수준으로 명세한다.

## 선행 입력
- `docs/training/episode-storage.md`
- `docs/training/training-pipeline.md`
- `specs/training/self-play-data-schema.md`
- `agents/governance-agent.md`

## 필수 작업
- episode 저장 모듈의 최소 공개 함수 경로 정의
- JSONL 기본 저장 규약 정의
- `Episode` 입력과 dict 입력 정규화 계약 정의
- 부분 저장 실패와 `written_count` 규약 정의
- 기본 저장 출력과 스키마 최소 필드 관계 정의

## 출력 파일
- `specs/training/episode-storage-spec.md`

## 완료 조건
- 구현자가 writer 함수 시그니처와 기본 동작을 바로 정할 수 있을 정도로 계약이 명확하다.
- JSONL 한 줄 = episode 규약이 문서화되어 있다.
- 부분 저장 실패 시 호출자가 어떤 정보를 받는지 명확하다.
- `Episode.to_dict()` 기반 출력과 저장 스키마 최소 필드 관계가 정리되어 있다.
