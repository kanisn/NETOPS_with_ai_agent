# 유선 네트워크 Testbed 구현 범위

2026-09-29 유선망 전환에서 정한 실행 범위다. 아래 항목은 합성 backend에서 구현되어 있으며, 현재 완료·미완료 상태는 [STATUS](STATUS.md), 2026-11-11 공개 준비 검증은 [VALIDATION](VALIDATION.md)에 정리한다. 현재 코드와 카탈로그가 웹 콘솔의 시나리오를 결정한다.

1. W1–W5/N0 여섯 시나리오, HOST-001 서비스 대상, host/switch/router/link/flow 상태를 구성한다.
2. NetworkBackend 계약과 실제 MCP/A2A, Operation/Diagnosis 책임 분리를 유지한다.
3. Runbook·Memory 초기 조건, 변경 승인, preview/apply/verify/rollback, 독립 Oracle와 artifact seal을 유지한다.
4. 실행 설정은 사용자 업무 상황을 설명하고, 모니터는 통신 방향·실제 전달 내용을, 결과는 조치와 KPI 변화·업무 해결 목표를 보여준다.
5. 이전 도메인의 웹 문서·Memory·실행 인덱스를 보존용 archive로 분리한 뒤 새 카탈로그를 초기화한다. 이전 결과 파일을 새 실험에 사용하거나 다시 해석하지 않는다.
6. 실제 Mininet adapter는 후속 범위다. 이번에는 Mininet에서 재현할 수 있는 시나리오와 도구 계약을 확정하고 합성 backend로 검증한다.

API 모델과 credentials 설정은 유지한다. 개발 검증은 mock 및 offline transport로 수행하며 유료 모델 품질이나 실망 성능을 검증했다고 주장하지 않는다.

[시나리오 상세](WIRED_SCENARIOS.md) · [Backend](BACKEND.md) · [웹 사용법](WEB_CONSOLE.md) · [검증 기록](VALIDATION.md)
