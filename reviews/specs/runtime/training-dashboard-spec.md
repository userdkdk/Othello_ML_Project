# Review: specs/runtime/training-dashboard-spec.md

## 권장 수정
- 마지막 비교 결과 조회 API의 부재 표현이 아직 이중 규약으로 남아 있다.
  - 근거: [specs/runtime/training-dashboard-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/runtime/training-dashboard-spec.md:114)~[116행]은 비교 결과가 없을 때 `comparison: null` 또는 `404` 둘 중 아무 방식이나 허용한다.
  - 문제: 이 정도는 구현 유연성보다 클라이언트 분기만 늘리는 모호성이다. 앞서 `GET /api/training/state`는 빈 세션 응답을 `session.status = idle`로 고정한 것과도 톤이 다르다.
  - 권장: `200 + comparison: null` 또는 `404` 중 하나로 고정한다.
