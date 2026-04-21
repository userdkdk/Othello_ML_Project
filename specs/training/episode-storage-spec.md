# Episode 저장 명세

## 목적
이 문서는 `training` 계층의 episode 저장기가 따라야 할 최소 파일/함수 계약을 정의한다.

## 관련 문서
- `docs/training/episode-storage.md`
- `specs/training/self-play-data-schema.md`
- `specs/training/training-pipeline-spec.md`

## 구현 대상
- `src/training/` 아래 episode 저장 모듈
- JSONL 또는 동등 기본 저장 경로

## 최소 공개 계약
- 저장 계층은 `Episode` iterable을 직접 받는 기본 경로를 제공해야 한다.
- 필요하면 직렬화 가능한 dict iterable을 받는 보조 경로를 제공할 수 있다.
- 기본 저장 출력은 `self-play-data-schema.md`에 정의된 최소 필드를 만족해야 한다.
- 저장 순서는 입력 episode 순서를 보존해야 한다.

## 권장 함수 경로
- 기본 writer는 다음과 같은 성격의 함수를 권장한다.
  - `write_episodes_jsonl(path, episodes, mode="w")`
- 입력 `episodes`는 iterable이어야 한다.
- `mode` 기본값은 덮어쓰기 성격의 `"w"`여야 한다.
- append를 허용하면 `"a"`만 허용하는 식으로 범위를 좁히는 편이 낫다.

## 기본 저장 계약
- 기본 포맷은 JSONL을 허용해야 한다.
- 각 줄은 하나의 episode dict여야 한다.
- UTF-8 텍스트 출력이어야 한다.
- `completed`와 `failed` episode를 모두 저장할 수 있어야 한다.
- 멀티라인 pretty JSON은 기본 출력으로 허용하지 않는다.
- 저장 구현은 각 episode 뒤에 줄바꿈 하나를 기록해야 한다.

## 필드 계약
- 저장 출력은 최소한 다음 필드를 보존해야 한다.
  - `episode_id`
  - `status`
  - `seed`
  - `policy_black_version`
  - `policy_white_version`
  - `started_at`
  - `finished_at`
  - `reward_perspective`
  - `final_reward`
  - `winner`
  - `turns`
  - `failure`
- 위 필드는 최소 요구 필드다.
- 구현은 현재 `Episode.to_dict()`가 제공하는 추가 필드를 함께 보존할 수 있다.

## 입력 정규화 계약
- `Episode` 입력은 저장 직전에 `episode.to_dict()`로 정규화할 수 있어야 한다.
- dict 입력을 허용한다면 writer는 dict를 다시 해석하거나 reward를 재계산하면 안 된다.
- 기본 writer는 입력 episode를 재정렬하면 안 된다.

## 경계 계약
- 저장 계층은 `Episode.finalize()`를 대신 수행하지 않는다.
- 저장 계층은 reward를 새로 계산하지 않는다.
- 저장 계층은 메모리상 `encoded_state`를 기본 출력에 강제로 포함하지 않는다.
- 저장 계층은 현재 `Episode.to_dict()`에 존재하는 `valid_moves`, `action_mask`를 임의 삭제하거나 재계산하지 않는 것을 기본값으로 한다.
- 따라서 현재 기본 writer 출력은 `self-play-data-schema` 최소 필드 집합의 상위호환일 수 있다.

## 오류 계약
- 파일 열기 또는 쓰기 실패는 호출자에게 드러나야 한다.
- 부분 저장을 허용하면 마지막으로 성공한 episode 경계를 식별 가능해야 한다.
- 기본 저장 의미는 non-transactional append/write다.
- 따라서 일부 episode가 이미 기록된 뒤 실패할 수 있다는 점이 호출자에게 문서화되어야 한다.
- 전체 원자성 보장은 별도 구현 전략이 없는 한 기본 계약에 포함하지 않는다.

## 반환 계약
- writer는 최소한 `written_count: int` 또는 동등 정보를 반환해야 한다.
- 예외가 발생하면 호출자는 최소한 마지막으로 완전히 기록된 episode 수를 식별 가능해야 한다.

## 비범위
- 원격 저장소 API
- Parquet writer 세부 구현
