# 학습 대시보드 기준

## 목적
이 문서는 `runtime` 영역에서 학습 제어, 진행 상황 모니터링, checkpoint 비교를 제공하는 운영 UI의 상위 기준을 정의한다.

기본 게임 보드 UI와 학습 운영 UI를 분리해, 게임 플레이 기능과 장기 학습 관리 기능이 서로의 복잡도를 오염시키지 않도록 하는 것이 목적이다.

## 적용 범위
- 학습 대시보드 화면
- 학습 제어 API와 UI 연결
- iteration 상태 폴링 또는 갱신
- checkpoint 비교 실행 화면

## UI 분리 기준
- 기본 `/` 게임 플레이 UI는 유지 가능한 최소 범위로 남긴다.
- 학습 운영 UI는 별도 경로 또는 별도 탭으로 분리하는 것을 기본값으로 둔다.
- 권장 기본 예시는 다음 둘 중 하나다.
  - `/training`
  - `/ops/training`
- 게임 플레이 UI와 학습 운영 UI는 같은 FastAPI 앱 안에 있어도 되지만, 상태 모델과 API namespace는 분리하는 것을 권장한다.

## 학습 대시보드 최소 화면 구성
- 세션 제어 패널
- 최근 iteration 요약 패널
- 누적 학습 진행 패널
- checkpoint 상태 패널
- checkpoint 비교 실행 패널
- 최근 이벤트 또는 오류 패널

## 세션 제어 패널 기준
- 새 세션 시작
- 기존 checkpoint 기반 `start_from_checkpoint` 시작
- pause 요청
- `resume_session` 요청
- stop 요청
- 현재 상태 배지 표시

## 최근 iteration 패널 기준
- 현재 또는 마지막 iteration 번호
- self-play 게임 수
- self-play 실패 수
- 학습 sample 수
- policy loss
- value loss
- heuristic 평가 점수
- current-best 비교 결과
- 승격된 track

## checkpoint 패널 기준
- latest training checkpoint
- best-black training/inference checkpoint
- best-white training/inference checkpoint
- best-balanced training/inference checkpoint
- 각 checkpoint의 버전, 저장 시각, track, 주요 평가 메타데이터를 표시할 수 있어야 한다.

## checkpoint 비교 패널 기준
- 비교 대상 두 checkpoint 선택
- 게임 수 설정
- seed 설정
- 비교 실행 버튼
- 결과 요약 표시
- 색별 승률과 balanced score 표시
- 기본 선택지는 inference checkpoint를 우선하고, training checkpoint는 호환 가능한 비교 입력으로만 노출하는 것을 권장한다.

## 상호작용 기준
- 긴 작업은 동기 브라우저 요청 하나에 모두 매달리지 않는 구조를 권장한다.
- UI는 제어 요청 후 세션 상태 조회 API를 통해 진행 상황을 갱신하는 흐름을 기본값으로 둔다.
- 비교 실행은 단발성 작업으로 둘 수 있지만, 결과는 마지막 비교 이력으로 재조회 가능하면 좋다.
- 실패 응답은 버튼 비활성화만으로 숨기지 말고 이유를 사용자에게 노출해야 한다.

## 비범위
- 실시간 websocket 스트리밍 강제
- 복수 사용자 동시 협업
- 실험 태깅/검색 시스템
