# Training Docker 기준

## 목적
이 문서는 학습과 평가를 위한 `training` 전용 Docker 실행 환경 기준을 정의한다.

`runtime`용 Docker는 FastAPI와 웹 UI 실행을 담당하고, `training`용 Docker는 `torch` 기반 모델 개발, self-play, 평가, 테스트 실행을 담당한다.

## 분리 원칙
- `runtime` 이미지와 `training` 이미지는 분리한다.
- `runtime` 이미지는 API 실행에 필요한 최소 의존성만 포함한다.
- `training` 이미지는 모델 학습과 평가에 필요한 의존성을 포함한다.
- `training` 이미지 변경이 `runtime` 이미지 무게와 배포 경로에 직접 영향을 주면 안 된다.

## 범위
- `Dockerfile.training`
- `requirements-training.txt`
- training 테스트 실행
- self-play, trainer, evaluator 실행

## 포함 의존성 기준
- Python 3.11 이상
- `torch`
- `numpy`
- `pytest`
- `src/training` 개발과 테스트에 필요한 의존성

## 실행 기준
- 컨테이너 내부 source root는 `/app` 기준으로 잡는다.
- `PYTHONPATH=/app/src`를 기본으로 둔다.
- training 관련 테스트는 컨테이너 안에서 재현 가능해야 한다.
- self-play와 evaluator 실행에 필요한 명령을 컨테이너에서 바로 실행할 수 있어야 한다.
- 최소 검증은 다음을 포함해야 한다.
  - `docker build -f Dockerfile.training ...`
  - 컨테이너 안에서 `import torch`, `import engine`, `import training`
  - 컨테이너 안에서 `pytest tests/unit/training -q`

## runtime과의 관계
- `Dockerfile`은 계속 `runtime` 전용으로 유지한다.
- `Dockerfile.training`은 학습/평가/테스트 전용으로 유지한다.
- 두 이미지가 서로 다른 `requirements` 파일을 사용할 수 있다.

## 권장 사용 예
- training 단위 테스트 실행
- CNN 모델 shape 검증
- self-play 배치 실행
- evaluator 리포트 생성

## 비범위
- API 서버 배포
- GPU 스케줄링 전략
- 분산 학습 오케스트레이션
