# Episode 저장 구현 작업 지시서

## 목적
self-play 결과를 `self-play-data-schema` 기준으로 파일에 기록할 수 있는 기본 episode 저장 경로를 구현한다.

## 선행 입력
- `docs/training/episode-storage.md`
- `docs/training/training-pipeline.md`
- `specs/training/episode-storage-spec.md`
- `specs/training/self-play-data-schema.md`
- `agents/training-data-agent.md`

## 필수 작업
- episode 저장 모듈 추가
- `Episode` iterable을 JSONL 기본 포맷으로 저장하는 경로 구현
- 저장 입력을 `Episode.to_dict()` 기준으로 정규화하는 경로 구현
- 저장 순서 보존
- 기본 파일 모드와 append 모드 정책 정리
- `completed`와 `failed` episode 저장 검증
- 부분 저장 실패 시 의미가 호출부와 테스트에서 드러나게 하기
- 기본 저장 출력이 `self-play-data-schema.md`와 정합하는지 검증

## 완료 조건
- 여러 episode를 파일에 순서대로 저장할 수 있다.
- 저장 출력은 `Episode.to_dict()` 기준 필드를 유지한다.
- 각 JSONL 줄이 하나의 episode object로 저장된다.
- UTF-8 텍스트와 줄 경계 규약이 유지된다.
- `encoded_state`가 기본 저장 출력에 포함되지 않는다는 점이 드러난다.
- 현재 `Episode.to_dict()`가 가진 `valid_moves`, `action_mask`를 writer가 임의로 변경하지 않는다.
- 실패 episode도 디버깅용으로 저장 가능하다.
- 부분 저장 실패 또는 예외 전달 규칙이 문서와 테스트에서 드러난다.
- 최소 단위 테스트가 포함된다.
