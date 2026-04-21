# Episode 저장 기준

## 목적
이 문서는 self-play 결과를 파일로 저장할 때 따를 `episode` 저장 기준을 정의한다.

현재 구현은 `Episode.to_dict()` 수준의 직렬화 경로만 가진다. 이 문서는 향후 JSONL 또는 동등 저장기를 붙일 때 어떤 단위와 책임으로 저장할지 상위 기준을 고정한다.

## 적용 범위
- `src/training/`의 episode 저장기
- `Episode.to_dict()` 결과를 파일에 쓰는 계층
- 향후 JSONL 또는 Parquet 변환 진입점

## 저장 단위 기준
- 기본 저장 단위는 `episode`다.
- 한 줄 또는 한 레코드는 하나의 `episode`를 표현해야 한다.
- 기본 저장 형식은 `specs/training/self-play-data-schema.md`를 따라야 한다.

## 책임 분리 기준
- self-play 실행 계층은 `Episode`를 생성한다.
- 저장 계층은 `Episode` 또는 직렬화 가능한 dict를 파일로 기록한다.
- 저장 계층이 엔진 규칙이나 보상 기준을 다시 계산하면 안 된다.
- 기본 저장 계층은 `Episode.to_dict()`를 신뢰하는 얇은 writer 계층으로 두는 것을 권장한다.

## 공개 API 방향
- 기본 저장기는 `Episode` iterable을 직접 받는 경로를 우선 제공하는 것을 권장한다.
- 필요하면 이미 직렬화된 episode dict iterable을 받는 보조 경로를 둘 수 있다.
- 기본 저장기는 단일 episode 저장보다 다수 episode 순차 저장을 우선 지원해야 한다.

## 파일 모드 기준
- 기본 파일 모드는 새 파일 작성 또는 덮어쓰기다.
- 필요하면 append 모드를 둘 수 있지만, append 시에도 JSONL 한 줄 = episode 규약을 깨면 안 된다.
- 동일 파일에 여러 번 append할 때는 줄 경계가 깨지지 않아야 한다.

## 기본 출력 기준
- 기본 출력은 `completed`와 `failed` episode를 구분 가능해야 한다.
- 시간, 시드, 정책 버전, 최종 보상, 실패 정보가 보존되어야 한다.
- 기본 출력은 `self-play-data-schema.md`의 최소 필드 계약과 정합해야 한다.
- 기본 JSONL 출력은 각 episode를 한 줄의 독립 JSON object로 기록해야 한다.

## JSONL 기준
- 문자 인코딩은 UTF-8을 기본값으로 한다.
- 각 episode 뒤에는 줄바꿈 하나를 둔다.
- 한 줄 안에는 정확히 하나의 episode object만 있어야 한다.
- pretty-print 또는 멀티라인 JSON은 기본값으로 사용하지 않는다.

## 메모리상 필드와 저장 필드의 경계
- 메모리상 `TurnRecord`는 `encoded_state`, `action_mask`, `valid_moves`를 포함할 수 있다.
- 기본 저장 출력은 이 메모리상 필드를 그대로 모두 내보내는 계층이 아니다.
- 현재 기본 저장 출력에는 `encoded_state`가 포함되지 않는다.
- 현재 구현의 `TurnRecord.to_dict()`는 `valid_moves`와 `action_mask`를 포함한다.
- `self-play-data-schema.md`는 기본 저장 출력이 반드시 가져야 할 최소 필드를 정의한다.
- 따라서 현재 writer의 기본 출력은 `self-play-data-schema.md` 최소 필드를 만족하는 상위호환 출력으로 해석한다.
- 저장기는 현재 `Episode.to_dict()` 출력에서 `valid_moves`, `action_mask`를 임의 삭제하지 않는 것을 기본값으로 둔다.
- 추가 저장 필드가 필요하면 기본 스키마 확장 작업으로 분리해야 한다.

## 운영 기준
- 여러 episode를 이어서 저장할 수 있어야 한다.
- 저장 실패 시 어떤 episode까지 기록되었는지 구분 가능해야 한다.
- 기본 저장기와 후속 변환기 역할은 분리할 수 있다.
- 부분 저장을 허용하면 "마지막으로 완전히 기록된 episode" 경계를 호출자가 식별 가능해야 한다.
- 저장기는 성공한 episode를 자동 롤백하지 않는 방향을 기본값으로 둔다.
- 원자적 전체 저장이 필요하면 임시 파일 후 rename 같은 별도 전략으로 분리한다.
- 기본 writer는 마지막 성공 경계를 `written_count` 반환값으로 드러내는 것을 권장한다.

## 부분 저장 실패 기준
- episode 단위 쓰기 중 파일 열기 실패, JSON 직렬화 실패, 쓰기 실패가 호출자에게 드러나야 한다.
- N개 episode 중 K개를 성공적으로 기록한 뒤 실패하면, 기본 의미는 "앞의 K개는 파일에 남을 수 있음"이다.
- 기본 writer는 가능하면 예외와 함께 `written_count`를 식별 가능한 방식으로 제공해야 한다.
- 호출자는 저장 결과를 바탕으로 재시도 또는 후처리를 결정할 수 있어야 한다.

## 구현 우선순위 기준
- 1단계 기본 구현은 `Episode` iterable -> JSONL file writer다.
- dict iterable writer, append 모드, Parquet 변환기는 그 다음 확장으로 본다.

## 비범위
- Parquet 최종 컬럼 설계
- 데이터 압축 전략
- 원격 object storage 업로드 방식
