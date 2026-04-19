# 프로젝트 구조 명세

## 목적
이 문서는 Python 프로젝트의 패키지 구조와 계층 경계를 정의한다.

## 목표 구조

```text
src/
  engine/
    __init__.py
    types.py
    board.py
    move_validator.py
    game_engine.py
  training/
    __init__.py
    self_play.py
    data_schema.py
    policy_client.py
  api/
    __init__.py
    fastapi_app.py
tests/
  unit/
    engine/
    training/
  integration/
    engine/
    training/
specs/
docs/
tasks/
agents/
reviews/
prompts/
```

## 계층 원칙

### `src/engine`
- 순수 도메인 계층
- 오셀로 규칙과 상태 변화만 다룬다
- 외부 I/O 없음
- FastAPI, DB, 파일 저장, 모델 서버 호출 의존 금지

### `src/training`
- 엔진을 사용해 셀프 플레이와 데이터 생성 수행
- 저장 포맷 변환
- 정책 출력 연결
- 엔진 규칙 재구현 금지

### `src/api`
- 엔진 또는 학습 계층을 외부에서 호출하기 위한 어댑터
- 현재 후보는 FastAPI
- API 레이어는 요청/응답 변환만 담당하고 규칙 계산은 `engine` 또는 `training`에 위임

## import 방향
- `engine` -> 다른 프로젝트 계층 import 금지
- `training` -> `engine` import 가능
- `api` -> `engine`, `training` import 가능
- 테스트는 대상 계층 import 가능

허용 방향:

```text
api -> training -> engine
api -> engine
tests -> api/training/engine
```

금지 방향:

```text
engine -> training
engine -> api
training -> api
```

## 패키지별 책임

### `src/engine/types.py`
- enum
- dataclass
- type alias

### `src/engine/board.py`
- 보드 표현
- 범위 확인
- 칸 조회/복사/직렬화

### `src/engine/move_validator.py`
- 유효 수 계산
- 뒤집기 대상 계산
- 방향 계산

### `src/engine/game_engine.py`
- 새 게임 생성
- 수 적용
- 패스
- 종료/승패 판정

### `src/training/self_play.py`
- 반복 대국 실행
- 정책 호출
- 결과 수집

### `src/training/data_schema.py`
- 저장용 dict 변환
- JSONL/Parquet 직렬화 준비

### `src/training/policy_client.py`
- 정책 인터페이스 추상화
- 랜덤 정책, 휴리스틱 정책, 모델 정책 래퍼

### `src/api/fastapi_app.py`
- FastAPI app 생성
- 엔진/학습 계층 호출
- 요청/응답 스키마 연결

## 테스트 구조

### `tests/unit/engine`
- `board`, `move_validator`, `game_engine` 단위 테스트

### `tests/unit/training`
- 셀프 플레이 단위 테스트
- 스키마 직렬화 테스트

### `tests/integration/engine`
- 초기 상태부터 종료까지 통합 시나리오
- 인수 테스트 문서 매핑

### `tests/integration/training`
- 정책 stub와 함께 한두 판 셀프 플레이 실행
- 완료 대국/실패 대국 저장 검증

## 실행 엔트리포인트 후보
- 단위 테스트: `pytest`
- 로컬 API 실행: `src/api/fastapi_app.py`
- 셀프 플레이 배치 실행: `src/training/self_play.py` 또는 별도 CLI 래퍼

## 의존성 관리 원칙
- 최소 시작 의존성:
  - Python 3.11+
  - `pytest`
- API 시작 시 추가 가능:
  - `fastapi`
  - `uvicorn`
- 데이터 포맷 확장 시 추가 가능:
  - `pydantic`
  - `pyarrow`

## 구현 순서
1. `src/engine`
2. `tests/unit/engine`
3. `tests/integration/engine`
4. `src/training`
5. `tests/unit/training`
6. `tests/integration/training`
7. `src/api`

## 결정 사항
- 첫 구현 언어는 Python
- 첫 API 후보는 FastAPI지만, 엔진 코어는 API 프레임워크에 의존하지 않는다
- `src/engine`는 이후 다른 인터페이스에서도 재사용 가능한 라이브러리 형태로 유지한다
