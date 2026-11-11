# 현재 구현 상태와 다음 단계

[처음으로](../README.md) · [문서 지도](README.md) · [실험 결과](RESULTS.md)

기준일: 2026-11-11. 공개 소스와 확인한 실행 결과의 범위를 설명한다. 별도 Claude 프로젝트의 연구 결정 원본에는 접근하지 않았으며 이 문서를 연구 결정의 정본으로 취급하지 않는다.

## 지금 할 수 있는 일

| 기능 | 상태 | 확인할 문서 |
|---|---|---|
| 6개 업무 시나리오 W1–W5/N0 | 구현 | [시나리오](WIRED_SCENARIOS.md) |
| SQLite 합성 네트워크 장애·관측·복구 | 구현 | [Backend](BACKEND.md) |
| Operation/Diagnosis 역할 분리, MCP/A2A 통신 | 구현 | [전체 흐름](ARCHITECTURE.md), [프로토콜](PROTOCOLS.md) |
| Runbook 검색과 Memory 초기 조건 | 구현 | [knowledge](../knowledge/README.md), [설정](../configs/README.md) |
| preview/승인/apply/verify/rollback | 구현 | [모듈 계약](MODULE_CONTRACTS.md) |
| CLI·웹 실행·모니터·결과 분석 | 구현 | [Quickstart](QUICKSTART.md), [웹 안내](WEB_CONSOLE.md) |
| 로그·Oracle·seal·read-only 결과 검증 | 구현 | [계측](INSTRUMENTATION.md), [검증](VALIDATION.md) |
| GPT-6 Luna D0 L1/L2/L3 authoring 실행 | 과거 90건 완료 | [결과와 한계](RESULTS.md) |
| GitHub용 설치·폴더 설명·함수 목록·제외 규칙 | 준비 | [GitHub 등록 안내](GITHUB_PREPARATION.md) |

기본 Protection은 `NullGate`이다. 성공률은 장애를 해결하는 D0 기준 동작에 관한 결과이며 민감정보 보호 효과가 아니다.

## 공개 준비에서 보완한 부분

- 각 폴더 README와 전체 구조도를 연결하고 실제 Python 정의를 함수 문서로 정리했다.
- 컴퓨터에 묶인 Python·작업 경로를 실행 설정과 예제 파일로 분리했다.
- 새 사용자는 API Key 없이 doctor·Mock·웹을 시작할 수 있다.
- `knowledge/runbooks/README.md`를 runbook으로 오인하지 않도록 검색·snapshot·웹 초기화 경로를 통일했다.
- 테스트별 작업 폴더와 비용 장부를 분리하고 공개 예제만 있는 새 checkout을 검증한다.
- 개인 설정·DB·원시 결과·빌드 산출물은 보존하면서 Git 후보에서 제외한다.

이 변경 이후 실제 유료 모델 실험을 다시 실행한 것은 아니다. 과거 90건은 당시 고정된 소스의 결과로 유지하고 공개 준비 변경은 [offline 검증](VALIDATION.md)으로 구분한다.

## 아직 하지 않은 일

| 항목 | 필요한 다음 작업 |
|---|---|
| Mininet 실제망 실행 | Linux 환경·topology·probe 조건을 정하고 NetworkBackend 계약을 만족하는 adapter 구현 |
| 정식 D0 pilot | 더 넓은 시나리오 집합, seed·초기 조건·판정 기준 고정 |
| Memory 효과 비교 | 동일 초기 Memory를 사용한 ON/OFF 집단 설계 |
| holdout 일반화 | 개발에 사용하지 않은 평가 사례를 봉인하고 별도 측정 |
| Protection 효과 | necessary-set 및 field ablation, utility와 disclosure의 동시 평가 |
| 원격 CI·배포 | GitHub 등록 후 Actions 실행 확인. 웹 공개 호스팅은 별도 작업 |
| License | 소유자가 권리·이용 조건 확인 후 선택 |

권장 진행 순서는 **공개 가능한 저장소 확정 → 새 환경에서 Mock 재현 → Mininet adapter 설계·conformance → 실제 probe 기반 D0 기준 실험**이다. 합성 backend와 Mininet 결과는 별도 집단으로 관리한다.

