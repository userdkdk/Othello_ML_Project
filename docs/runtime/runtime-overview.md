# 런타임 개요

## 목적
이 문서는 엔진과 학습 계층을 실제로 실행하는 런타임 구조를 정의한다.

## 범위
- Docker
- FastAPI
- 웹 UI
- 실행 엔트리포인트

## 원칙
- `runtime`은 `engine`과 `training`의 어댑터 계층이다.
- 규칙 계산은 `src/engine` 또는 `src/training`에 위임한다.
- Docker 실행은 로컬 Python 설치 유무와 무관하게 동작해야 한다.
- 웹 UI는 상태 표시와 조작 인터페이스를 제공하되, 게임 규칙은 직접 계산하지 않는다.
