# 웹 런타임 명세

## 목적
이 문서는 Docker와 FastAPI 기반 실행 환경의 최소 계약을 정의한다.

## 구현 대상
- `src/api/fastapi_app.py`
- `frontend/`
- `Dockerfile`
- `requirements.txt`

## 최소 엔드포인트
- `GET /`
- `GET /training`
- `GET /api/state`
- `POST /api/new`
- `POST /api/move`
- `POST /api/pass`
- `POST /api/step`
- `GET /api/training/state`
- `GET /api/training/comparisons/latest`

## 게임 모드 계약
- runtime은 최소한 다음 게임 모드를 지원할 수 있어야 한다.
  - `human_vs_human`
  - `human_vs_model`
  - `model_vs_model`
- `POST /api/new`는 필요 시 다음 시작 옵션을 입력으로 받을 수 있어야 한다.
  - `mode`
  - `human_side`
  - `black_checkpoint_path`
  - `white_checkpoint_path`
- `human_vs_model`에서 `human_side`는 `BLACK` 또는 `WHITE`로 해석 가능해야 한다.
- `model_vs_model`에서는 흑 agent와 백 agent를 서로 다른 inference checkpoint에서 만들 수 있어야 한다.
- 별도 경로가 주어지지 않으면 기본 모델 경로는 runtime 기본 inference checkpoint 규칙을 따른다.

## 최소 UI 요구사항
- 프론트와 백이 분리된 구조
- 보드 표시
- 현재 플레이어 표시
- 유효 수 시각화
- 새 게임 버튼
- 패스 버튼
- 점수 또는 상태 정보 표시
- 게임 모드 선택
- `human_vs_model`일 때 사람 색 선택
- `model_vs_model`일 때 관전 진행 버튼 또는 자동 진행 제어
- 현재 흑/백 agent 정보 또는 모델 버전 표시
- runtime warning 또는 dependency warning 표시

## 프론트/백 분리 계약
- 프론트엔드는 `frontend/` 아래 독립 앱으로 존재해야 한다.
- 개발 모드에서는 프론트엔드 dev server와 FastAPI API 서버를 분리할 수 있어야 한다.
- 배포 모드에서는 FastAPI가 빌드된 프론트엔드 정적 산출물을 서빙할 수 있어야 한다.
- `/`는 게임 UI, `/training`은 학습 운영 UI 진입점으로 사용 가능해야 한다.

## API 동작 기준
- `human_vs_model`에서 모델 턴이 오면 runtime은 training 계층의 agent를 호출해 다음 수를 계산할 수 있어야 한다.
- `model_vs_model`에서는 두 턴 모두 runtime이 agent를 호출해 진행할 수 있어야 한다.
- `model_vs_model` 진행은 한 수씩 수동 진행하거나 자동 진행으로 확장 가능해야 한다.
- 사람 턴이 아닌데 `POST /api/move`가 호출되면 runtime은 명시적으로 실패를 반환해야 한다.
- `POST /api/step`은 현재 모드와 현재 턴에 따라 모델이 둘 수 있는 한 수를 진행시키는 기본 경로여야 한다.
- `human_vs_model`에서는 현재 턴이 모델일 때만 `POST /api/step`이 성공해야 한다.
- `model_vs_model`에서는 `POST /api/step`으로 한 수씩 관전 진행할 수 있어야 한다.
- agent가 유효하지 않은 수를 반환해 엔진이 실패하면 그 실패는 UI와 API 응답에 드러나야 한다.
- explicit checkpoint 경로 로드가 dependency 부족 또는 payload 오류로 실패하면 `500`이 아니라 제어된 오류 응답을 반환해야 한다.

## Docker 요구사항
- 컨테이너 내부에서 `PYTHONPATH=/app/src`
- `uvicorn api.fastapi_app:app` 실행
- 기본 포트 `8000`
- runtime image는 inference checkpoint 로드가 가능한 의존성을 포함해야 한다.
