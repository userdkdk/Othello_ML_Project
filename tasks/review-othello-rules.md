# 오셀로 규칙 문서 리뷰 작업 지시서

## 목적
`docs/othello-rules.md`가 실제 오셀로 규칙과 구현 가능한 명세 기준을 충족하는지 검토한다.

## 선행 입력
- `docs/othello-rules.md`
- `agents/review-agent.md`
- 루트 `AGENTS.md`

## 리뷰 범위
- 실제 오셀로 규칙과의 불일치
- 구현 관점에서 모호한 표현
- 테스트 기준으로 사용하기 어려운 누락

## 출력 파일
- `reviews/docs/othello-rules.md`

## 작성 규칙
- 틀리거나 모호한 부분만 쓴다.
- 각 지적마다 근거를 함께 적는다.
- 가능하면 우선순위를 표기한다.

## 완료 조건
- 리뷰 결과가 `reviews/docs/othello-rules.md`에 정리되어 있다.
- 수정 필요 사항이 기준과 함께 설명되어 있다.
