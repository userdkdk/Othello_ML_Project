# 셀프 플레이 데이터 스키마 작성 작업 지시서

## 목적
학습용 대국 기록을 어떤 구조로 저장할지 데이터 스키마를 명세한다.

## 선행 입력
- `docs/training/self-play-spec.md`
- `docs/training/predict-api.md`
- `docs/engine/othello-rules.md`
- `docs/training/rl-components.md`
- `agents/spec-agent.md`

## 필수 작업
- 에피소드 단위 저장 구조 정의
- 턴 단위 상태/행동/보상 구조 정의
- 메타데이터 필드 정의
- 완료 대국과 실패 대국 구분 규약 정의
- 직렬화 포맷 후보와 기본값 정의

## 출력 파일
- `specs/training/self-play-data-schema.md`

## 완료 조건
- 학습 파이프라인이 바로 읽을 수 있는 필드 목록이 정의되어 있다.
- 보상 기준 관점이 고정되어 있다.
- 상태, 행동, 결과, 메타데이터 연결 방식이 명확하다.
- 실패 대국 처리 규칙이 문서화되어 있다.
