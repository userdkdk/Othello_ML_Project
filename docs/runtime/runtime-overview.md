# 런타임 개요

## 목적
이 문서는 엔진과 학습 계층을 실제로 실행하는 런타임 구조를 정의한다.

## 범위
- Docker
- FastAPI
- 분리된 웹 프론트엔드
- 실행 엔트리포인트
- runtime용 모델 로드 경로

## 원칙
- `runtime`은 `engine`과 `training`의 어댑터 계층이다.
- 규칙 계산은 `src/engine` 또는 `src/training`에 위임한다.
- Docker 실행은 로컬 Python 설치 유무와 무관하게 동작해야 한다.
- 프론트엔드와 백엔드는 분리하되 API 계약은 단순하게 유지한다.
- 웹 UI는 상태 표시와 조작 인터페이스를 제공하되, 게임 규칙은 직접 계산하지 않는다.
- runtime은 기본적으로 추론 가능한 모델만 소비하고, 학습 재개 상태는 직접 다루지 않는 것을 기본값으로 한다.

## checkpoint 소비 기준
- runtime이 기본적으로 읽는 모델 아티팩트는 `training checkpoint`가 아니라 `inference checkpoint`다.
- 권장 기본 경로는 다음과 같다.
  - 기본 게임 정책: `checkpoints/best-balanced-inference.pt`
  - 필요 시 흑 전용 비교/실험 정책: `checkpoints/best-black-inference.pt`
  - 필요 시 백 전용 비교/실험 정책: `checkpoints/best-white-inference.pt`
- runtime은 기본적으로 `latest training checkpoint`를 직접 읽지 않는다.
- `latest training checkpoint`는 trainer의 `resume`용 경로로 남겨두고, runtime은 추론 전용 checkpoint를 읽는 구조를 기본값으로 한다.
- runtime 호출자가 경로를 명시적으로 넘기면 그 값을 우선할 수 있어야 한다.

## 실행 엔트리포인트 기준
- runtime 엔트리포인트는 최소한 다음 책임을 가진다.
  - inference checkpoint 경로 해석
  - FastAPI app 초기화
  - 웹 UI 또는 API에서 사용할 agent/model 생성
- checkpoint 경로 해석 우선순위는 다음을 권장한다.
  - 호출자 명시 경로
  - runtime 기본 inference checkpoint 경로

## 프론트엔드 경계
- runtime의 기본 UI는 백엔드 템플릿이 아니라 분리된 프론트엔드 앱으로 두는 것을 기본값으로 한다.
- 권장 기본 조합은 다음과 같다.
  - 백엔드: `FastAPI`
  - 프론트엔드: `Vite + React`
- 개발 시 프론트엔드는 독립 dev server에서 실행하고, 백엔드는 `/api/*`를 제공한다.
- 배포 시 FastAPI가 빌드된 정적 프론트엔드 산출물을 함께 서빙할 수 있다.
- 현재 runtime의 게임 UI는 게임 상태 표시와 수 입력을 위한 얇은 인터페이스로 본다.
- 학습 제어, self-play 반복, best checkpoint 비교, 누적 학습 상태 모니터링 같은 기능은 기본 게임 UI와 분리하는 것을 권장한다.
- 즉 프론트엔드는 최소 두 부류로 나눠 해석하는 것이 안전하다.
  - 게임 플레이 UI
  - 학습/운영 UI
- 구현 spec이 아직 없는 상태라면, 우선순위는 게임 플레이 UI를 runtime 최소 범위로 두고 학습/운영 UI는 별도 문서와 spec으로 분리하는 쪽이 맞다.
- 같은 이유로 training dashboard 성격의 프론트엔드는 `runtime` 내부 구현이라도 별도 task와 spec으로 관리하는 것을 권장한다.
- 반면 다음 기능은 기본 게임 플레이 UI 범위 안에서 확장하는 것이 자연스럽다.
  - 사람 vs 사람
  - 사람 vs 모델
  - 모델 vs 모델 관전
- 위 기능들은 모두 동일한 보드 상태와 수 진행을 보여주므로, 별도 프론트 앱으로 나누기보다 하나의 게임 UI 안에서 모드 선택으로 푸는 것을 권장한다.

## 런타임 의존성 기준
- runtime이 inference checkpoint를 실제 로드해 모델 턴을 수행하려면 `torch`가 runtime 의존성에 포함되어야 한다.
- runtime 기본값은 GPU 학습 환경이 아니라 CPU 추론 환경이므로, Docker와 전용 venv에서는 CPU wheel 기준 설치를 우선한다.
- `torch`가 없는 환경에서는 다음 둘 중 하나로 처리해야 한다.
  - 명시적 오류를 API 응답으로 반환
  - 기본 checkpoint 로드 실패 시 heuristic fallback과 경고 노출
- 적어도 explicit checkpoint 경로를 받은 경우에는 `500`이 아니라 제어된 오류 응답을 반환해야 한다.

## 게임 UI 모드 기준
- 기본 게임 UI는 최소한 다음 모드를 표현할 수 있어야 한다.
  - `human_vs_human`
  - `human_vs_model`
  - `model_vs_model`
- `human_vs_model`에서는 사람이 어느 색을 맡는지 선택 가능해야 한다.
  - `human_black`
  - `human_white`
- `model_vs_model`에서는 흑/백 각각 어떤 inference checkpoint를 사용할지 구분 가능해야 한다.
- 기본 runtime 경로에서는 별도 지정이 없으면 양쪽 모두 `best-balanced-inference.pt`를 사용하되, 필요 시 흑/백에 다른 모델을 붙일 수 있어야 한다.
- `model_vs_model`은 관전 모드로 해석하고, UI는 사람이 수를 입력하지 않아도 진행 상태와 다음 수를 확인할 수 있어야 한다.
