# Self Play 구현 작업 지시서

## 목적
오셀로 엔진을 사용해 학습용 대국 데이터를 생성하는 셀프 플레이 실행기를 구현한다.

## 선행 입력
- `docs/training/self-play-spec.md`
- `docs/training/predict-api.md`
- `docs/engine/othello-rules.md`
- `docs/training/rl-components.md`
- `specs/training/self-play-data-schema.md`
- `specs/training/rl-components-spec.md`
- `agents/training-data-agent.md`

## 필수 작업
- 정책 또는 예측 API를 호출해 수 선택
- 패스와 종료를 포함한 전체 대국 진행
- 표준 초기 상태 또는 합법적인 도달 가능 초기 상태만 허용하도록 검증
- 대국 기록 저장
- 시드 기반 재현성 보장
- 실패한 대국 로그 기록
- 완료 대국과 실패 대국 구분 저장 또는 식별 정보 제공
- 보상 기준 관점 고정

## 완료 조건
- 정상 종료 대국 기록을 안정적으로 저장한다.
- 유효하지 않은 수를 최종 선택하지 않는다.
- 재현성 검증이 가능하다.
- 대국 기록에 최소한 수순, 상태별 정책 입력 정보, 최종 보상, 시드, 시작 시각, 종료 시각, 정책 버전이 포함된다.
- 시작 상태가 표준 초기 상태가 아니면 합법적인 도달 가능 상태임을 검증하거나, 검증할 수 없을 때는 표준 초기 상태만 사용한다.
- 보상 기준은 문서나 설정에서 고정되고, 완료 대국과 실패 대국을 구분할 수 있다.
