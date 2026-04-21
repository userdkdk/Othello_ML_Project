# Review: specs/training/training-ops-spec.md

## 필수 수정
- 세션 제어 용어가 `docs/training/training-ops.md`와 불일치한다.
  - 근거: [specs/training/training-ops-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-ops-spec.md:55)에는 `resume_from_checkpoint` 필드가 남아 있고, 오류 계약 [185행](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-ops-spec.md:185)은 `pause`, `resume`, `stop`으로 서술한다.
  - 비교 기준: [docs/training/training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:30)~[40행]은 `resume_session`과 `start_from_checkpoint`를 분리했다.
  - 문제: 상위 문서와 상세 명세의 제어 용어가 어긋나면 API, 상태 머신, task에서 같은 동작을 다른 이름으로 구현하게 된다.
  - 권장: spec도 `resume_session`, `start_from_checkpoint` 기준으로 맞추고, checkpoint 입력 필드는 `start_from_checkpoint_path`처럼 더 명확한 이름으로 정리한다.

## 권장 수정
- checkpoint inventory와 comparison 입력의 기본 사용 대상을 inference checkpoint로 더 명시하는 편이 좋다.
  - 근거: [specs/training/training-ops-spec.md](/home/dkdk/dkdk/03.study/06.practice/pr3/specs/training/training-ops-spec.md:122)~[152행]은 inventory 슬롯과 비교 입력 필드를 정의하지만, training checkpoint는 표시/재개용이고 inference checkpoint가 비교 기본값이라는 점이 약하다.
  - 비교 기준: [docs/training/training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:107)~[110행]은 비교/추론 기본 입력을 inference checkpoint로 두도록 정리했다.
  - 권장: training checkpoint는 관찰 및 재개 후보, inference checkpoint는 비교 기본 입력이라는 계약을 spec에도 반영한다.
