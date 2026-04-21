# Training Run Guide

## 목적
이 문서는 training Docker 실행과 누적 학습 재개 방법을 정리한다.

## 기본 실행
- training 테스트 이미지 실행:
  - `./scripts/run-training.sh`
- `make` 실행:
  - `make training`

기본 동작:
- 인자를 주지 않으면 `pytest tests/unit/training -q`를 실행한다.
- 호스트의 `./checkpoints`, `./runs`를 컨테이너 `/app/checkpoints`, `/app/runs`에 마운트한다.

## 누적 학습 실행
- 기본 resume:
  - `./scripts/train-resume.sh`
- 게임 수/에포크 직접 지정:
  - `./scripts/train-resume.sh --num-games 256 --epochs 10`
- `make` 실행:
  - `make train-resume`

기본 동작:
- `checkpoints/latest-training.pt`가 있으면 자동으로 resume한다.
- 없으면 새 학습으로 시작한다.
- 출력은 기본적으로 `/app/runs/latest`에 기록된다.
- checkpoint 파일명 기본값은 `latest-training.pt`다.
- 실행 중에는 `self-play`, `train` 단계별 진행률이 퍼센트로 출력된다.
- 상태 스냅샷은 기본적으로 `runs/latest/training_state.json`에 기록된다.
- 특히 에폭 기준으로 `현재 에폭`, `목표 에폭`, `누적 완료 에폭`을 이어서 추적할 수 있다.

## 파일 배치 기준
- resume용 기본 checkpoint:
  - `checkpoints/latest-training.pt`
- 학습 결과 기본 출력:
  - `runs/latest/`
- training Docker 마운트:
  - 호스트 `./checkpoints` -> 컨테이너 `/app/checkpoints`
  - 호스트 `./runs` -> 컨테이너 `/app/runs`

의미:
- 누적 학습은 `training checkpoint`를 사용한다.
- runtime AI 대전에 쓰는 `best-balanced-inference.pt`는 resume 기본 입력이 아니다.
- 학습을 이어가려면 먼저 `checkpoints/latest-training.pt`가 있어야 한다.

## 자주 쓰는 예시
- 더 오래 학습:
  - `./scripts/train-resume.sh --num-games 256 --epochs 10`
- checkpoint 이름 변경:
  - `./scripts/train-resume.sh --checkpoint-name experiment-a.pt`
- 출력 디렉터리 변경:
  - `./scripts/train-resume.sh --output-dir /app/runs/exp-a`
- resume checkpoint 경로 강제:
  - `./scripts/train-resume.sh --resume-checkpoint /app/checkpoints/experiment-a.pt`
- learning rate 변경:
  - `./scripts/train-resume.sh --learning-rate 5e-4`

## resume와 checkpoint 기준
- 누적 학습은 `training checkpoint`를 사용한다.
- 기본 resume 경로는 `checkpoints/latest-training.pt`다.
- runtime 추론용 `best-balanced-inference.pt`는 resume 기본값으로 쓰지 않는다.

## 어떤 파일을 어디에 둘지
- 새로 누적 학습을 시작하고 결과를 계속 이어가고 싶을 때:
  - `checkpoints/latest-training.pt`를 유지
- runtime에서 기본 AI 대전을 하고 싶을 때:
  - `checkpoints/best-balanced-inference.pt`를 유지
- 학습 결과 리포트와 episode를 보고 싶을 때:
  - `runs/latest/` 확인

권장 운영:
- 학습이 끝나면 `latest-training.pt`는 resume용으로 유지
- 대전에 쓸 모델은 별도로 `best-*-inference.pt`로 관리
- 학습용 checkpoint와 대전용 checkpoint를 같은 파일 의미로 섞지 않는다

## 주요 환경 변수
- `NUM_GAMES`
- `SELF_PLAY_SEED`
- `EPOCHS`
- `LEARNING_RATE`
- `BLACK_AGENT`
- `WHITE_AGENT`
- `CHECKPOINT_NAME`
- `CHECKPOINT_VERSION`
- `OUTPUT_DIR`
- `RESUME_CHECKPOINT`

기본 권장:
- 자주 쓰는 값은 CLI 인자 `--num-games`, `--epochs`로 지정
- 반복 실험 자동화가 필요할 때만 환경 변수를 사용

## 관련 경로
- 테스트/실행 스크립트: `scripts/run-training.sh`
- 누적 학습 스크립트: `scripts/train-resume.sh`
- 학습 진입점: `scripts/train_policy.py`
- trainer 구현: `src/training/trainer.py`
- pipeline 구현: `src/training/training_pipeline.py`
- checkpoint 기준: `docs/training/checkpoint-policy.md`
