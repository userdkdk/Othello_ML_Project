# Training 구현 우선순위 기준

## 목적
이 문서는 `training` 영역의 구현 작업을 어떤 순서로 진행해야 하는지 우선순위 기준을 정의한다.

현재 저장소의 `training`은 self-play, episode 수집, 모델 추론, 저장, 체크포인트, 향후 학습 루프까지 여러 작업이 분리되어 있다. 이 문서는 선후관계와 리스크를 기준으로 구현 순서를 고정한다.

## 우선순위 판단 기준
- 먼저 구현할수록 다른 작업의 입력 계약을 안정화하는가
- 나중 작업이 앞선 작업의 출력 구조에 의존하는가
- 테스트와 검증 경로를 빨리 확보할 수 있는가
- 문서상 비범위와 현재 구현 범위를 혼동시키지 않는가

## 권장 구현 순서
1. `training-pipeline`
2. `episode-storage`
3. `cnn-policy-model`
4. `checkpoint-policy`
5. `training-docker`
6. `trainer-loop`

## 순서별 이유

### 1. `training-pipeline`
- 현재 self-play, episode, report, evaluator의 직접 계약을 먼저 안정화해야 한다.
- 이후 저장기, CNN 모델, checkpoint, trainer-loop가 모두 이 경로를 입력으로 사용한다.
- 실패 episode 집계, 메모리상 필드, 직렬화 경계를 먼저 고정하는 것이 중요하다.

### 2. `episode-storage`
- 파이프라인 산출물을 파일에 남기는 경로가 정리되어야 이후 학습 루프와 운영 흐름이 안정된다.
- 저장 스키마와 `Episode.to_dict()` 관계를 먼저 구현해 두면 이후 학습 입력 재사용 경로를 명확히 할 수 있다.

### 3. `cnn-policy-model`
- 추론 계층과 모델 버전 메타데이터를 먼저 연결해야 checkpoint와 향후 trainer-loop 의미가 선명해진다.
- action mask, `PASS` 규약, `policy_output` 기록은 self-play 흐름과 직접 연결되므로 early integration 대상이다.

### 4. `checkpoint-policy`
- 모델 로드/저장 규칙은 CNN 모델 구현이 어느 정도 정리된 뒤 고정하는 편이 자연스럽다.
- 정책 버전과 self-play 메타데이터 연결도 이 시점에 정리하기 쉽다.

### 5. `training-docker`
- training 전용 실행 환경은 앞선 구현들을 한 번에 검증하는 데 유용하다.
- 너무 먼저 만들면 아직 흔들리는 계약을 따라가느라 이미지 정의가 자주 바뀔 수 있다.
- 반대로 너무 늦으면 통합 검증이 늦어진다. 따라서 모델과 checkpoint 방향이 보인 뒤에 두는 것이 적절하다.

### 6. `trainer-loop`
- 실제 모델 업데이트 학습 루프는 가장 뒤에 두는 것이 안전하다.
- 이 작업은 self-play 산출물, 저장 경로, 모델 출력, checkpoint 정책을 모두 입력으로 사용한다.
- 현재 `Trainer.train()` 요약 계층과의 분리도 앞선 작업들이 안정된 뒤 구현하는 편이 충돌이 적다.

## 병렬 진행 가능 범위
- `training-pipeline`과 직접 충돌하지 않는 문서 정비
- `cnn-policy-model` 구현 중 `training-docker` 초안 준비
- `checkpoint-policy` 문서/테스트 정리와 `episode-storage` 구현 준비

## 선행 완료 체크
- `trainer-loop` 시작 전:
  - `run_self_play()` 산출물 구조가 안정적이어야 한다.
  - `Episode.to_dict()`와 저장 경계가 문서/테스트로 드러나야 한다.
  - CNN 정책 모델의 입력/출력 shape와 버전 메타데이터가 정리돼 있어야 한다.
  - checkpoint 버전 해석 규칙이 고정돼 있어야 한다.

## 비권장 순서
- `trainer-loop`를 `training-pipeline`보다 먼저 구현
- checkpoint writer를 CNN 모델 경로보다 먼저 고정
- Docker 환경을 문서/계약보다 앞서 과도하게 고정

## 현재 권장 착수점
- 가장 먼저 손댈 구현은 `tasks/training/implement-training-pipeline.md`다.
- 그 다음은 `tasks/training/implement-episode-storage.md`다.
- 실제 모델 업데이트는 마지막 단계로 미룬다.
