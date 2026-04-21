# 프로젝트 구조 명세 작성 작업 지시서

## 목적
Python 프로젝트 시작 전에 패키지 구조, 테스트 구조, API 레이어 분리 방식을 명세한다.

## 선행 입력
- `docs/engine/othello-module-spec.md`
- `docs/training/self-play-spec.md`
- `docs/training/predict-api.md`
- `docs/runtime/runtime-overview.md`
- `agents/governance-agent.md`

## 필수 작업
- `src/` 아래 패키지 구조 정의
- `src/engine`, `src/training`, 향후 API 레이어 분리 원칙 정의
- 테스트 디렉터리 구조 정의
- 의존성 경계와 import 방향 정의
- 실행 엔트리포인트 후보 정의

## 출력 파일
- `specs/runtime/project-structure.md`

## 완료 조건
- 구현 시작 시 폴더를 그대로 만들 수 있을 정도로 구조가 명확하다.
- 엔진 코어와 API 레이어가 분리된 구조가 문서화되어 있다.
- 테스트 위치와 단위/통합 테스트 구분이 명시되어 있다.
