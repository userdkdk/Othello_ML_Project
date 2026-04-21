# `policy_client.py` Review

## 권장 수정

### 1. `device` 인자가 실제 모델 장치 이동을 보장하지 않음
- 기준 문서:
  - `docs/training/cnn-policy.md`
  - `specs/training/cnn-model-spec.md`
  - `tasks/training/implement-cnn-policy-model.md`
- 문제:
  - `PolicyClient.__init__()`는 `device`를 받지만, `_run_model()`에서는 입력 텐서만 `self.device`로 옮긴다.
  - `self.model` 자체를 `to(self.device)`로 이동시키지 않기 때문에, CPU 모델에 `device="cuda"`를 주거나 GPU 모델에 `device="cpu"`를 주면 inference 시 device mismatch가 난다.
- 영향:
  - 현재 구현은 `device` 파라미터가 있는 것처럼 보이지만 실제로는 안전한 장치 전환을 제공하지 않는다.
  - CNN 정책을 런타임이나 학습 환경에 붙일 때 호출자가 모델과 입력의 device를 수동으로 맞춰야 하며, 이 제약이 코드 계약에 드러나지 않는다.
- 근거 위치:
  - `src/training/policy_client.py:27-37`
  - `src/training/policy_client.py:95-99`
- 수정 방향:
  - `PolicyClient` 생성 시 모델을 명시된 device로 이동시키거나,
  - `device` 인자를 제거하고 호출자가 모델 배치를 직접 관리하도록 계약을 단순화해야 한다.

