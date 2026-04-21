# Meta Entities

이 폴더는 코드, 문서, 테스트 엔티티를 저장하는 위치다.

## 권장 파일
- `code.jsonl`
- `docs.jsonl`
- `tests.jsonl`

## 저장 규칙
- 한 줄에 한 엔티티를 JSON으로 저장한다.
- 스키마는 `meta/schema/`를 따른다.
- 원본 경로 변경 시 관련 엔티티 id와 edge를 함께 갱신한다.
