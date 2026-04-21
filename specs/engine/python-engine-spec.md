# Python 엔진 명세

## 목적
이 문서는 `src/engine`에 구현할 Python 오셀로 엔진의 상세 설계를 정의한다.

엔진 코어는 웹 프레임워크와 분리된 순수 Python 패키지여야 하며, FastAPI 같은 API 레이어는 이후 별도 계층에서 이 엔진을 호출한다.

## 구현 대상 경로
- `src/engine/types.py`
- `src/engine/board.py`
- `src/engine/move_validator.py`
- `src/engine/game_engine.py`
- `src/engine/__init__.py`

## 설계 원칙
- 엔진 코어는 FastAPI, DB, 네트워크 I/O에 의존하지 않는다.
- 좌표는 `(row, col)` 튜플 형식을 사용한다.
- 실패는 예외 또는 명시적 실패 결과로 표현할 수 있지만, 상태 불변은 반드시 유지해야 한다.
- `board`는 순수 상태 표현만 담당한다.
- `move_validator`는 상태를 변경하지 않는다.
- `game_engine`만 게임 상태를 변경한다.
- 프로젝트 import 기준은 `src`를 source root로 두는 방식으로 고정한다.
  - 예: `from engine.game_engine import create_new_game`

## 핵심 타입

### `CellState`
`Enum`

- `EMPTY`
- `BLACK`
- `WHITE`

### `Player`
`Enum`

- `BLACK`
- `WHITE`

### `Position`
`TypeAlias = tuple[int, int]`

### `GameResult`
`Enum`

- `BLACK`
- `WHITE`
- `DRAW`

### `GameStatus`
`dataclass`

필수 필드:
- `is_finished: bool`
- `winner: GameResult | None`

### `MoveErrorCode`
`Enum`

- `OUT_OF_BOUNDS`
- `CELL_NOT_EMPTY`
- `NO_FLIPS`
- `GAME_ALREADY_FINISHED`
- `PASS_NOT_ALLOWED`

### `MoveResult`
`dataclass`

필수 필드:
- `success: bool`
- `applied_move: Position | None`
- `applied_player: Player | None`
- `flipped_positions: list[Position]`
- `next_player: Player | None`
- `status: GameStatus`
- `error_code: MoveErrorCode | None`

### `GameState`
`dataclass`

필수 필드:
- `board: Board`
- `current_player: Player`
- `status: GameStatus`

선택 필드:
- `move_history: list[Position | str]`
- `last_move: Position | str | None`

권장 메서드:
- `clone() -> GameState`
  - training 계층에서 agent 호출 시 원본 상태와 분리된 스냅샷을 넘길 수 있어야 한다.
  - 구현이 메서드 대신 동등한 복제 helper를 택하더라도 외부 계약상 clone 가능한 상태여야 한다.

## 모듈별 책임

### `types.py`
- 공통 enum, dataclass, type alias 정의

### `board.py`
- `Board` 클래스 정의
- 8x8 상태 보관
- 범위 확인
- 칸 조회
- 칸 갱신
- 돌 개수 계산
- 직렬화용 스냅샷 추출

### `move_validator.py`
- 단일 좌표 유효성 검사
- 특정 좌표에서 뒤집히는 방향 계산
- 특정 좌표에서 뒤집히는 좌표 목록 계산
- 전체 유효 수 목록 계산

### `game_engine.py`
- 초기 게임 생성
- 수 적용
- 패스 처리
- 종료 여부 판정
- 승패 계산

## 공개 API

### `board.py`

```python
class Board:
    @classmethod
    def create_initial(cls) -> "Board": ...

    def get_cell(self, position: Position) -> CellState: ...
    def set_cell(self, position: Position, value: CellState) -> None: ...
    def is_in_bounds(self, position: Position) -> bool: ...
    def count_cells(self) -> dict[CellState, int]: ...
    def clone(self) -> "Board": ...
    def to_matrix(self) -> list[list[CellState]]: ...
```

규약:
- `set_cell()`은 내부용 API로 사용할 수 있다.
- 공개 엔진 사용자는 직접 `set_cell()`로 게임 규칙을 우회하지 않도록 `game_engine` 경로를 우선 사용한다.

### `move_validator.py`

```python
def get_flippable_positions(
    board: Board,
    player: Player,
    position: Position,
) -> list[Position]: ...

def get_flippable_directions(
    board: Board,
    player: Player,
    position: Position,
) -> list[tuple[int, int]]: ...

def is_valid_move(
    board: Board,
    player: Player,
    position: Position,
) -> bool: ...

def get_valid_moves(
    board: Board,
    player: Player,
) -> list[Position]: ...
```

규약:
- 모든 함수는 입력 `board`를 변경하지 않는다.
- `get_valid_moves()` 결과 순서는 `(row, col)` 오름차순으로 고정한다.

### `game_engine.py`

```python
def create_new_game() -> GameState: ...

def apply_move(
    state: GameState,
    position: Position,
) -> MoveResult: ...

def pass_turn(
    state: GameState,
) -> MoveResult: ...

def get_valid_moves_for_current_player(
    state: GameState,
) -> list[Position]: ...

def evaluate_game_status(
    board: Board,
    current_player: Player,
) -> GameStatus: ...
```

규약:
- `apply_move()`와 `pass_turn()`은 성공 시 새 상태를 반영한 `MoveResult`를 반환한다.
- 구현 방식은 내부 가변/불변 무엇이든 가능하지만, 외부 관점에서 실패 시 입력 `state`는 변경되지 않아야 한다.
- 종료된 게임에서는 `apply_move()`와 `pass_turn()` 모두 실패해야 한다.

## 실패 규약

### `apply_move()`
실패 조건:
- 좌표가 범위 밖
- 대상 칸이 비어 있지 않음
- 어떤 방향에서도 뒤집을 수 없음
- 이미 종료된 게임

실패 시 보장:
- `state.board` 유지
- `state.current_player` 유지
- `state.status` 유지
- `move_history`, `last_move` 같은 부가 상태 유지

### `pass_turn()`
실패 조건:
- 현재 플레이어가 둘 수 있는 유효 수가 있음
- 이미 종료된 게임

성공 시 보장:
- 보드는 유지
- 현재 플레이어만 상대 플레이어로 전환
- 직후 종료 여부를 다시 계산

## 직렬화 규약

### `Board.to_matrix()`
- 8x8 2차원 리스트 반환
- 각 원소는 `CellState` 또는 직렬화 가능한 대응 문자열로 변환 가능해야 함

### `GameState` 직렬화 최소 필드
- 보드 64칸 상태
- 현재 플레이어
- 종료 여부
- 종료 시 승패 결과 또는 무승부 정보

## 테스트 연결 예시

```python
from engine.game_engine import create_new_game, apply_move, get_valid_moves_for_current_player

state = create_new_game()
assert get_valid_moves_for_current_player(state) == [(2, 3), (3, 2), (4, 5), (5, 4)]

result = apply_move(state, (2, 3))
assert result.success is True
assert (3, 3) in result.flipped_positions
```

위 예시는 `src` 디렉터리를 source root로 설정한 환경을 전제로 한다.

## 비결정 사항
- 실패를 예외로 노출할지 `MoveResult.error_code` 중심으로 노출할지는 구현 전 최종 선택 가능
- 내부적으로 dataclass 불변 객체를 사용할지, clone 기반 가변 객체를 사용할지는 구현자가 선택 가능
  - 단, 외부 계약은 동일해야 한다
