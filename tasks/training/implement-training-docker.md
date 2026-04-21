# Training Docker 구현 작업 지시서

## 목적
학습, 평가, 테스트 실행을 위한 `training` 전용 Docker 환경을 runtime과 분리해 구성한다.

## 선행 입력
- `docs/training/training-docker.md`
- `docs/training/cnn-policy.md`
- `specs/training/training-docker-spec.md`
- `specs/training/cnn-model-spec.md`
- `agents/training-loop-agent.md`

## 필수 작업
- `Dockerfile.training` 추가
- `requirements-training.txt` 추가
- `torch`, `numpy`, `pytest` 포함
- training 테스트 실행 경로 구성
- `PYTHONPATH=/app/src` 기준 import 경로 보장
- runtime Docker와 분리 유지
- 최소 build/run 검증 수행

## 완료 조건
- `Dockerfile.training`으로 training 전용 이미지를 빌드할 수 있다.
- 컨테이너 안에서 `engine`, `training` import가 동작한다.
- 컨테이너 안에서 `torch` import 시 기본 dependency 경고가 없다.
- 컨테이너 안에서 training 단위 테스트를 실행할 수 있다.
- `requirements.txt`는 runtime 전용으로 유지되고, `requirements-training.txt`는 training 전용 의존성을 가진다.
- CNN 모델 구현이 추가될 때 같은 이미지에서 테스트를 계속 수행할 수 있다.
