# Meta State

이 폴더는 agent가 전체 문서를 다시 읽지 않도록 현재 작업 상태를 압축해 저장한다.

## 구조
- `compressed/`
  - `engine.json`
  - `training.json`
  - `runtime.json`

## 사용 기준
- 현재 집중 대상
- 직접 연결된 spec, task, test
- 가까운 이웃 노드
- 리스크 요약
- 아직 확인되지 않은 검증 항목
