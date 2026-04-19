# 웹 런타임 명세

## 목적
이 문서는 Docker와 FastAPI 기반 실행 환경의 최소 계약을 정의한다.

## 구현 대상
- `src/api/fastapi_app.py`
- `Dockerfile`
- `requirements.txt`

## 최소 엔드포인트
- `GET /`
- `GET /api/state`
- `POST /api/new`
- `POST /api/move`
- `POST /api/pass`

## 최소 UI 요구사항
- 보드 표시
- 현재 플레이어 표시
- 유효 수 시각화
- 새 게임 버튼
- 패스 버튼
- 점수 또는 상태 정보 표시

## Docker 요구사항
- 컨테이너 내부에서 `PYTHONPATH=/app/src`
- `uvicorn api.fastapi_app:app` 실행
- 기본 포트 `8000`
