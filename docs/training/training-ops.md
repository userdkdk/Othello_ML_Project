# 학습 운영 기준

## 목적
이 문서는 `training` 계층에서 학습 제어, 대시보드 노출용 상태, checkpoint 비교 기능을 어떤 경계로 다뤄야 하는지에 대한 상위 기준을 정의한다.

현재 저장소에는 self-play, evaluator, checkpoint 저장/로드, 일부 trainer-loop 구현이 존재한다. 이 문서는 그 위에 "운영 가능한 학습 흐름"을 얹을 때 필요한 기준을 고정한다.

## 적용 범위
- 학습 세션 시작, 중지, 재개 요청
- iteration 단위 self-play + training + evaluation 실행
- 대시보드에 표시할 학습 상태와 요약 지표
- checkpoint 간 비교 실행과 결과 해석
- runtime이 training 계층을 호출할 때의 책임 분리

## 경계 기준
- 실제 모델 업데이트와 checkpoint 저장 책임은 `training` 계층에 둔다.
- 웹 화면, API, 버튼, 폴링 같은 상호작용 책임은 `runtime` 계층에 둔다.
- 대시보드는 학습 상태를 보여주는 어댑터여야 하며, 학습 규칙 자체를 재구현하면 안 된다.
- checkpoint 비교의 승패 계산, 양방향 평가, balanced score 계산은 `training` 계층 규칙을 따른다.

## 학습 제어 기준
- 학습 제어의 기본 단위는 `session`과 `iteration`이다.
- `session`은 동일한 모델 계열과 checkpoint 경로 집합을 공유하는 학습 실행 묶음이다.
- `iteration`은 다음 단계를 한 번 수행하는 단위다.
  1. self-play 데이터 생성
  2. 모델 업데이트 수행
  3. latest checkpoint 저장
  4. 기준 상대 평가
  5. 필요 시 best checkpoint 승격
- 최소 제어 동작은 다음을 지원하는 것을 권장한다.
  - `start`
  - `run_once`
  - `pause`
  - `resume_session`
  - `start_from_checkpoint`
  - `stop`
- `pause`는 현재 진행 중인 iteration을 중간 파손 없이 끝낸 뒤 다음 iteration 진입을 멈추는 의미를 기본값으로 둔다.
- `stop`은 세션을 종료 상태로 바꾸고 이후 같은 세션 객체를 다시 재사용하지 않는 방향을 기본값으로 둔다.
- `resume_session`은 이미 존재하는 paused 세션을 다시 진행하는 경로다.
- `start_from_checkpoint`는 training checkpoint를 입력으로 새 세션을 시작하는 경로다.
- 위 둘은 같은 동작으로 취급하면 안 된다.

## 세션 상태 기준
- 학습 세션은 최소한 다음 상태를 표현 가능해야 한다.
  - `idle`
  - `running`
  - `pause_requested`
  - `paused`
  - `completed`
  - `failed`
  - `stopped`
- `running` 중에는 현재 iteration 번호와 현재 단계가 추적 가능해야 한다.
- 실패 시 마지막 오류 메시지와 실패 단계가 함께 남아야 한다.
- 세션 상태는 대시보드와 API 응답에서 같은 용어를 사용해야 한다.

## 대시보드 기준
- 게임 플레이 UI와 학습 운영 UI는 분리된 화면 또는 분리된 패널로 해석해야 한다.
- 대시보드는 최소한 다음 범주의 정보를 보여줄 수 있어야 한다.
  - 현재 세션 상태
  - 최근 iteration 결과
  - 누적 학습 진행도
  - self-play 통계
  - 평가 통계
  - checkpoint 상태
- 대시보드는 "현재 값"뿐 아니라 "직전 iteration 결과"를 함께 보여줄 수 있어야 한다.
- 대시보드에서 직접 노출하는 수치는 training 리포트와 checkpoint 메타데이터에서 추적 가능해야 한다.

## 최소 대시보드 지표
- 세션 식별자
- 현재 상태
- 현재 iteration 번호
- 누적 epoch 수
- 누적 step 수
- 최근 self-play 게임 수
- 최근 self-play 실패 수
- 최근 policy loss
- 최근 value loss
- 최근 heuristic 평가 결과
- 최근 current-best 비교 결과
- 최근 승격된 track 목록
- latest training checkpoint 경로
- best inference checkpoint 경로 집합

## checkpoint 비교 기준
- 비교 기능은 단순 파일 diff가 아니라 "두 checkpoint가 만든 agent의 대국 결과 비교"로 해석한다.
- 비교 기본값은 양방향 평가다.
  - checkpoint A가 흑, checkpoint B가 백
  - checkpoint B가 흑, checkpoint A가 백
- 비교 리포트는 최소한 다음을 포함할 수 있어야 한다.
  - 총 게임 수
  - A 기준 black-side win rate
  - A 기준 white-side win rate
  - A 기준 balanced score
  - draw rate
  - failures
- 비교 결과는 승자만 보여주기보다, 어느 색에서 강했는지 드러내야 한다.
- 같은 모델 버전이라도 서로 다른 checkpoint 파일은 별도 비교 대상으로 취급한다.
- checkpoint 비교는 현재 best track 판정 규칙과 충돌하지 않도록 독립 기능으로 유지한다.

## checkpoint 선택 기준
- runtime 대시보드가 기본적으로 보여주는 checkpoint 집합은 다음 경로 규칙을 따른다.
  - `checkpoints/latest-training.pt`
  - `checkpoints/best-black-training.pt`
  - `checkpoints/best-white-training.pt`
  - `checkpoints/best-balanced-training.pt`
  - `checkpoints/best-black-inference.pt`
  - `checkpoints/best-white-inference.pt`
  - `checkpoints/best-balanced-inference.pt`
- 위 training checkpoint들은 운영 상태 표시와 학습 재개 입력 후보를 위한 슬롯으로 해석한다.
- runtime이 실제 비교 실행이나 추론 agent 생성을 할 때의 기본 입력은 inference checkpoint로 두는 것을 권장한다.
- 호출자가 경로를 명시하면 그 값을 우선한다.
- 존재하지 않는 checkpoint는 오류로 처리할지, "비교 불가" 상태로 표시할지 runtime 구현에서 선택할 수 있어야 한다.

## runtime 연동 기준
- runtime은 장기 실행 중인 학습 세션의 상태를 조회할 수 있어야 한다.
- runtime은 training 계층에 직접 self-play, trainer, evaluator 호출을 위임하되, 계산 로직은 복제하지 않는다.
- runtime은 대시보드용 요약 스냅샷을 캐시할 수 있지만, 최종 해석 기준은 training 리포트다.
- 학습 제어 요청과 checkpoint 비교 요청은 게임 플레이 엔드포인트와 분리된 별도 namespace로 노출하는 것을 권장한다.

## 비범위
- 분산 작업 스케줄러
- 원격 워커 큐
- 장기 실험 비교 저장소
- 권한 관리와 멀티유저 세션 분리
