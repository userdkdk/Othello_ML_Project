# Runtime Run Guide

## 목적
이 문서는 runtime 웹 앱을 Docker 기준으로 실행하는 방법을 정리한다.

## 기본 실행
- 웹 런타임 실행:
  - `./scripts/run-runtime.sh`
- `make` 실행:
  - `make runtime`

기본 주소:
- `http://localhost:8000/`
- `http://localhost:8000/training`

## 동작 방식
- `scripts/run-runtime.sh`는 runtime Docker 이미지를 빌드한다.
- 컨테이너 안에서 `uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000`을 실행한다.
- FastAPI는 `/api/*`를 제공하고, 빌드된 `frontend/dist`를 `/`와 `/training`에서 서빙한다.

## 환경 변수
- 포트 변경:
  - `HOST_PORT=8010 ./scripts/run-runtime.sh`
- 이미지 이름 변경:
  - `IMAGE_NAME=my-othello-runtime ./scripts/run-runtime.sh`
- 컨테이너 이름 변경:
  - `CONTAINER_NAME=my-othello-runtime ./scripts/run-runtime.sh`

## 주의
- runtime 실행은 로컬 Python이 아니라 Docker 기준으로 사용한다.
- runtime 이미지에는 CPU 추론용 `torch`가 포함된다.
- 기본 inference checkpoint는 `checkpoints/best-balanced-inference.pt`를 우선 탐색한다.

## AI 대전용 checkpoint 위치
- 기본 AI 대전 모델:
  - `checkpoints/best-balanced-inference.pt`
- 흑 전용 모델 실험:
  - `checkpoints/best-black-inference.pt`
- 백 전용 모델 실험:
  - `checkpoints/best-white-inference.pt`

의미:
- runtime은 기본적으로 `training checkpoint`가 아니라 `inference checkpoint`를 사용한다.
- 즉 누적 학습 resume용 `latest-training.pt`를 기본 대전 모델로 직접 쓰는 구조가 아니다.

## 파일 배치 기준
- 호스트 기준 checkpoint는 프로젝트 루트의 `checkpoints/` 아래에 둔다.
- runtime Docker 이미지는 이 경로의 checkpoint를 기준으로 모델을 찾는다.
- 기본 대전은 `best-balanced-inference.pt`가 있으면 그 파일을 사용한다.
- 파일이 없거나 로드 실패 시에는 heuristic fallback과 warning으로 내려갈 수 있다.

예시:
- 기본 AI 대전만 쓰고 싶을 때:
  - `checkpoints/best-balanced-inference.pt` 배치
- 흑/백 다른 모델 비교를 준비할 때:
  - `checkpoints/best-black-inference.pt`
  - `checkpoints/best-white-inference.pt`

## 관련 경로
- 실행 스크립트: `scripts/run-runtime.sh`
- Docker 이미지 정의: `Dockerfile`
- FastAPI app 조립: `src/api/fastapi_app.py`
- runtime API 로직: `src/api/runtime.py`
- frontend 앱: `frontend/`
