# Meta Index

이 폴더는 빠른 조회를 위한 역색인을 저장한다.

## 권장 파일
- `by_symbol.json`
- `by_feature.json`
- `by_task.json`
- `by_endpoint.json`

## 예시
- `by_symbol.json`
  - 함수나 클래스 이름으로 관련 entity id 목록 조회
- `by_feature.json`
  - feature tag로 관련 코드, 문서, 테스트 조회
- `by_task.json`
  - task 경로로 연결된 spec, code, test 조회
- `by_endpoint.json`
  - API endpoint로 런타임 영향 범위 조회
