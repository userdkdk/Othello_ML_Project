# Othello ML Project

## 배경
코드작성없이 agent에게 명령만해서 구현한 오셀로 학습 모델 생성 프로젝트입니다. agent들의 목적과 구성을 설계하는데 집중했습니다.
명세 작성, 구현, 검증 역할을 수행할 서브 에이전트를 두고 docs, specs, tasks, reviews 폴더에 명세 파일들을 만들어 참고하게 하였습니다. 또한 구현 과정에서 새로운 기능 추가나 기능 변경시 영향 범위를 확인하기 위해 매번 전체 파일을 생성하는 문제를 해결하기 위해 색인, 역색인이 기록된 메타 데이터를 만들고, 에이전트가 직접 실행하여 확인 및 업데이트 할 수 있도록 하였습니다.

오셀로 엔진, 학습 파이프라인, 실행 환경을 한 저장소에서 관리하는 Python 프로젝트다.

## 현재 구조
- `src/engine/`
  - 오셀로 규칙, 보드, 수 검증, 게임 진행
- `src/training/`
  - 랜덤/휴리스틱 agent, match runner, self-play, encoder, trainer, evaluator
- `src/api/`
  - FastAPI 런타임과 웹 UI
- `frontend/`
  - Vite + React 런타임 프론트엔드
- `meta/`
  - 역색인, relation graph, compressed state, 메타 스키마
- `tests/unit/`
  - engine, training 단위 테스트
- `tests/integration/`
  - engine 인수 시나리오 테스트

## 문서 읽는 순서
1. `README.md`
2. `AGENTS.md`
3. `meta/README.md`
4. 현재 작업과 직접 연결된 `meta/state/`, `meta/index/`, `meta/graph/`
5. `docs/README.md`
6. 작업 영역 문서
   - 엔진: `docs/engine/`
   - 학습: `docs/training/`
   - 실행부: `docs/runtime/`
7. 상세 명세: `specs/`
8. 역할 문서: `agents/`
9. 작업 지시서: `tasks/`

주의:
- `meta/`는 탐색과 영향 범위 분석을 위한 운영 계층이다.
- 실제 기준 문서는 여전히 `docs/`, `specs/`, `tasks/`, `AGENTS.md`다.

## 문서 체계
- `docs/`
  - 프로젝트 기준과 상위 규칙
- `specs/`
  - 구현 직전의 코드 레벨 계약
- `tasks/`
  - 구현 또는 정리 작업 지시
- `agents/`
  - 역할별 책임과 품질 기준
- `meta/`
  - 에이전트용 역색인, 관계 그래프, 압축 상태, 메타 스키마
- `reviews/`
  - 검토 결과 기록

## 구조 운영 원칙
- 기능 추가 시 기존 큰 파일에 계속 누적하지 않는다.
- `src/api/`는 app 조립, router, runtime helper, state, schema 단위로 나누는 것을 기본값으로 한다.
- `frontend/src/`는 `pages/`, `components/`, `lib/` 기준 분리를 기본값으로 한다.
- 폴더 구조만 봐도 어떤 기능이 어디에 있고 무엇이 영향을 받는지 추적 가능해야 한다.
- 담당 agent는 구현뿐 아니라 구조 과밀 여부도 함께 관리한다.

## 영역별 빠른 진입
- `engine`
  - 메타 진입: `meta/state/compressed/engine.json`, `meta/index/by_symbol.json`
  - 기준 문서: `docs/engine/othello-rules.md`
  - 상세 명세: `specs/engine/python-engine-spec.md`
  - 작업 지시: `tasks/engine/`
  - 담당 코드: `src/engine/`, `tests/unit/engine/`, `tests/integration/engine/`
- `training`
  - 메타 진입: `meta/state/compressed/training.json`, `meta/index/by_feature.json`
  - 기준 문서: `docs/training/self-play-spec.md`, `docs/training/rl-components.md`
  - 상세 명세: `specs/training/self-play-data-schema.md`, `specs/training/rl-components-spec.md`
  - 작업 지시: `tasks/training/`
  - 담당 코드: `src/training/`, `tests/unit/training/`
- `runtime`
  - 메타 진입: `meta/state/compressed/runtime.json`, `meta/index/by_endpoint.json`
  - 기준 문서: `docs/runtime/runtime-overview.md`
  - 상세 명세: `specs/runtime/project-structure.md`, `specs/runtime/web-runtime-spec.md`
  - 작업 지시: `tasks/runtime/`
  - 담당 코드: `src/api/`, `frontend/`, `Dockerfile`, `requirements.txt`

## 실행 메모
- 엔진 코어는 `src/engine/`에 있고 웹 프레임워크와 분리되어 있다.
- 런타임은 현재 `FastAPI + Docker` 기준으로 정리되어 있다.
- 로컬 Python 버전과 무관한 실행은 Docker 기준으로 맞춘다.

## 빠른 실행
- 런타임 웹 실행: `./scripts/run-runtime.sh`
- 런타임 웹 실행(`make`): `make runtime`
- 학습 테스트 이미지 실행: `./scripts/run-training.sh`
- 학습 테스트 이미지 실행(`make`): `make training`
- 누적 학습 실행: `./scripts/train-resume.sh`
- 누적 학습 실행 예시: `./scripts/train-resume.sh --num-games 256 --epochs 10`
- 누적 학습 실행(`make`): `make train-resume`
- 상세 runtime 사용법: `docs/runtime/run-guide.md`
- 상세 training 사용법: `docs/training/training-run-guide.md`

기본 런타임 주소:
- `http://localhost:8000/`
- `http://localhost:8000/training`

환경 변수:
- `HOST_PORT=8010 ./scripts/run-runtime.sh`
- `IMAGE_NAME=my-othello-runtime ./scripts/run-runtime.sh`

## 체크포인트와 결과물 위치
- `checkpoints/latest-training.pt`
  - 누적 학습 resume용 기본 checkpoint
- `checkpoints/best-balanced-inference.pt`
  - 런타임 AI 대전 기본 checkpoint
- `checkpoints/best-black-inference.pt`
  - 흑 전용 비교/실험용 checkpoint
- `checkpoints/best-white-inference.pt`
  - 백 전용 비교/실험용 checkpoint
- `runs/latest/`
  - 학습 결과물 기본 출력 디렉터리

주의:
- AI 대전 기본값은 `inference checkpoint`를 사용한다.
- 누적 학습 resume 기본값은 `training checkpoint`를 사용한다.
- `scripts/run-training.sh`와 `scripts/train-resume.sh`는 호스트의 `./checkpoints`, `./runs`를 컨테이너 `/app/checkpoints`, `/app/runs`에 마운트한다.
