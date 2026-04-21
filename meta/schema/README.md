# Meta Schema

이 폴더는 `meta/`에서 사용하는 최소 스키마를 정의한다.

## 스키마 목록
- `code-entity.schema.json`
- `doc-entity.schema.json`
- `test-entity.schema.json`
- `edge.schema.json`
- `compressed-state.schema.json`

## 공통 규칙
- 모든 엔티티는 `entity_id`를 가진다.
- `entity_id`는 저장소 안에서 유일해야 한다.
- 원본 경로는 항상 저장소 루트 기준 상대 경로를 사용한다.
- `meta/` 데이터는 가능하면 JSONL 또는 JSON으로 저장한다.

## 권장 entity id 규칙
- 코드 함수: `code:src/training/trainer.py:Trainer.train`
- 코드 모듈: `code:src/engine/game_engine.py`
- 문서 섹션: `doc:specs/training/trainer-loop-spec.md#checkpoint-save`
- 테스트: `test:tests/unit/training/test_trainer_loop.py:test_save_checkpoint_metadata`
