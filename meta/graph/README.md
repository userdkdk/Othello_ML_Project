# Meta Graph

이 폴더는 엔티티 사이 관계를 저장한다.

## 권장 파일
- `nodes.jsonl`
- `edges.jsonl`

## 목적
- 어떤 task가 어떤 spec section을 구현하는지 추적
- 어떤 함수가 어떤 테스트와 연결되는지 추적
- 어떤 endpoint가 어떤 코드 경로를 노출하는지 추적

## 운영 규칙
- edge는 방향성을 가진다.
- relation 타입은 `meta/schema/edge.schema.json`만 사용한다.
- 영향 범위 계산은 보통 `edges.jsonl`에서 시작한다.
