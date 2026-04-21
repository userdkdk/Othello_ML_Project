# Training Docker 명세

## 목적
이 문서는 `training` 전용 Docker 실행 환경의 최소 파일 구조와 계약을 정의한다.

## 구현 대상
- `Dockerfile.training`
- `requirements-training.txt`

## 파일 계약

### `Dockerfile.training`
- Python 3.11 계열 베이스 이미지를 사용해야 한다.
- 작업 디렉터리는 `/app`이어야 한다.
- 최소 환경 변수:
  - `PYTHONDONTWRITEBYTECODE=1`
  - `PYTHONUNBUFFERED=1`
  - `PYTHONPATH=/app/src`
- `requirements-training.txt`를 복사해 설치해야 한다.
- `src/`와 `tests/`를 컨테이너에 포함해야 한다.
- 기본 명령은 training 환경 검증 또는 테스트 실행에 적합해야 한다.

### `requirements-training.txt`
- `torch`를 포함해야 한다.
- `numpy`를 포함해야 한다.
- `pytest`를 포함해야 한다.
- training 계층 테스트와 구현에 필요한 패키지를 포함해야 한다.
- `runtime` 전용 `requirements.txt`와 분리되어야 한다.

## 동작 계약
- 컨테이너 안에서 `PYTHONPATH=src` 추가 설정 없이 `engine`, `training` import가 가능해야 한다.
- 컨테이너 안에서 `torch` import 시 기본 scientific dependency 누락 경고가 없어야 한다.
- 컨테이너 안에서 training 단위 테스트를 실행할 수 있어야 한다.
- CNN 모델 구현이 들어오면 같은 이미지에서 모델 import와 기본 추론 테스트가 가능해야 한다.

## 비범위
- GPU 전용 베이스 이미지 강제
- CUDA 버전 고정
- 모델 체크포인트 볼륨 전략
