# Review: docs/training/training-ops.md

## 필수 수정
- `resume` 용어가 두 의미로 섞여 있다.
  - 근거: [docs/training/training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:38)에서는 `resume`을 "같은 세션 상태를 이어서 진행"으로 정의한다.
  - 근거: 같은 문서 [39행](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:39)에서는 "새로운 세션 시작과 기존 checkpoint 기반 `resume`"을 구분해야 한다고 적고 있다.
  - 문제: `trainer-loop.md`의 `resume`은 training checkpoint 기반 학습 재개 의미에 더 가깝고, 이 문서의 `paused -> running` 재개와는 다른 개념이다. 이 상태로 두면 이후 API와 task에서 `resume`이 "일시정지 해제"인지 "checkpoint 재개 시작"인지 충돌한다.
  - 권장: `resume_session`과 `resume_from_checkpoint`처럼 용어를 분리하거나, 문서 전체에서 `resume`은 checkpoint 기반 재개로 고정하고 paused 세션 재개는 `continue` 또는 `resume_paused_session` 등으로 별도 명명한다.

## 권장 수정
- runtime 대시보드가 training checkpoint를 "표시"하는 것과 runtime이 training checkpoint를 "소비"하는 것을 더 분리해서 적는 편이 안전하다.
  - 근거: [docs/training/training-ops.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/training/training-ops.md:99)~[108행]에서는 runtime 대시보드가 `latest training checkpoint`와 best training checkpoint들을 기본적으로 보여주는 것으로 적혀 있다.
  - 비교 기준: [docs/runtime/runtime-overview.md](/home/dkdk/dkdk/03.study/06.practice/pr3/docs/runtime/runtime-overview.md:17)~[26행]은 runtime이 기본적으로 inference checkpoint만 소비하고 `latest training checkpoint`는 직접 읽지 않는다고 정의한다.
  - 문제: 현재 표현만 보면 runtime 대시보드가 training checkpoint를 로드해 비교하거나 실행하는 것으로 오해될 수 있다.
  - 권장: training checkpoint는 운영 상태 표시와 resume 정보 노출용, 실제 비교/추론 기본 입력은 inference checkpoint라는 점을 이 문서에서 명시한다.
